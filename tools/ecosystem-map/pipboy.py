#!/usr/bin/env python3
"""Pip-Boy on-demand host — поднять/погасить локальный HTTP-хост Pip-Boy.

Универсальный контракт: Pip-Boy всегда живёт на
  http://127.0.0.1:8123/        (PIPBOY_PORT переопределяет)
— один и тот же URL работает во встроенном браузере M Code GUI, в будущем
браузере TUI и в любом внешнем браузере. Зависимостей нет: только stdlib
python3, only-static, bind 127.0.0.1 (PIPBOY_HOST переопределяет), read-only
(только GET/HEAD; остальное -> 501).

Команды:
  up        поднять в фоне (idempotent: уже запущен -> сообщить и выйти 0)
  down      погасить (SIGTERM, при необходимости SIGKILL) и убрать pidfile
  restart   down + up
  status    статус: pid, порт, число запросов, последний запрос
  open      up + открыть в браузере ($PIPBOY_OPEN > $BROWSER > xdg-open)
  serve     foreground-режим (ручной запуск/systemd)

Авто-гашение: если N секунд нет ни одного запроса (любым клиентом),
сервер гасит сам себя. N = PIPBOY_IDLE сек (по умолчанию 1800 = 30 мин,
0 = никогда). AUTO-polling Pip-Boy (раз в 60 с) считается активностью:
открытая вкладка с AUTO держит сервер живым.

Файлы состояния: /tmp/mcode/pipboy-<port>.pid и .log (вне git).
Перед открытием обнови snapshot: python3 tools/ecosystem-map/observer.py

Exit codes: 0 = ок; 1 = не удалось; 2 = неверное использование.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVE_DIR = os.path.join(VAULT_ROOT, "tools", "ecosystem-map")

DEFAULT_PORT = 8123
DEFAULT_IDLE = 1800
DEFAULT_HOST = "127.0.0.1"

STATE = {"last": time.time(), "started": time.time(), "n_req": 0}
SERVE_INFO = {"port": DEFAULT_PORT, "idle_timeout": DEFAULT_IDLE}

# --- SSE / live (T-128/ECO-018): file-watcher → event-log ---
SSE_STATE = {"seq": 0, "last_digest": None}


def input_digest() -> str:
    """sha256 registry.json + generated/snapshot.json; изменение = новый event."""
    import hashlib

    h = hashlib.sha256()
    for name in ("registry.json", "generated/snapshot.json"):
        p = os.path.join(SERVE_DIR, name)
        if os.path.exists(p):
            with open(p, "rb") as fh:
                h.update(fh.read())
        else:
            h.update(b"<missing>")
    return h.hexdigest()


def watch_files(interval: float = 2.0) -> None:
    """File-watcher: при изменении входов инкрементит SSE_STATE['seq'].

    Частный случай будущего живой observer: событие `file.watcher.updated`
    рождается по факту изменения digest, а не wall-clock. Детерминизм не
    нарушается (событие не подделывает данные, только сигналит фронту).
    """
    SSE_STATE["last_digest"] = input_digest()
    while True:
        time.sleep(interval)
        d = input_digest()
        if d != SSE_STATE["last_digest"]:
            SSE_STATE["last_digest"] = d
            SSE_STATE["seq"] += 1


def pidfile_path(port: int) -> str:
    return f"/tmp/mcode/pipboy-{port}.pid"


def log_path(port: int) -> str:
    return f"/tmp/mcode/pipboy-{port}.log"


class Handler(SimpleHTTPRequestHandler):
    server_version = "PipBoyHost/1"

    def end_headers(self) -> None:
        # статические файлы SimpleHTTPRequestHandler отдаёт без Cache-Control,
        # из-за чего браузер кеширует устаревшие JS/HTML после обновления.
        # Форсируем no-store на всём, кроме SSE (у SSE свой Cache-Control).
        if not getattr(self, "_sse_written", False):
            if not self.headers.get("Cache-Control"):
                self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802
        STATE["last"] = time.time()
        STATE["n_req"] += 1
        if self.path.split("?")[0] == "/event":
            self._handle_sse()
            return
        if self.path.split("?")[0] == "/healthz":
            now = time.time()
            body = json.dumps({
                "pipboy": True,
                "pid": os.getpid(),
                "port": SERVE_INFO["port"],
                "idle_timeout_s": SERVE_INFO["idle_timeout"],
                "uptime_s": round(now - STATE["started"]),
                "requests_served": STATE["n_req"],
                "last_request": time.strftime("%H:%M:%S", time.localtime(STATE["last"])),
                "serve_dir": SERVE_DIR,
            }, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?")[0] == "/action":
            self._handle_action()
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        STATE["last"] = time.time()
        super().do_HEAD()

    def _handle_sse(self) -> None:
        """GET /event — Server-Sent Events: толкает событие при изменении входов.

        Формат: `event: <name>\ndata: {json}\n\n`, heartbeat `:ping` каждые 2 с
        (держит соединение и обновляет idle-активность). Клиент — EventSource.
        """
        self._sse_written = True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        w = self.wfile
        last = SSE_STATE["seq"]
        try:
            while True:
                # изменение digested входов → событие
                if SSE_STATE["seq"] != last:
                    last = SSE_STATE["seq"]
                    payload = json.dumps({
                        "event": "file.watcher.updated",
                        "seq": last,
                        "digest": SSE_STATE["last_digest"][:12],
                        "ts": time.time(),
                    }, ensure_ascii=False)
                    w.write(f"event: file.watcher.updated\ndata: {payload}\n\n".encode("utf-8"))
                    w.flush()
                else:
                    w.write(b":ping\n\n")
                    w.flush()
                STATE["last"] = time.time()  # SSE-подключение = активность (idle)
                time.sleep(2)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def _handle_action(self) -> None:
        """GET /action?<query> — whitelist-механизм серверных действий.

        Безопасность: только GET (нет side-effect от перезагрузки страницы), только
        whitelist операций; реальное исполнение — в actions.py.
        """
        STATE["last"] = time.time()
        import urllib.parse

        q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        op = (q.get("op") or [""])[0]
        ALLOWED = {"workspace-open", "workspace-status", "link-open", "link-resolve", "capture-scan", "term-open",
                   "term-status", "term-close", "query", "blockers", "next", "dependencies", "notify",
                   "proposals", "apply"}
        body = None
        code = 200
        if op not in ALLOWED:
            code = 400
            body = {"ok": False, "error": f"action не разрешён: {op}"}
        else:
            ACTIONS = os.path.join(SERVE_DIR, "actions.py")
            if not os.path.exists(ACTIONS):
                code = 500
                body = {"ok": False, "error": "actions.py не найден"}
            else:
                argv = [python_bin(), str(ACTIONS), op]
                positional = {
                    "workspace-open": ["project"],
                    "workspace-status": ["project"],
                    "link-open": ["target"],
                    "link-resolve": ["target"],
                    "capture-scan": [],
                    "term-open": ["project"],
                    "term-status": ["project"],
                    "term-close": ["project"],
                }.get(op, [])
                for key in positional:
                    argv.append((q.get(key) or [""])[0])
                if op == "link-open" and q.get("mode"):
                    argv.append("--mode")
                    argv.append(q["mode"][0])
                if op == "workspace-open" and "no_term" in q:
                    argv.append("--no-term")
                if op == "capture-scan" and "run" in q:
                    argv.append("--run")
                if op == "capture-scan" and q.get("limit"):
                    argv.append("--limit")
                    argv.append(q["limit"][0])
                if op == "term-open" and q.get("port"):
                    argv.append("--port")
                    argv.append(q["port"][0])
                # flag-операции (query/blockers/next/dependencies/notify/apply).
                # NB: "project" и "target" НЕ в общем списке — это позиционные
                # аргументы у workspace-open/status/term-open и link-open/link-resolve
                # соответственно; для query передаём project отдельно, для apply —
                # target. "card" use only in dependencies/apply (flag-операции).
                for flag in ("q", "facet", "limit", "card", "message", "topic", "priority"):
                    if q.get(flag):
                        argv.append(f"--{flag}")
                        argv.append(q[flag][0])
                if op == "apply" and q.get("target"):
                    argv.append("--target")
                    argv.append(q["target"][0])
                if op == "query" and q.get("project"):
                    argv.append("--project")
                    argv.append(q["project"][0])
                r = subprocess.run(argv, capture_output=True, text=True, timeout=30)
                try:
                    body = json.loads(r.stdout.strip() or "{}")
                except json.JSONDecodeError:
                    body = {"ok": False, "error": "actions: не-JSON вывод", "stderr": r.stderr[:200]}
                if r.returncode != 0 and body.get("ok"):
                    body = {"ok": False, "error": body.get("error") or f"exit {r.returncode}"}
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


class PipBoyServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    idle_timeout: int = DEFAULT_IDLE


def watch_idle(srv: PipBoyServer, idle_s: int) -> None:
    """Гасить сервер после idle_s секунд без запросов (idle_s <= 0 -> никогда).

    Graceful shutdown через srv.shutdown(): serve_forever() возвращается,
    управление доходит до finally в start_foreground, pidfile убирается чисто.
    """
    if idle_s <= 0:
        return
    while True:
        time.sleep(min(5, max(1, idle_s // 6)))
        if time.time() - STATE["last"] > idle_s:
            sys.stderr.write(
                "pipboy: %ds без запросов -> авто-гашение (поднять снова: pipboy.py up)\n" % idle_s
            )
            srv.shutdown()
            return


def http_alive(port: int, host: str = DEFAULT_HOST, timeout: float = 0.4) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/healthz", timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data if data.get("pipboy") else None
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return None


def read_pid(port: int) -> int | None:
    try:
        with open(pidfile_path(port)) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def python_bin() -> str:
    """Надёжный интерпретатор для дочернего процесса.

    sys.executable под M Code GUI указывает на AppImage-бинарь самого
    приложения — тогда берём PIPBOY_PYTHON или python3 из PATH.
    """
    exe = os.environ.get("PIPBOY_PYTHON") or sys.executable or ""
    if os.path.basename(exe).startswith("python") and os.path.isfile(exe):
        return exe
    # любой явный PIPBOY_PYTHON с полным путём принимается как есть
    if os.environ.get("PIPBOY_PYTHON") and os.path.isfile(os.environ["PIPBOY_PYTHON"]):
        return os.environ["PIPBOY_PYTHON"]
    found = shutil.which("python3") or shutil.which("python")
    if found:
        return found
    print("pipboy: не найден python3 (задай PIPBOY_PYTHON)", file=sys.stderr)
    sys.exit(2)


def spawn_daemon(port: int, idle: int, host: str) -> None:
    with open(log_path(port), "ab") as log:
        subprocess.Popen(
            [python_bin(), os.path.abspath(__file__),
             "serve", "--port", str(port), "--idle", str(idle), "--host", host],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            start_new_session=True, close_fds=True,
        ).pid


def start_foreground(port: int, idle: int, host: str) -> int:
    os.makedirs(os.path.dirname(pidfile_path(port)), exist_ok=True)
    try:
        srv = PipBoyServer((host, port), partial(Handler, directory=SERVE_DIR))
    except OSError as e:
        print(f"pipboy: порт {port} занят или недоступен: {e}", file=sys.stderr)
        return 1
    srv.idle_timeout = idle
    SERVE_INFO["port"] = port
    SERVE_INFO["idle_timeout"] = idle
    with open(pidfile_path(port), "w") as f:
        f.write(str(os.getpid()))
    threading.Thread(target=watch_idle, args=(srv, idle), daemon=True).start()
    threading.Thread(target=watch_files, args=(), daemon=True).start()
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    sys.stderr.write(
        f"pipboy: serving {SERVE_DIR} on http://{host}:{port}/ "
        f"(pid {os.getpid()}, idle {idle}s, {stamp})\n"
    )
    try:
        srv.serve_forever()
    finally:
        try:
            os.remove(pidfile_path(port))
        except OSError:
            pass
    return 0


def cmd_up(args) -> int:
    alive = http_alive(args.port, args.host)
    if alive:
        print(f"pipboy: уже запущен (pid {alive['pid']}) -> http://{args.host}:{args.port}/")
        return 0
    stale = read_pid(args.port)
    if stale and pid_alive(stale):
        print(f"pipboy: pid {stale} жив, но /healthz не отвечает; погаси вручную: kill {stale}",
              file=sys.stderr)
        return 1
    try:
        os.remove(pidfile_path(args.port))
    except OSError:
        pass
    spawn_daemon(args.port, args.idle, args.host)
    for _ in range(40):
        time.sleep(0.1)
        alive = http_alive(args.port, args.host)
        if alive:
            break
    if not alive:
        print(f"pipboy: не удалось поднять порт {args.port}; лог: {log_path(args.port)}",
              file=sys.stderr)
        return 1
    print(f"pipboy: поднят (pid {alive['pid']}) -> http://{args.host}:{args.port}/")
    print(f"pipboy: авто-гашение {args.idle}s простоя · лог {log_path(args.port)}")
    return 0


def cmd_down(args) -> int:
    alive = http_alive(args.port, args.host)
    pid = alive["pid"] if alive else read_pid(args.port)
    if not pid or not pid_alive(pid):
        try:
            os.remove(pidfile_path(args.port))
        except OSError:
            pass
        print(f"pipboy: на порту {args.port} ничего не запущено")
        return 0
    os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        time.sleep(0.1)
        if not pid_alive(pid):
            break
    else:
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.2)
    try:
        os.remove(pidfile_path(args.port))
    except OSError:
        pass
    print(f"pipboy: погашен (pid {pid}, порт {args.port})")
    return 0


def cmd_status(args) -> int:
    alive = http_alive(args.port, args.host)
    if alive:
        print(f"RUNNING pid={alive['pid']} url=http://{args.host}:{args.port}/ "
              f"idle_timeout={alive['idle_timeout_s']}s requests={alive['requests_served']} "
              f"last={alive['last_request']}")
        return 0
    print(f"DOWN · порт {args.port} свободен · поднять: "
          f"python3 tools/ecosystem-map/pipboy.py up")
    return 0


def cmd_open(args) -> int:
    if cmd_up(args) != 0:
        return 1
    url = f"http://{args.host}:{args.port}/" + (f"#{args.view}" if args.view else "")
    opener = os.environ.get("PIPBOY_OPEN") or os.environ.get("BROWSER") or shutil.which("xdg-open")
    if opener:
        try:
            subprocess.Popen([opener, url])
            print(f"pipboy: открыл {url} (через {os.path.basename(opener)})")
            return 0
        except OSError:
            pass
    print(f"pipboy: открывашка не найдена ($PIPBOY_OPEN/$BROWSER/xdg-open) — URL: {url}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Pip-Boy on-demand host (up/down/status/open)")
    sub = p.add_subparsers(dest="cmd", required=True)
    def common(sp) -> None:
        sp.add_argument("--port", type=int, default=int(os.environ.get("PIPBOY_PORT", DEFAULT_PORT)))
        sp.add_argument("--idle", type=int, default=int(os.environ.get("PIPBOY_IDLE", DEFAULT_IDLE)),
                        help="авто-гашение после N сек без запросов (0 = никогда)")
        sp.add_argument("--host", default=os.environ.get("PIPBOY_HOST", DEFAULT_HOST))
    for name in ("up", "down", "restart", "status", "open", "serve"):
        common(sub.add_parser(name))
    sub.choices["open"].add_argument("--view", default="", help="view-хэш: next/deps/kanban/...")
    args = p.parse_args()
    if args.cmd == "up":
        return cmd_up(args)
    if args.cmd == "down":
        return cmd_down(args)
    if args.cmd == "restart":
        rc = cmd_down(args)
        return cmd_up(args) if rc == 0 else rc
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "open":
        return cmd_open(args)
    if args.cmd == "serve":
        return start_foreground(args.port, args.idle, args.host)
    return 2


if __name__ == "__main__":
    sys.exit(main())
