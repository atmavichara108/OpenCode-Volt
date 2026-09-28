#!/usr/bin/env python3
"""rotate — Iter-1: failover-ротация моделей агентов (probe → выбор → apply → notify).

Поведение:
  по умолчанию читает последний health-log (быстро, без сети);
  --probe перед выбором прогоняет свежий read-only probe (Iter-0).

Причина ротации агента:
  * провайдер его текущей модели BLOCKED/ERROR в health-log → failover;
  * --prefer-better: лучший кандидат для роли строго выше по priority (апгрейд);
  * иначе агент НЕ трогается (никакого дёрганья без причины).

Кандидат: провайдер из каталога (не skip), статус healthy, роль подходит,
провайдер реально виден model-router (live/declared/in-use), иначе модель
не заработает у OpenCode. Модель: preferred-подстрока по роли, иначе первая
доступная провайдера.

Запись: только через model-router.py (flock + бэкап + atomic) — сюда в
конфиг не пишем. Уведомление — ненавязчивый ntfy-пуш (curl, не urllib),
без топика молча пропускается.

Контракт вывода: одна строка JSON {"ok": true, ...} | {"ok": false, "error": ...}
Exit: 0 ок · 1 были ошибки apply/probe · 2 ошибка ввода.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import keys as key_store
from lib import notify as notify_mod
from lib import redact as redact_mod
from lib import router

TOOL_DIR = Path(__file__).resolve().parent
VAULT_ROOT = TOOL_DIR.parents[1]
CATALOG_PATH = TOOL_DIR / "providers.json"
ROTATION_PATH = TOOL_DIR / "rotation.json"
HEALTH_LOG = VAULT_ROOT / "control-plane" / "telemetry" / "provider-health.jsonl"
PROBE_SCRIPT = TOOL_DIR / "probe.py"


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


# --- статусы из health-log -------------------------------------------------

def read_health_statuses(path: Path = HEALTH_LOG) -> dict[str, dict]:
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


def run_probe(timeout: int = 20, retries: int = 1, pause: float = 5.0) -> tuple[bool, str]:
    """Свежий read-only probe перед выбором. → (ok, error)."""
    cmd = [sys.executable, str(PROBE_SCRIPT),
           "--quiet", "--timeout", str(timeout),
           "--retries", str(retries), "--pause", str(pause)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout * 30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"probe: {type(exc).__name__}: {exc}"
    if proc.returncode not in (0, 1):  # 1 = есть ERROR по провайдерам — статусы записаны
        return False, f"probe exit {proc.returncode}: {(proc.stderr or proc.stdout or '')[:300]}"
    return True, ""


# --- выбор кандидата -------------------------------------------------------

def role_for(agent: str, rot: dict) -> str:
    roles = rot.get("agent_roles") or {}
    return roles.get(agent, rot.get("default_role", "coding"))


def split_model(model: str) -> tuple[str | None, str | None]:
    """'prov/vendor/id' → ('prov', 'vendor/id'); 'prov/id' → ('prov', 'id')."""
    if not model or "/" not in model:
        return None, None
    prov, _, rest = model.partition("/")
    return prov, rest or None


def is_healthy(pid: str, statuses: dict[str, dict], rot: dict) -> bool:
    rec = statuses.get(pid)
    if not rec:
        return False  # нет данных probe — не рискуем
    return rec.get("status") in (rot.get("healthy_statuses") or ["ACTIVE"])


def choose_candidate(current_provider: str | None, role: str,
                     statuses: dict[str, dict], rot: dict, catalog: dict,
                     models_by_provider: dict[str, list[str]],
                     providers: dict) -> dict | None:
    """Лучший кандидат по роли: с preferred → по priority. Не включая current."""
    preferred = rot.get("preferred") or {}
    ranked: list[tuple] = []
    for pid, pcfg in (catalog.get("providers") or {}).items():
        if pcfg.get("skip"):
            continue
        if pid == current_provider:
            continue
        if pid not in models_by_provider:
            continue  # провайдер не объявлен/не виден рантайму — модель не заработает
        if role not in (pcfg.get("roles") or []):
            continue
        if not is_healthy(pid, statuses, rot):
            continue
        has_pref = bool((preferred.get(pid) or {}).get(role))
        priority = pcfg.get("priority", 0)
        # сортировка: (не preferred сначала — pref выше, priority убывание)
        ranked.append((0 if has_pref else 1, -priority, pid))
    if not ranked:
        return None
    ranked.sort()
    _, _, pid = ranked[0]
    pcfg = catalog["providers"][pid]
    pref_list = (preferred.get(pid) or {}).get(role) or []
    avail = models_by_provider.get(pid) or []

    model = None
    lower_avail = [(m, m.lower()) for m in avail]
    for pref in pref_list:
        pl = str(pref).lower()
        for mid, ml in lower_avail:
            if pl in ml:
                model = mid
                break
        if model:
            break
    if not model and avail:
        model = avail[0]
    if not model:
        return None
    # collect_models отдаёт id уже с префиксом провайдера (prov/model)
    full = model if model.startswith(f"{pid}/") else f"{pid}/{model}"
    return {"provider": pid, "model": full,
            "priority": pcfg.get("priority", 0),
            "preferred": bool(pref_list)}


# --- применение ------------------------------------------------------------

def append_switch_event(rec: dict, path: Path = HEALTH_LOG) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="rotate",
        description="Failover-ротация моделей агентов (Iter-1).",
    )
    p.add_argument("--agent", action="append", default=[],
                   help="ротировать только этих агентов (можно несколько)")
    p.add_argument("--project", default=None, help="project id (для проектных агентов)")
    p.add_argument("--probe", action="store_true",
                   help="свежий read-only probe перед выбором (по умолчанию читаем health-log)")
    p.add_argument("--prefer-better", action="store_true",
                   help="апгрейд на лучшего кандидата даже если текущий здоров")
    p.add_argument("--dry-run", action="store_true",
                   help="показать решения, ничего не писать и не уведомлять")
    p.add_argument("--no-notify", action="store_true", help="без ntfy-пуша")
    p.add_argument("--no-log", action="store_true", help="не писать события switch в health-log")
    p.add_argument("--quiet", action="store_true", help="только итоговая строка JSON")

    args = p.parse_args(argv)

    catalog = load_json(CATALOG_PATH)
    rot = load_json(ROTATION_PATH)

    if args.probe:
        ok, err = run_probe()
        if not ok and not args.quiet:
            print(f"  ! probe: {err}", file=sys.stderr)
        if not ok and not read_health_statuses(HEALTH_LOG):
            return fail(err, 1)

    statuses = read_health_statuses(HEALTH_LOG)
    if not statuses:
        return fail("health-log пуст — сначала probe: probe.py (или --probe)", 2)

    agents_payload, err = router.list_agents(args.project)
    if err:
        return fail(err, 1)
    models_payload, err = router.list_models()
    if err:
        return fail(err, 1)

    by_provider = router.available_models_by_provider(models_payload)
    agents = (agents_payload or {}).get("agents") or []
    if args.agent:
        wanted = set(args.agent)
        agents = [a for a in agents if a.get("agent") in wanted]
        missing = wanted - {a.get("agent") for a in agents}
        if missing:
            return fail(f"агенты не найдены: {', '.join(sorted(missing))}")

    results: list[dict] = []
    errors = 0

    for agent in agents:
        name = agent.get("agent")
        current = agent.get("model")
        scope = agent.get("scope")
        project = agent.get("project")
        if not name:
            continue
        if not current:
            results.append({"agent": name, "scope": scope, "action": "skip",
                            "reason": "no_model"})
            continue

        role = role_for(name, rot)
        cur_prov, _ = split_model(current)
        candidates = choose_candidate(cur_prov, role, statuses, rot, catalog,
                                      by_provider, catalog.get("providers") or {})
        # reason
        rec = statuses.get(cur_prov) if cur_prov else None
        status = (rec or {}).get("status")
        reason = None
        if status is not None and status in (rot.get("failover_statuses") or ["BLOCKED", "ERROR"]):
            reason = f"provider_{str(status).lower()}"
        elif status is None:
            reason = None
        elif args.prefer_better and candidates:
            cur_prio = (catalog.get("providers") or {}).get(cur_prov, {}).get("priority", 0)
            if candidates["priority"] > cur_prio and candidates["provider"] != cur_prov:
                reason = "prefer_better"

        if not reason:
            results.append({"agent": name, "scope": scope,
                            "action": "keep", "model": current,
                            "provider_status": status or "unknown",
                            "role": role})
            continue
        if not candidates:
            results.append({"agent": name, "scope": scope, "action": "skip",
                            "reason": reason, "model": current,
                            "note": "нет здорового кандидата для роли"})
            continue
        new_model = candidates["model"]
        if new_model == current:
            results.append({"agent": name, "scope": scope, "action": "keep",
                            "model": current, "reason": reason,
                            "note": "лучший кандидат уже стоит"})
            continue

        apply_payload, apply_err = router.apply(
            name, new_model, scope=scope, project=project,
            kind=agent.get("kind"), dry_run=args.dry_run)
        entry = {
            "agent": name, "scope": scope, "project": project,
            "from": current, "to": new_model, "reason": reason,
            "role": role, "provider": candidates["provider"],
            "dry_run": args.dry_run,
        }
        if apply_err:
            errors += 1
            entry.update({"action": "error", "error": apply_err})
            results.append(entry)
            continue
        payload = apply_payload or {}
        if args.dry_run:
            # model-router в dry-run всегда changed:false — решаем по diff
            changed = bool(payload.get("diff"))
            entry["action"] = "applied" if changed else "noop"
        else:
            changed = bool(payload.get("changed"))
            entry["action"] = "applied" if changed else "noop"
        entry["changed"] = changed
        results.append(entry)

        if changed and not args.dry_run and not args.no_log:
            append_switch_event({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": "switch", "agent": name, "scope": scope,
                "project": project, "from": current, "to": new_model,
                "reason": reason, "verified": True, "redacted": True,
            })
        if changed and not args.dry_run and not args.no_notify:
            msg = notify_mod.format_switch(name, scope, project, current,
                                           new_model, reason)
            nres = notify_mod.send(msg, priority="default")
            entry["notify"] = {"ok": nres.get("ok"),
                               "skipped": nres.get("skipped")}

    summary = {
        "total": len(results),
        "kept": sum(1 for r in results if r.get("action") == "keep"),
        "switched": sum(1 for r in results if r.get("action") == "applied"
                        and not r.get("dry_run")),
        "dry": sum(1 for r in results if r.get("action") == "applied"
                   and r.get("dry_run")),
        "skipped": sum(1 for r in results if r.get("action") == "skip"),
        "errors": errors,
        "notifies_sent": sum(1 for r in results
                             if (r.get("notify") or {}).get("ok")),
    }

    if not args.quiet:
        for r in results:
            a = r.get("action")
            if a == "applied":
                mark = "~" if r.get("dry_run") else "+"
                print(f"  {mark} {r['agent']:<16} {r['from']} → {r['to']} ({r['reason']})",
                      file=sys.stderr)
            elif a == "error":
                print(f"  ! {r['agent']:<16} {r.get('error')}", file=sys.stderr)

    payload = {"ok": errors == 0, "summary": summary, "results": results}
    redacted = redact_mod.redact_obj(payload, keys=[key_store.resolve_key(None, None)[0]])
    out(redacted if isinstance(redacted, dict) else payload)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
