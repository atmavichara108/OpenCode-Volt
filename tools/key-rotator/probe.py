#!/usr/bin/env python3
"""key-rotator probe — read-only проверка провайдеров (Iter-0).

Что делает:
  GET /models на каждый провайдер из providers.json (ключ: env -> .env -> auth.json),
  классифицирует результат в статусы ACTIVE|DEGRADED|BLOCKED|ERROR|SKIPPED,
  опционально --smoke (оплачиваемый чат, только opt-in), пишет append-only
  health-лог, ключи никогда не попадают в вывод/логи (redact).

Транспорт: curl (обход отпечатка urllib/Cloudflare 1010; см. key-rotator-brief);
fallback requests. 429 ретраится (по умолчанию до 2 раз, пауза 20с).

Контракт вывода: одна строка JSON {"ok": true, ...} | {"ok": false, "error": ...}
Exit: 0 все прогоны без ERROR | 1 есть ERROR | 2 ошибка ввода | 3 фатальная.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import http_client
from lib import keys as key_store
from lib import redact as redact_mod

TOOL_DIR = Path(__file__).resolve().parent
VAULT_ROOT = TOOL_DIR.parents[1]
CATALOG_PATH = TOOL_DIR / "providers.json"
HEALTH_LOG = VAULT_ROOT / "control-plane" / "telemetry" / "provider-health.jsonl"

EXIT_BY_STATUS = {"ACTIVE": 0, "DEGRADED": 1, "BLOCKED": 2, "ERROR": 3, "SKIPPED": 4}

DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 2
DEFAULT_PAUSE = 20.0


def out(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def fail(msg: str, code: int = 2) -> int:
    out({"ok": False, "error": msg})
    return code


def load_catalog(path: Path = CATALOG_PATH) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"каталог провайдеров: {exc}")
    providers = data.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise SystemExit("каталог провайдеров: пустой providers")
    return data


def auth_headers(key: str) -> dict:
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def anthropic_headers(key: str) -> dict:
    return {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def classify_models(resp: dict, cfg: dict) -> tuple[str, list[str], int, list[str]]:
    warnings: list[str] = []
    status = "ACTIVE"
    body = resp.get("body") or ""
    code = resp.get("status")

    if resp.get("error_kind") == "network" and code is None:
        warnings.append("network")
        return "ERROR", warnings, 0, []

    if code in (401,):
        warnings.append(f"http_{code}")
        return "BLOCKED", warnings, 0, []
    if code == 403:
        if http_client.is_cloudflare_fingerprint(body):
            warnings.append("cloudflare_1010_client_fingerprint")
        else:
            warnings.append("http_403")
        return "BLOCKED", warnings, 0, []
    if code == 429:
        warnings.append("rate_limited")
        return "DEGRADED", warnings, 0, []
    if code is None or code >= 500 or code < 200:
        warnings.append(f"http_{code}" if code else "no_status")
        return "ERROR", warnings, 0, []
    if code >= 400:
        warnings.append(f"http_{code}")
        return "DEGRADED", warnings, 0, []

    model_ids: list[str] = []
    if body.strip():
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            warnings.append("non_json_body")
            return "BLOCKED", warnings, 0, []
        raw = data.get("data") if isinstance(data, dict) else data
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    mid = item.get("id") or item.get("name")
                else:
                    mid = item
                if mid:
                    model_ids.append(str(mid))
    if not model_ids:
        warnings.append("empty_models")
        return "BLOCKED", warnings, 0, []

    warnings.append("balance_unknown")
    return "ACTIVE", warnings, len(model_ids), model_ids


def probe_models(cfg: dict, key: str, *, timeout: int, retries: int,
                 pause: float, endpoint: str) -> tuple[dict, list[str]]:
    headers = anthropic_headers(key) if cfg.get("transport") == "anthropic" else auth_headers(key)
    if cfg.get("transport") == "anthropic":
        url = endpoint.rstrip("/")
        if not url.endswith("/models"):
            url = url + "/models"
    else:
        url = endpoint.rstrip("/")
        if not url.endswith("/models"):
            url = url + "/models"
    resp = http_client.request("GET", url, headers=headers, timeout=timeout,
                               retries=retries, pause=pause)
    return resp, []


def probe_smoke(cfg: dict, key: str, *, endpoint: str, model: str,
                timeout: int, retries: int, pause: float) -> dict:
    transport = cfg.get("transport", "openai")
    if transport == "anthropic":
        url = endpoint.rstrip("/")
        if url.endswith("/v1"):
            url = url[: -len("/v1")] + "/v1/messages"
        if not url.endswith("/messages"):
            url = endpoint.rstrip("/") + "/messages"
        headers = anthropic_headers(key)
        json_body = {
            "model": model,
            "max_tokens": 32,
            "messages": [{"role": "user", "content": "ping"}],
        }
    elif transport == "google":
        url = endpoint.rstrip("/") + "/chat/completions"
        headers = auth_headers(key)
        json_body = {
            "model": model,
            "max_tokens": 32,
            "messages": [{"role": "user", "content": "ping"}],
        }
    else:
        url = endpoint.rstrip("/") + "/chat/completions"
        headers = auth_headers(key)
        json_body = {
            "model": model,
            "max_tokens": 32,
            "messages": [{"role": "user", "content": "ping"}],
        }
    resp = http_client.request("POST", url, headers=headers, json_body=json_body,
                               timeout=timeout, retries=retries, pause=pause)
    code = resp.get("status")
    body = (resp.get("body") or "")
    ok = bool(code and 200 <= code < 300)
    fin = None
    if body.strip():
        try:
            parsed = json.loads(body)
            fin = (parsed.get("choices") or [{}])[0].get("finish_reason")
        except (json.JSONDecodeError, IndexError, KeyError, TypeError):
            fin = None
    return {"ok": ok, "status": code, "finish_reason": fin,
            "error_kind": resp.get("error_kind")}


def probe_provider(pid: str, cfg: dict, *, timeout: int, retries: int,
                   pause: float, smoke: bool, smoke_model: str | None) -> dict:
    checked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec: dict = {
        "provider_id": pid,
        "status": "ERROR",
        "models_count": 0,
        "model_ids_sample": [],
        "endpoint": cfg.get("endpoint"),
        "balance": None,
        "balance_kind": None,
        "warnings": [],
        "latency_ms": None,
        "checked_at": checked_at,
        "transport": cfg.get("transport", "openai"),
        "redacted": True,
    }

    if cfg.get("skip"):
        rec["status"] = "SKIPPED"
        rec["warnings"] = [f"skip_{cfg['skip']}"]
        rec["exit"] = EXIT_BY_STATUS["SKIPPED"]
        return rec

    endpoints = [e for e in (cfg.get("endpoints") or []) if e]
    if not endpoints:
        rec["warnings"] = ["no_endpoint"]
        rec["exit"] = EXIT_BY_STATUS["BLOCKED"]
        rec["status"] = "BLOCKED"
        return rec

    key, source = key_store.resolve_key(cfg.get("env"), cfg.get("auth_id"))
    if not key:
        rec["warnings"] = ["no_key"]
        rec["exit"] = EXIT_BY_STATUS["ERROR"]
        return rec
    rec["key_source"] = source

    last_rec = rec
    best_rec = None
    best_rank = None
    status_rank = {"ACTIVE": 0, "DEGRADED": 1, "BLOCKED": 2, "ERROR": 3}
    for endpoint in endpoints:
        try:
            resp, _ = probe_models(cfg, key, timeout=timeout, retries=retries,
                                   pause=pause, endpoint=endpoint)
        except Exception as exc:
            cand = dict(rec)
            cand["status"] = "ERROR"
            cand["warnings"] = [f"{type(exc).__name__}"]
            cand["endpoint"] = endpoint
            rank = status_rank["ERROR"]
        else:
            status, warnings, count, ids = classify_models(resp, cfg)
            cand = dict(rec)
            cand["status"] = status
            cand["warnings"] = warnings
            cand["models_count"] = count
            cand["model_ids_sample"] = ids[:8]
            cand["latency_ms"] = resp.get("latency_ms")
            cand["endpoint"] = endpoint
            rank = status_rank[status]
        last_rec = cand
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_rec = cand
        if best_rank == 0:
            break

    rec = best_rec if best_rec is not None else last_rec

    if smoke and smoke_model and rec["status"] in ("ACTIVE", "DEGRADED"):
        ep = rec.get("endpoint") or endpoints[0]
        sres = probe_smoke(cfg, key, endpoint=ep, model=smoke_model,
                           timeout=timeout, retries=retries, pause=pause)
        rec["smoke"] = {"model": smoke_model, "ok": sres["ok"],
                        "status": sres.get("status"),
                        "finish_reason": sres.get("finish_reason")}
        if not sres["ok"]:
            rec["warnings"].append("smoke_failed")
            if rec["status"] == "ACTIVE":
                rec["status"] = "DEGRADED"
    elif smoke and not smoke_model:
        rec["warnings"].append("smoke_skipped_no_model")

    rec["exit"] = EXIT_BY_STATUS[rec["status"]]
    return rec


def append_health_log(records: list[dict], path: Path = HEALTH_LOG) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            for rec in records:
                line = {
                    "ts": rec["checked_at"],
                    "provider_id": rec["provider_id"],
                    "status": rec["status"],
                    "models_count": rec["models_count"],
                    "usable_balance": rec["balance"],
                    "balance_kind": rec["balance_kind"],
                    "warnings": rec["warnings"],
                    "latency_ms": rec["latency_ms"],
                    "redacted": True,
                }
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="probe",
        description="Read-only probe промо/реферальных провайдеров (key-rotator Iter-0).",
    )
    p.add_argument("--provider", action="append", default=[],
                   help="probe только этих провайдеров (можно несколько)")
    p.add_argument("--all", action="store_true",
                   help="все провайдеры из каталога (по умолчанию)")
    p.add_argument("--smoke", action="store_true",
                   help="оплачиваемый smoke-чат (только opt-in)")
    p.add_argument("--smoke-model", default=None,
                   help="модель для smoke-чата (обязательна при --smoke)")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                   help="ретраи на 429 (по умолчанию 2)")
    p.add_argument("--pause", type=float, default=DEFAULT_PAUSE,
                   help="пауза между 429-ретраями, сек (по умолчанию 20)")
    p.add_argument("--no-log", action="store_true",
                   help="не писать в provider-health.jsonl")
    p.add_argument("--quiet", action="store_true", help="только итоговая строка JSON")

    args = p.parse_args(argv)

    if args.smoke and not args.smoke_model:
        return fail("--smoke требует --smoke-model (явное имя модели оператора)")

    try:
        catalog = load_catalog()
    except SystemExit as exc:
        return fail(str(exc), 3)

    providers: dict = catalog["providers"]
    if args.provider:
        missing = [pid for pid in args.provider if pid not in providers]
        if missing:
            return fail(f"нет в каталоге: {', '.join(missing)}")
        selected = {pid: providers[pid] for pid in args.provider}
    else:
        selected = providers

    started = time.time()
    records: list[dict] = []
    for pid, cfg in selected.items():
        try:
            rec: dict = probe_provider(pid, cfg, timeout=args.timeout,
                                       retries=args.retries, pause=args.pause,
                                       smoke=args.smoke, smoke_model=args.smoke_model)
        except Exception as exc:
            rec = {
                "provider_id": pid, "status": "ERROR", "models_count": 0,
                "warnings": [f"{type(exc).__name__}"], "balance": None,
                "balance_kind": None, "latency_ms": None,
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "endpoint": cfg.get("endpoint"), "redacted": True,
                "exit": EXIT_BY_STATUS["ERROR"],
            }
        redacted = redact_mod.redact_obj(rec, keys=[key_store.resolve_key(
            cfg.get("env"), cfg.get("auth_id"))[0]])
        rec = redacted if isinstance(redacted, dict) else rec
        records.append(rec)
        if not args.quiet:
            status = str(rec.get("status", "ERROR"))
            mark = {"ACTIVE": "+", "DEGRADED": "~", "BLOCKED": "x",
                    "ERROR": "!", "SKIPPED": "-"}.get(status, "?")
            warnings = rec.get("warnings")
            warn = ",".join(str(w) for w in warnings) if isinstance(warnings, list) else "-"
            print(f"  {mark} {pid:<24} {status:<9} "
                  f"models={rec.get('models_count', 0):<3} {warn}", file=sys.stderr)

    logged = False
    if not args.no_log:
        logged = append_health_log(records)

    counts: dict[str, int] = {}
    for rec in records:
        status = str(rec.get("status", "ERROR"))
        counts[status] = counts.get(status, 0) + 1
    run_exit = 1 if counts.get("ERROR") else 0

    out({
        "ok": True,
        "total": len(records),
        "counts": counts,
        "health_log_written": logged,
        "duration_s": round(time.time() - started, 1),
        "providers": records,
    })
    return run_exit


if __name__ == "__main__":
    sys.exit(main())
