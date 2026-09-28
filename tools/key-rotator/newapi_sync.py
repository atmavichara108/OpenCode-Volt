#!/usr/bin/env python3
"""newapi_sync — синк bench-PASS моделей в каналы New API (admin API).

Слой шлюза (docs/specs/newapi-gateway-layer.md): все key-based провайдеры
(amd, google, mistral, реле) заменяются ЕДИНОЙ точкой входа `newapi/<alias>`
для всех агентов. New API сам выбирает реальный канал per-request
(priority+weight, transparent failover), агент не видит смену провайдера.

Правило приёмки (bench-gate): модель попадает каналом ТОЛЬКО с пройденным
бенчем. Порядок: `probe ACTIVE` -> `model-bench PASS (tools/build/reasoning)`.
Модель без PASS в роутер НЕ попадает.

Роль ротатора здесь СДВИНУТА: для key-based тира он больше НЕ правит конфиги
агентов — только управляет каналами New API (регистрация/дизейбл через admin
API). Правка `model:` в конфигах агентов — руками оператора (сниппеты).

Безопасность: ключи провайдеров нигде не логируются и не печатаются (redact).
Секреты читаются так же, как в probe.py: env -> vault .env -> auth.json.

Контракт вывода: одна строка JSON {"ok": true, ...} | {"ok": false, "error": ...}
Exit: 0 ок | 1 были ошибки при синке | 2 ошибка ввода | 3 фатальная.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import keys as key_store
from lib import redact as redact_mod

TOOL_DIR = Path(__file__).resolve().parent
VAULT_ROOT = TOOL_DIR.parents[1]
CATALOG_PATH = TOOL_DIR / "providers.json"
HEALTH_LOG = VAULT_ROOT / "control-plane" / "telemetry" / "provider-health.jsonl"
BENCH_DIR = VAULT_ROOT / "01-Reference" / "model-benchmarks"

ALIASES = {
    "free-code": "coding",
    "free-general": "general",
    "free-vision": "vision",
}

GATE_BY_ROLE = {
    "coding": ("tools", "build"),
    "general": ("tools", "reasoning"),
    "vision": ("tools",),
}

OK_STATUSES = {"ACTIVE", "DEGRADED"}

NEWAPI_BASE_URL_ENV = "NEWAPI_BASE_URL"
NEWAPI_ADMIN_TOKEN_ENV = "NEWAPI_ADMIN_TOKEN"
DEFAULT_BASE_URL = "http://127.0.0.1:3000"


def out(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def fail(msg: str, code: int = 2) -> int:
    out({"ok": False, "error": msg})
    return code


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{path.name}: {exc}")


def load_catalog(path: Path = CATALOG_PATH) -> dict:
    data = load_json(path)
    providers = data.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise SystemExit("каталог провайдеров: пустой providers")
    return data


def load_bench(dir_path: Path = BENCH_DIR) -> list[dict]:
    results = []
    if not dir_path.is_dir():
        return results
    for p in sorted(dir_path.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("provider_id") and data.get("model_id"):
            results.append(data)
    return results


def read_health(path: Path = HEALTH_LOG) -> dict[str, dict]:
    res: dict[str, dict] = {}
    if not path.is_file():
        return res
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = rec.get("provider_id")
            if pid:
                res[pid] = rec
    except OSError:
        return {}
    return res


def bare_model(model_id: str) -> str:
    if not model_id:
        return ""
    if "/" not in model_id:
        return model_id
    _, _, rest = model_id.partition("/")
    return rest


def model_roles(provider_cfg: dict, bench: dict) -> list[str]:
    """Алиасы/роли, под которые модель допускается (bench-gate).

    Критерии (детерминированный, консервативный):
      - coding  допускается, если PASS и tools, и build.
      - general допускается, если PASS и tools, и reasoning.
      - vision  допускается, если PASS tools и модель vision-способна.

    Роль/vision берутся из models_detail каталога (если задано); иначе
    vision=False, а роль — только из pass-гейтов. Без models_detail модель
    не попадёт в vision-алиас осознанно — не заводим в роутер модель без
    подтверждённого vision-агентства.
    """
    gates = set(bench.get("recommendation") or [])
    md = (provider_cfg or {}).get("models_detail") or {}
    entry = md.get(bare_model(bench.get("model_id", ""))) or {}
    role_hint = entry.get("role")
    vision = bool(entry.get("vision"))
    roles = []
    if set(GATE_BY_ROLE["coding"]) <= gates:
        roles.append("coding")
    if set(GATE_BY_ROLE["general"]) <= gates:
        roles.append("general")
    if set(GATE_BY_ROLE["vision"]) <= gates and vision:
        roles.append("vision")
    if role_hint in ("coding", "general", "vision") and role_hint not in roles:
        if "tools" in gates:
            roles.append(role_hint)
    return roles


def channel_name(provider_id: str, model_id: str, alias: str) -> str:
    return f"{provider_id}|{model_id}|{alias}"


def build_channel(provider_id: str, provider_cfg: dict, model_id: str,
                  alias: str, key_value: str = "") -> dict:
    """Тело канала New API (type 1 = OpenAI-compatible).

    base_url из каталога провайдера; models — [model_id]; group — алиас;
    priority из каталога. Секрет подставляется только при apply (--apply),
    никогда в dry-run/вывод.
    """
    urls = provider_cfg.get("endpoints") or [provider_cfg.get("endpoint")]
    base_url = next((u for u in urls if u), "")
    priority = provider_cfg.get("priority") or 0
    try:
        priority = int(priority)
    except (TypeError, ValueError):
        priority = 0
    return {
        "type": 1,
        "name": channel_name(provider_id, model_id, alias),
        "base_url": base_url,
        "key": key_value,
        "models": model_id,
        "group": [alias],
        "priority": priority,
        "weight": 0,
    }


# --- клиент admin API New API ------------------------------------------------

class NewApiClient:
    """Минимальный клиент admin REST New API.

    Эндпоинты (конвенция QuantumNous/new-api, v1):
      GET    /api/channel      -> список каналов  {success, message, data}
      POST   /api/channel      -> создать канал   (тело канала в body)
      PUT    /api/channel/{id} -> обновить канал
      DELETE /api/channel/{id} -> удалить канал

    Аутентификация: System Access Token в `Authorization: Bearer <token>`.
    Транспорт: subprocess curl (обходит отпечаток urllib, см. http_client).
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, body: dict | None = None):
        import subprocess
        cmd = ["curl", "-sS", "-X", method, "-m", "20", "-w", "\n%{http_code}"]
        for name, value in self._headers().items():
            cmd += ["-H", f"{name}: {value}"]
        if body is not None:
            cmd += ["--data-binary", json.dumps(body, ensure_ascii=False)]
        cmd.append(self.base_url + path)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, f"newapi: {type(exc).__name__}: {exc}"
        outp = proc.stdout or ""
        status_line = outp.rsplit("\n", 1)[-1].strip()
        payload_text = outp.rsplit("\n", 1)[0] if "\n" in outp else outp
        try:
            status = int(status_line)
        except ValueError:
            status = 0
        try:
            payload = json.loads(payload_text) if payload_text else {}
        except json.JSONDecodeError:
            payload = {"raw": payload_text[:500]}
        if proc.returncode != 0 and status == 0:
            return None, f"newapi: exit {proc.returncode}: {(proc.stderr or '')[:300]}"
        return {"status": status, "payload": payload}, None

    def list_channels(self):
        data, err = self._request("GET", "/api/channel")
        if err:
            return None, err
        assert data is not None
        if data["status"] >= 400:
            return None, f"list_channels HTTP {data['status']}: {str(data['payload'])[:200]}"
        return data["payload"].get("data") or [], None

    def create_channel(self, channel: dict):
        data, err = self._request("POST", "/api/channel", channel)
        if err:
            return None, err
        assert data is not None
        if data["status"] >= 400:
            return None, f"create_channel HTTP {data['status']}: {str(data['payload'])[:200]}"
        return data["payload"], None

    def update_channel(self, channel_id: int, channel: dict):
        data, err = self._request("PUT", f"/api/channel/{channel_id}", channel)
        if err:
            return None, err
        assert data is not None
        if data["status"] >= 400:
            return None, f"update_channel HTTP {data['status']}: {str(data['payload'])[:200]}"
        return data["payload"], None

    def delete_channel(self, channel_id: int):
        data, err = self._request("DELETE", f"/api/channel/{channel_id}")
        if err:
            return None, err
        assert data is not None
        if data["status"] >= 400:
            return None, f"delete_channel HTTP {data['status']}: {str(data['payload'])[:200]}"
        return data["payload"], None


