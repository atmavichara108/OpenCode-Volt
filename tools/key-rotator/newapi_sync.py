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

# Алиасы шлюза по ролям (см. спека §5).
ALIASES = {
    "free-code": "coding",
    "free-general": "general",
    "free-vision": "vision",
}

# Гейты, обязательные для допуска роли в канал.
# База для всех агентских ролей: tools PASS (tool-calling + JSON без говнокода).
GATE_BY_ROLE = {
    "coding": ("tools", "build"),
    "general": ("tools", "reasoning"),
    "vision": ("tools",),
}

# Статусы провайдера, допустимые для канала (health-log).
OK_STATUSES = {"ACTIVE", "DEGRADED"}

NEWAPI_BASE_URL_ENV = "NEWAPI_BASE_URL"
NEWAPI_ADMIN_TOKEN_ENV = "NEWAPI_ADMIN_TOKEN"

DEFAULT_BASE_URL = "http://127.0.0.1:3000"


# --- helper: вывести ---------------------------------------------------------

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


# --- данные: каталог, бенч, здоровье ----------------------------------------

def load_catalog(path: Path = CATALOG_PATH) -> dict:
    data = load_json(path)
    providers = data.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise SystemExit("каталог провайдеров: пустой providers")
    return data


def load_bench(dir_path: Path = BENCH_DIR) -> list[dict]:
    """Все per-model JSON из каталога бенчей (без matrix.md)."""
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
    """Последняя запись на провайдер из append-only JSONL."""
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


# --- модель: bare-имя, вхождение, элиджибилити -------------------------------

def bare_model(model_id: str) -> str:
    """'prov/vendor/id' -> 'vendor/id'; 'prov/id' -> 'id'; 'id' -> 'id'."""
    if not model_id:
        return ""
    if "/" not in model_id:
        return model_id
    _, _, rest = model_id.partition("/")
    return rest


def model_roles(provider_cfg: dict, bench: dict) -> list[str]:
    """Алиасы, под которые модель допускается (bench-gate).

    Критерий (детерминированный, консервативный):
      - провайдер должен быть не skip и здоров (проверяется отдельно, см. sync).
      - роль `coding`  допускается, если PASS и tools, и build.
      - роль `general` допускается, если PASS и tools, и reasoning.
      - роль `vision`  допускается, если PASS tools и модель vision-способна.

    Роль/vision берутся из models_detail каталога (если задано); иначе
    vision=False, а роль — только из pass-гейтов. Это значит: без models_detail
    модель не попадёт в vision-алиас — осознанно, чтобы не заводить в роутер
    модель без подтверждённого vision-агентства.
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
        # models_detail явно называет агентскую роль — допустим по этому сигналу,
        # только если база tools всё же пройдена (не даём пролезть без tools).
        if "tools" in gates:
            roles.append(role_hint)
    return roles