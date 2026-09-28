import http.client
import json
import shutil
import subprocess
import time

try:
    import requests
except ImportError:
    requests = None

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)


def _network_result(error, latency_ms, attempts=1):
    return {
        "ok": False,
        "status": None,
        "body": "",
        "error_kind": "network",
        "error": error,
        "latency_ms": latency_ms,
        "attempts": attempts,
    }


def _curl_once(method, url, headers, body, timeout):
    cmd = ["curl", "-sS", "-X", method, "-m", str(timeout), "-w", "\n%{http_code}"]
    for name, value in (headers or {}).items():
        cmd += ["-H", f"{name}: {value}"]
    if body is not None:
        cmd += ["--data-binary", body]
    cmd.append(url)
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
    except subprocess.TimeoutExpired:
        return _network_result("curl timeout", int((time.monotonic() - started) * 1000))
    except (OSError, http.client.HTTPException, ValueError) as exc:
        return _network_result(f"{type(exc).__name__}: {exc}", 0)
    latency = int((time.monotonic() - started) * 1000)
    if proc.returncode != 0:
        err = (proc.stderr or "").strip() or f"curl exit {proc.returncode}"
        return _network_result(err, latency)
    out = proc.stdout or ""
    head, _, tail = out.rpartition("\n")
    tail = tail.strip()
    if tail.isdigit() and len(tail) == 3:
        return {
            "ok": True,
            "status": int(tail),
            "body": head,
            "error_kind": None,
            "error": None,
            "latency_ms": latency,
            "attempts": 1,
        }
    return _network_result("curl: статус в ответе не найден", latency)


def _requests_once(method, url, headers, body, timeout):
    if requests is None:
        return _network_result("requests недоступен", 0)
    headers = dict(headers or {})
    headers.setdefault("User-Agent", BROWSER_UA)
    started = time.monotonic()
    try:
        resp = requests.request(method, url, headers=headers, data=body, timeout=timeout)
    except http.client.HTTPException as exc:
        return _network_result(f"HTTPException: {exc}", int((time.monotonic() - started) * 1000))
    except (requests.exceptions.RequestException, OSError, ValueError) as exc:
        return _network_result(f"{type(exc).__name__}: {exc}", int((time.monotonic() - started) * 1000))
    return {
        "ok": True,
        "status": resp.status_code,
        "body": resp.text or "",
        "error_kind": None,
        "error": None,
        "latency_ms": int((time.monotonic() - started) * 1000),
        "attempts": 1,
    }


def single_request(method, url, headers=None, body=None, timeout=15):
    headers = dict(headers or {})
    headers.setdefault("Accept", "application/json")
    try:
        if shutil.which("curl"):
            return _curl_once(method, url, headers, body, timeout)
        if requests is not None:
            return _requests_once(method, url, headers, body, timeout)
        return _network_result("нет HTTP-клиента (curl и requests недоступны)", 0)
    except (http.client.HTTPException, OSError, ValueError, subprocess.SubprocessError) as exc:
        return _network_result(f"{type(exc).__name__}: {exc}", 0)


def request(method, url, *, headers=None, body=None, json_body=None,
            timeout=15, retries=2, pause=20.0):
    payload = body
    headers = dict(headers or {})
    if json_body is not None:
        payload = json.dumps(json_body, ensure_ascii=False)
        headers.setdefault("Content-Type", "application/json")
    attempts = 0
    while True:
        attempts += 1
        res = single_request(method, url, headers, payload, timeout)
        res["attempts"] = attempts
        if res.get("status") == 429 and attempts <= retries:
            if pause > 0:
                time.sleep(pause)
            continue
        return res


def is_cloudflare_fingerprint(body):
    return bool(body) and "error code: 1010" in body