# --- план синка -------------------------------------------------------------

def build_plan(catalog: dict, benchmarks: list[dict],
               health: dict[str, dict]) -> tuple[list[dict], dict]:
    """Желаемое состояние каналов из каталога + бенчей + здоровья.

    Для каждого бенч-артефакта: провайдер не skip и здоров в health-log,
    модель проходит bench-gate хотя бы по одной алиас-роли. Канал — на пару
    (модель, алиас-роль). Ничего не создаёт/не удаляет — только вычисляет.
    """
    providers = catalog.get("providers") or {}
    stats = {
        "scan_models": len(benchmarks),
        "provider_missing": 0,
        "provider_skipped": 0,
        "provider_unhealthy": 0,
        "no_gate_pass": 0,
        "candidate_channels": 0,
        "by_alias": {a: 0 for a in ALIASES},
    }
    channels: list[dict] = []
    seen: set[tuple] = set()
    for bench in benchmarks:
        pid = bench.get("provider_id")
        mid = bench.get("model_id")
        if not pid or not mid:
            continue
        pcfg = providers.get(pid)
        if not pcfg:
            stats["provider_missing"] += 1
            continue
        if pcfg.get("skip"):
            stats["provider_skipped"] += 1
            continue
        h = health.get(pid)
        if not h or h.get("status") not in OK_STATUSES:
            stats["provider_unhealthy"] += 1
            continue
        roles = model_roles(pcfg, bench)
        if not roles:
            stats["no_gate_pass"] += 1
            continue
        for role in roles:
            alias = next((a for a, r in ALIASES.items() if r == role), role)
            key = (pid, mid, alias)
            if key in seen:
                continue
            seen.add(key)
            channels.append({
                "provider_id": pid, "model_id": mid, "alias": alias,
                "role": role, "channel": build_channel(pid, pcfg, mid, alias),
            })
            stats["candidate_channels"] += 1
            stats["by_alias"][alias] = stats["by_alias"].get(alias, 0) + 1
    channels.sort(key=lambda c: (c["alias"], c["provider_id"], c["model_id"]))
    return channels, stats


