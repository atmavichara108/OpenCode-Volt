#!/usr/bin/env python3
"""termproxy — лёгкий терминальный мост pty→WebSocket (stdlib, без зависимостей).

Заменяет ttyd/gotty: поднимает pty с оболочкой, раздаёт HTML-обёртку с
xterm.js (локальный vendor) и транслирует ввод/вывод через WebSocket.

Архитектура: raw socket server — обходит BaseHTTPRequestHandler, чтобы
WebSocket upgrade работал без блокировки HTTP-потока.

Команды:
  serve --port PORT --cmd CMD [--cwd DIR]
      foreground-сервер (вызывается из pipboy.py /action term-open)
  status --port PORT   JSON: жив ли

Контракт: GET / → HTML-терминал; GET /ws → WebSocket pty-мост.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pty
import select
import signal
import socket
import struct
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")

DEFAULT_SHELL = os.environ.get("SHELL") or "/bin/bash"


class WSConn:
    """Минимальный WebSocket (RFC6455): handshake + text frames."""

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buf = b""

    def recv_frames(self) -> list[tuple[int, bytes]]:
        try:
            self.buf += self.sock.recv(65536)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError:
            return [(0x8, b"")]
        frames = []
        while len(self.buf) >= 2:
            b1, b2 = self.buf[0], self.buf[1]
            opcode = b1 & 0x0F
            masked = b2 & 0x80
            length = b2 & 0x7F
            off = 2
            if length == 126:
                if len(self.buf) < 4:
                    break
                length = struct.unpack(">H", self.buf[2:4])[0]
                off = 4
            elif length == 127:
                if len(self.buf) < 10:
                    break
                length = struct.unpack(">Q", self.buf[2:10])[0]
                off = 10
            mask = None
            if masked:
                if len(self.buf) < off + 4:
                    break
                mask = self.buf[off:off + 4]
                off += 4
            if len(self.buf) < off + length:
                break
            payload = self.buf[off:off + length]
            self.buf = self.buf[off + length:]
            if masked and mask is not None:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            frames.append((opcode, payload))
        return frames

    def send_text(self, data: str) -> None:
        raw = data.encode("utf-8")
        header = bytes([0x81])
        n = len(raw)
        if n < 126:
            header += bytes([n])
        elif n < 65536:
            header += bytes([126]) + struct.pack(">H", n)
        else:
            header += bytes([127]) + struct.pack(">Q", n)
        try:
            self.sock.sendall(header + raw)
        except OSError:
            pass

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class TermSession:
    """Одна pty-сессия на WS-клиента."""

    def __init__(self, cmd: str, cwd: str):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.chdir(cwd or HERE)
            os.environ["TERM"] = "xterm-256color"
            os.execvp("/bin/sh", ["/bin/sh", "-c", cmd])
        self.dead = False

    def read_some(self, timeout=0.1) -> bytes:
        r, _, _ = select.select([self.fd], [], [], timeout)
        if not r:
            return b""
        try:
            return os.read(self.fd, 65536)
        except OSError:
            self.dead = True
            return b""

    def write(self, data: bytes) -> None:
        try:
            os.write(self.fd, data)
        except OSError:
            self.dead = True

    def close(self) -> None:
        try:
            os.kill(self.pid, signal.SIGHUP)
        except OSError:
            pass


def ws_handshake(sock: socket.socket, pre_read: bytes = b"") -> bool:
    """Perform WebSocket upgrade handshake on raw socket."""
    data = pre_read
    sock.settimeout(5)
    try:
        while b"\r\n\r\n" not in data:
            chunk = sock.recv(4096)
            if not chunk:
                return False
            data += chunk
    except OSError:
        return False
    lines = data.decode("latin-1").split("\r\n")
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    key = headers.get("sec-websocket-key", "")
    if not key:
        return False
    accept = base64.b64encode(hashlib.sha1(
        (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    resp = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
    )
    try:
        sock.sendall(resp.encode())
        return True
    except OSError:
        return False


def handle_ws(sock: socket.socket, cmd: str, cwd: str, pre_read: bytes = b"") -> None:
    """WebSocket handler: pty ↔ ws bidirectional bridge."""
    if not ws_handshake(sock, pre_read):
        sock.close()
        return
    ws = WSConn(sock)
    sess = TermSession(cmd, cwd)
    sock.setblocking(False)
    stop = threading.Event()

    def writer():
        while not stop.is_set() and not sess.dead:
            data = sess.read_some(0.1)
            if data:
                try:
                    ws.send_text(data.decode("utf-8", "replace"))
                except OSError:
                    break

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    while not sess.dead:
        frames = ws.recv_frames()
        for op, payload in frames:
            if op == 0x8:
                stop.set()
                sess.close()
                ws.close()
                return
            if op in (0x1, 0x2):
                sess.write(payload)
        if not frames:
            time.sleep(0.02)
        if sess.dead:
            break
    stop.set()
    sess.close()
    ws.close()


def html_page(port: int) -> bytes:
    with open(os.path.join(VENDOR, "xterm.css"), "rb") as f:
        css = f.read().decode()
    with open(os.path.join(VENDOR, "xterm.js"), "rb") as f:
        xtermjs = f.read().decode()
    with open(os.path.join(VENDOR, "xterm-fit.js"), "rb") as f:
        fitjs = f.read().decode()
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}
body{{margin:0;background:#0a100d}}
#term{{position:fixed;inset:8px}}</style></head>
<body><div id="term"></div>
<script>{xtermjs}</script><script>{fitjs}</script>
<script>
const term = new Terminal({{cursorBlink:true, fontFamily:'JetBrains Mono, monospace', fontSize:13,
  theme:{{background:'#0a100d', foreground:'#e8f2ea', cursor:'#4ade80', green:'#4ade80'}}}});
const fit = new FitAddon.FitAddon();
term.loadAddon(fit);
term.open(document.getElementById('term'));
fit.fit();
window.addEventListener('resize', () => fit.fit());
const ws = new WebSocket('ws://127.0.0.1:{port}/ws');
ws.onopen = () => term.write('\\x1b[32m[termproxy] connected\\x1b[0m\\r\\n');
ws.onmessage = e => term.write(e.data);
term.onData(d => ws.readyState === 1 && ws.send(d));
</script></body></html>"""
    return page.encode("utf-8")


