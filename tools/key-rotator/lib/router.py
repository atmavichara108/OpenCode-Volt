"""Обёртка над tools/ecosystem-map/model-router.py (subprocess, JSON-контракт).

Не дублирует логику правки конфига — вся запись идёт через model-router
(flock + бэкап + atomic). Здесь только вызов и разбор JSON-ответа.
"""
import json
import shutil
import subprocess
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[3]
MODEL_ROUTER = VAULT_ROOT / "tools" / "ecosystem-map" / "model-router.py"


def _python():
    venv = VAULT_ROOT / ".venv" / "bin" / "python"
    return str(venv) if venv.is_file() else "python3"


def _run(args, timeout=60):
    exe = shutil.which(_python()) or _python()
    cmd = [exe, str(MODEL_ROUTER)] + args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"model-router: {type(exc).__name__}: {exc}"
    out = (proc.stdout or "").strip()
    if not out:
        return None, f"model-router: пустой вывод (exit {proc.returncode}, stderr={(proc.stderr or '').strip()[:200]})"
    try:
        data = json.loads(out.splitlines()[-1])
    except json.JSONDecodeError:
        return None, f"model-router: не-JSON вывод: {out[:200]}"
    if not data.get("ok"):
        return None, data.get("error") or "model-router: ok=false"
    return data, None


def list_agents(project=None):
    args = ["list"]
    if project:
        args += ["--project", project]
    return _run(args)


def list_models():
    return _run(["models"])


def apply(agent, model, *, scope=None, project=None, kind=None,
          dry_run=False, no_backup=False):
    args = ["apply", "--agent", agent, "--model", model]
    if scope:
        args += ["--scope", scope]
    if project:
        args += ["--project", project]
    if kind:
        args += ["--kind", kind]
    if dry_run:
        args.append("--dry-run")
    if no_backup:
        args.append("--no-backup")
    return _run(args)


def available_models_by_provider(models_payload):
    """{provider: [model_id, ...]} из collect_models() — id уже полный (prov/model)."""
    res = {}
    for entry in (models_payload or {}).get("models") or []:
        pid = entry.get("provider")
        mid = entry.get("id")
        if pid and mid:
            res.setdefault(pid, []).append(mid)
    return res