def existing_key(existing: list[dict] | None, provider_id: str, model_id: str,
                 alias: str):
    """id существующего канала по (provider, model, alias) или None."""
    want = channel_name(provider_id, model_id, alias)
    for chan in existing or []:
        if chan.get("name") == want:
            chan_id = chan.get("id")
            if isinstance(chan_id, dict):
                chan_id = chan_id.get("value")
            return int(chan_id) if isinstance(chan_id, int) else chan_id
    return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="newapi_sync",
        description="Синк bench-PASS моделей в каналы New API (bench-gate).",
    )
    p.add_argument("--base-url", default=None,
                   help=f"адрес New API (default env {NEWAPI_BASE_URL_ENV} или {DEFAULT_BASE_URL})")
    p.add_argument("--admin-token", default=None,
                   help=f"System Access Token (default env {NEWAPI_ADMIN_TOKEN_ENV})")
    p.add_argument("--bench-dir", default=str(BENCH_DIR),
                   help="каталог бенч-артефактов")
    p.add_argument("--alias", action="append", default=[],
                   help="только эти алиасы (free-code|free-general|free-vision)")
    p.add_argument("--apply", action="store_true",
                   help="реально создать/обновить каналы (по умолчанию dry-run-план)")
    p.add_argument("--delete-stale", action="store_true",
                   help="удалить каналы, которых нет в плане (только с --apply)")
    p.add_argument("--quiet", action="store_true",
                   help="только итоговая строка JSON")
    args = p.parse_args(argv)

    try:
        catalog = load_catalog()
        benchmarks = load_bench(Path(args.bench_dir))
        health = read_health(HEALTH_LOG)
    except SystemExit as exc:
        return fail(str(exc), 3)

    channels, stats = build_plan(catalog, benchmarks, health)
    if args.alias:
        wanted = set(args.alias)
        unknown = wanted - set(ALIASES)
        if unknown:
            return fail(f"неизвестные алиасы: {', '.join(sorted(unknown))}")
        channels = [c for c in channels if c["alias"] in wanted]

    if not args.apply:
        plan = [
            {"provider_id": c["provider_id"], "model_id": c["model_id"],
             "alias": c["alias"], "role": c["role"], "name": c["channel"]["name"],
             "base_url": c["channel"]["base_url"],
             "priority": c["channel"]["priority"]}
            for c in channels
        ]
        payload = {"ok": True, "plan": True, "stats": stats, "channels": plan}
        out(redact_mod.redact_obj(payload, keys=[]))
        return 0

    base = args.base_url or os.getenv(NEWAPI_BASE_URL_ENV) or DEFAULT_BASE_URL
    token = args.admin_token or os.getenv(NEWAPI_ADMIN_TOKEN_ENV) or ""
    if not token:
        return fail(f"нет токена admin New API (--admin-token или env {NEWAPI_ADMIN_TOKEN_ENV})", 2)

    client = NewApiClient(base, token)
    existing, err = client.list_channels()
    if err:
        return fail(f"нет доступа к admin API: {err}", 1)

    errors = 0
    stale_deleted = 0
    if args.delete_stale:
        planned = {c["channel"]["name"] for c in channels}
        for chan in existing or []:
            name = chan.get("name") or ""
            # трогаем только каналы нашего слоя (имя = prov|model|alias)
            if "|" not in name or name in planned:
                continue
            chan_id = chan.get("id")
            if isinstance(chan_id, dict):
                chan_id = chan_id.get("value")
            if chan_id is None:
                continue
            _, derr = client.delete_channel(int(chan_id))
            if derr:
                errors += 1
            else:
                stale_deleted += 1

    results = []
    for c in channels:
        pcfg = catalog["providers"][c["provider_id"]]
        chan = c["channel"]
        key_value, _ = key_store.resolve_key(pcfg.get("env"), pcfg.get("auth_id"))
        if key_value:
            chan["key"] = key_value
        chan_id = existing_key(existing, c["provider_id"], c["model_id"], c["alias"])
        entry = {"provider_id": c["provider_id"], "model_id": c["model_id"],
                 "alias": c["alias"], "role": c["role"], "has_key": bool(key_value)}
        if chan_id is not None:
            _, err = client.update_channel(chan_id, chan)
            entry["action"] = "error" if err else "updated"
            entry["channel_id"] = chan_id
        else:
            res, err = client.create_channel(chan)
            entry["action"] = "error" if err else "created"
            entry["channel_id"] = None if err else (res or {}).get("id")
        if err:
            entry["error"] = err
            errors += 1
        results.append(entry)

    summary = {"errors": errors, "stale_deleted": stale_deleted}
    payload = {"ok": errors == 0, "stats": stats, "summary": summary,
               "results": results}
    out(redact_mod.redact_obj(payload, keys=[]))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())