def http_response(code: int, content_type: str, body: bytes) -> bytes:
    """Build a minimal HTTP/1.1 response."""
    reasons = {200: "OK", 404: "Not Found"}
    reason = reasons.get(code, "OK")
    header = (
        f"HTTP/1.1 {code} {reason}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return header.encode("latin-1") + body


def parse_request_line(data: bytes) -> tuple[str, str, str]:
    """Parse 'GET /path HTTP/1.1' → (method, path, version)."""
    first_line = data.split(b"\r\n", 1)[0].decode("latin-1")
    parts = first_line.split(" ", 2)
    method = parts[0] if len(parts) > 0 else ""
    path = parts[1] if len(parts) > 1 else "/"
    version = parts[2] if len(parts) > 2 else "HTTP/1.1"
    return method, path, version


def serve(port: int, cmd: str, cwd: str) -> None:
    """Raw socket server — dispatches HTTP vs WebSocket per connection."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(32)
    srv.settimeout(1.0)
    sys.stderr.write(f"termproxy: listening on http://127.0.0.1:{port}/ (cmd={cmd})\n")
    try:
        while True:
            try:
                client, addr = srv.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
            # Read first bytes to determine request type
            client.settimeout(3)
            try:
                first = client.recv(4096)
            except (OSError, socket.timeout):
                client.close()
                continue
            if not first:
                client.close()
                continue
            method, path, _ = parse_request_line(first)
            if path == "/ws" and method == "GET":
                # WebSocket: spawn handler in thread (non-blocking)
                threading.Thread(
                    target=handle_ws,
                    args=(client, cmd, cwd, first),
                    daemon=True,
                ).start()
            elif method in ("GET", "HEAD"):
                # HTTP: serve inline (fast, non-blocking)
                try:
                    if path == "/" or path == "/index.html":
                        resp = http_response(200, "text/html; charset=utf-8", html_page(port))
                    elif path == "/healthz":
                        resp = http_response(200, "application/json", b'{"termproxy": true}')
                    else:
                        resp = http_response(404, "text/plain", b"404")
                    client.sendall(resp)
                except OSError:
                    pass
                finally:
                    client.close()
            else:
                client.close()
    finally:
        srv.close()


def alive(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=0.5) as r:
            return r.status == 200
    except OSError:
        return False


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("serve")
    sp.add_argument("--port", type=int, default=8200)
    sp.add_argument("--cmd", default=DEFAULT_SHELL)
    sp.add_argument("--cwd", default=HERE)
    st = sub.add_parser("status")
    st.add_argument("--port", type=int, default=8200)
    args = p.parse_args()
    if args.cmd == "status":
        print(json.dumps({"alive": alive(args.port)}))
        return 0
    serve(args.port, args.cmd, args.cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
