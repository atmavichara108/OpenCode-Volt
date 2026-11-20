#!/usr/bin/env python3
"""watch — сторож new-api ротатора (алиасы шлюза + классы ошибок).

Мандат (слово владельца, basis: quoted, 2026-11-20): «ставить ротатор по
умолчанию и отслеживать его работу, ловить все ошибки, обрабатывать и
модернизировать ротатор и в то же время обеспечивать его бесперебойную работу».

Что делает (read-only по шлюзу + append в health-лог):
  1. SMOKE алиасов через живой шлюз: free-code, free-general и free-general с
     картинкой (контракт контента после слияния vision+general). Фиксирует
     HTTP-код, латенси и апстрим-модель, которая фактически ответила.
  2. СКАН лога шлюза с последнего курсора — классификация ошибок по классам:
       geo_block      — 451 (гео-блок edge NVIDIA; лечится прокси в юните)
       quota_or_rate  — 429 (суточная квота провайдера / reate-limit)
       content_contract — 400 («does not support image input» и т.п.: запрос
                          пришёл на алиас, которому контент не по контракту)
       key_resolution — no_key (ключ провайдера не резолвится; флак v2-export)
       channel_error  — прочие ошибки канала с указанием апстрима
       auth           — Invalid token / record not found
  3. HEALTH-строка в provider-health.jsonl (source=watch): статус шлюза как
     провайдера newapi — ACTIVE (все smoke 200), DEGRADED (частично), ERROR.

Курсор лога: control-plane/telemetry/watch-state.json (файл лога + смещение).
Смена файла лога (ротация) сбрасывает курсор. Секреты (ключ шлюза) не печатаются.

Контракт вывода: одна строка JSON {"ok": true, ...}. Exit: 0 все smoke 200 |
1 есть FAIL | 2 ошибка ввода | 3 фатальная.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
VAULT_ROOT = TOOL_DIR.parents[1]
HEALTH_LOG = VAULT_ROOT / "control-plane" / "telemetry" / "provider-health.jsonl"
STATE_PATH = VAULT_ROOT / "control-plane" / "telemetry" / "watch-state.json"
GATEWAY_DB = os.path.expanduser("~/.local/share/newapi/one-api.db")
GATEWAY_LOG_GLOB = os.path.expanduser("~/.local/share/newapi/logs/oneapi-*.log")
GATEWAY_URL = "http://127.0.0.1:3000/v1/chat/completions"

ALIASES = ("free-code", "free-general")
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAE"
    "hQGAhKmMIQAAAABJRU5ErkJggg=="
)


def out(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gateway_token() -> str | None:
    """Ключ шлюза — только чтение (mode=ro). Значение не печатается."""
    try:
        con = sqlite3.connect(f"file:{GATEWAY_DB}?mode=ro", uri=True)
        try:
            row = con.execute("select key from tokens where id=1").fetchone()
        finally:
            con.close()
        return row[0] if row and row[0] else None
    except sqlite3.Error:
        return None


def smoke(token: str, alias: str, with_image: bool, timeout: float) -> dict:
    content = [{"type": "text", "text": "ping, answer one word"}]
    if with_image:
        content.append({"type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{TINY_PNG_B64}"}})
    body = json.dumps({"model": alias, "max_tokens": 12,
                       "messages": [{"role": "user", "content": content}]}).encode()
    req = urllib.request.Request(GATEWAY_URL, data=body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8", "replace"))
            model = payload.get("model") or ""
            return {"alias": alias, "with_image": with_image, "ok": True,
                    "status": r.status, "latency_ms": int((time.time() - t0) * 1000),
                    "upstream": model}
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8", "replace"))
            msg = (msg.get("error") or {}).get("message", "")
        except Exception:
            msg = ""
        return {"alias": alias, "with_image": with_image, "ok": False,
                "status": e.code, "latency_ms": int((time.time() - t0) * 1000),
                "error": str(msg)[:200]}
    except Exception as e:
        return {"alias": alias, "with_image": with_image, "ok": False,
                "status": None, "latency_ms": int((time.time() - t0) * 1000),
                "error": f"{type(e).__name__}: {e}"[:200]}


def newest_log() -> Path | None:
    log_dir = Path(GATEWAY_LOG_GLOB).parent
    paths = sorted(log_dir.glob("oneapi-*.log"))
    return paths[-1] if paths else None


def classify(line: str) -> str | None:
    low = line.lower()
    if "451" in line and ("bad response status code" in low or "status code: 451" in low):
        return "geo_block"
    if "no_key" in low:
        return "key_resolution"
    if "does not support image input" in low or "multimodal" in low:
        return "content_contract"
    if "429" in line and ("status code" in low or "rate limit" in low):
        return "quota_or_rate"
    if "invalid token" in low or "record not found" in low:
        return "auth"
    if "channel error" in low or "bad response status code" in low:
        return "channel_error"
    if "relay error" in low:
        return "channel_error"
    return None


def scan_log(state: dict) -> tuple[dict, str | None]:
    """Читает лог с курсора, классифицирует строки, возвращает (classes, log_name)."""
    log = newest_log()
    if not log:
        return {}, state.get("log_file")
    offset = 0
    if state.get("log_file") == str(log):
        offset = int(state.get("offset") or 0)
    try:
        size = log.stat().st_size
        if offset > size:  # лог усекли/сменили — начинаем сначала
            offset = 0
        with open(log, "rb") as fh:
            fh.seek(offset)
            chunk = fh.read()
            new_offset = offset + len(chunk)
    except OSError:
        return {}, str(log)
    classes: dict[str, int] = {}
    samples: dict[str, str] = {}
    for raw in chunk.decode("utf-8", "replace").splitlines():
        cls = classify(raw)
        if not cls:
            continue
        classes[cls] = classes.get(cls, 0) + 1
        samples.setdefault(cls, raw[:220])
    state["log_file"] = str(log)
    state["offset"] = new_offset
    state["scanned_at"] = now_iso()
    return {"classes": classes, "samples": samples}, str(log)


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> bool:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        return True
    except OSError:
        return False


def append_health(rec: dict) -> bool:
    try:
        HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def refresh_live_catalog(timeout: float) -> dict:
    """Обновляет живой каталог моделей (полные списки по ключу провайдера).

    Источник 2 для пин-гейта УАС (дыра BF-20261120-01: каталог OpenCode считает
    мёртвый id живым). Гоняется probe.py подпроцессом — один таймер сторожа
    покрывает оба источника: health алиасов + health моделей.
    """
    probe = TOOL_DIR / "probe.py"
    out_path = VAULT_ROOT / "control-plane" / "live-model-catalog.json"
    cmd = [sys.executable, str(probe), "--live-catalog", str(out_path),
           "--timeout", str(int(timeout)), "--quiet"]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout * 30)
        return {"ok": proc.returncode in (0, 1), "path": str(out_path),
                "probe_exit": proc.returncode}
    except Exception as exc:
        return {"ok": False, "path": str(out_path), "error": f"{type(exc).__name__}: {exc}"}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="watch", description="сторож new-api ротатора")
    p.add_argument("--timeout", type=float, default=120.0, help="таймаут одного smoke")
    p.add_argument("--no-image", action="store_true", help="без smoke с картинкой")
    p.add_argument("--no-log-scan", action="store_true", help="без скана лога шлюза")
    p.add_argument("--no-catalog", action="store_true",
                   help="не обновлять живой каталог моделей (источник 2 пин-гейта)")
    p.add_argument("--max-latency-ms", type=int, default=60000,
                   help="порог латентности smoke: 200, но медленнее порога — "
                        "DEGRADED с предупреждением slow_alias (0 = выключено)")
    p.add_argument("--quiet", action="store_true", help="только итоговая строка JSON")
    args = p.parse_args(argv)

    token = gateway_token()
    if not token:
        out({"ok": False, "error": "нет ключа шлюза (tokens id=1 в БД new-api)"})
        return 3

    plan = [(a, False) for a in ALIASES]
    if not args.no_image:
        plan.append(("free-general", True))

    smokes = []
    for alias, with_image in plan:
        smokes.append(smoke(token, alias, with_image, args.timeout))

    ok_count = sum(1 for s in smokes if s["ok"])
    if ok_count == len(smokes):
        status = "ACTIVE"
    elif ok_count:
        status = "DEGRADED"
    else:
        status = "ERROR"

    catalog = None
    if not args.no_catalog:
        catalog = refresh_live_catalog(args.timeout)

    errors: dict[str, int] = {}
    log_name = None
    if not args.no_log_scan:
        state = load_state()
        scan, log_name = scan_log(state)
        save_state(state)
        errors = (scan or {}).get("classes") or {}

    warnings = []
    for cls, cnt in errors.items():
        if cls in ("geo_block", "key_resolution", "content_contract") and cnt:
            warnings.append(f"{cls}:{cnt}")
    for s in smokes:
        if not s["ok"]:
            warnings.append(f"smoke_fail:{s['alias']}{'+img' if s['with_image'] else ''}")
    # Латентность как часть здоровья: 200 за 5 минут — не ACTIVE для
    # исполнителя (флот ждёт ответа). Живой класс 20.11: AMD ответил 200 за
    # 320с; при одном таймауте smoke ещё и падал — порог ловит и «медленный
    # успех», и понижает статус до DEGRADED с предупреждением slow_alias.
    if args.max_latency_ms > 0 and status == "ACTIVE":
        slow = [s for s in smokes
                if s["ok"] and (s.get("latency_ms") or 0) > args.max_latency_ms]
        if slow:
            status = "DEGRADED"
            for s in slow:
                warnings.append(
                    f"slow_alias:{s['alias']}{'+img' if s['with_image'] else ''}"
                    f":{s.get('latency_ms')}ms")

    rec = {
        "ts": now_iso(),
        "provider_id": "newapi",
        "status": status,
        "models_count": len(smokes),
        "usable_balance": None,
        "balance_kind": None,
        "warnings": warnings,
        "latency_ms": max((s.get("latency_ms") or 0) for s in smokes) if smokes else None,
        "redacted": True,
        "source": "watch",
        "detail": {"aliases": [{"alias": s["alias"], "image": s["with_image"],
                                 "status": s.get("status"),
                                 "upstream": s.get("upstream"),
                                 "latency_ms": s.get("latency_ms")} for s in smokes],
                    "log_errors": errors, "log_file": log_name,
                    "live_catalog": catalog},
    }
    logged = append_health(rec)

    payload = {"ok": status in ("ACTIVE", "DEGRADED"), "status": status,
               "health_log_written": logged,
               "aliases": [{"alias": s["alias"], "image": s["with_image"],
                             "ok": s["ok"], "status": s.get("status"),
                             "latency_ms": s.get("latency_ms"),
                             "upstream": s.get("upstream"),
                             "error": s.get("error")} for s in smokes],
               "log_errors": errors,
               "live_catalog": catalog,
               "warnings": warnings}
    out(payload)
    return 0 if status == "ACTIVE" else (1 if status in ("DEGRADED", "ERROR") else 2)


if __name__ == "__main__":
    sys.exit(main())
