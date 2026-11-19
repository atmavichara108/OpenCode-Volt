#!/usr/bin/env python3
"""provider_lifecycle — единая точка жизненного цикла провайдера с бесплатной квотой.

Два типа провайдеров (слово владельца, 2026-11-18):
  * ВРЕМЕННЫЙ — бесплатный период с датой сгорания. Жизненный цикл замкнут:
    добавление обязано зарегистрировать срок (иначе провайдер останется в шлюзе
    навсегда), а по истечении срока срабатывает выпил (trial_expiry.py).
  * ПОСТОЯННЫЙ — обновляемая бесплатная квота (amd-radeon, google, nvidia,
    mistral). Срок не задан: провайдер не выпиливается по дате, вместо этого
    ведётся квотный гейт: израсходована квота → деградация (DEGRADED/ERROR) и
    сигнал владельцу, решение о выпиле — слово владельца.

Связка: `onboard-temporary` пишет в каталог блок `trial` (тот же формат, что
читает trial_expiry.py) — то есть добавление временного провайдера СРАЗУ
регистрирует его в механизме удаления. `onboard-permanent` пишет блок `quota`
(без срока) и НЕ регистрирует выпил.

Команды:
    python3 tools/key-rotator/provider_lifecycle.py status
    python3 tools/key-rotator/provider_lifecycle.py onboard-temporary <pid> --expires 2026-12-01 [--on-expiry delete_channels|disable_channels] [--owner-word "..."] [--fact "..."]
    python3 tools/key-rotator/provider_lifecycle.py onboard-permanent <pid> [--quota-note "..."] [--quota-kind daily_quota|free_tier_credits]
    python3 tools/key-rotator/provider_lifecycle.py reap [--provider <pid>] [--owner-word "..."]
    python3 tools/key-rotator/provider_lifecycle.py set-skip <pid> [--reason "..."] | clear-skip <pid>
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG_PATH = os.path.join(VAULT_ROOT, "tools", "key-rotator", "providers.json")
TRIAL_EXPIRY = os.path.join(VAULT_ROOT, "tools", "key-rotator", "trial_expiry.py")


def today():
    return datetime.date.today().isoformat()


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_catalog(catalog):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")


def require_provider(catalog, pid):
    p = (catalog.get("providers") or {}).get(pid)
    if not p:
        raise SystemExit(json.dumps({"ok": False, "error": "провайдер %r не найден в каталоге" % pid}, ensure_ascii=False))
    return p


def cmd_status(args):
    catalog = load_catalog()
    now = today()
    rows = []
    for pid, p in (catalog.get("providers") or {}).items():
        trial = p.get("trial") or {}
        quota = p.get("quota") or {}
        kind = trial.get("kind") or quota.get("kind") or ""
        if not kind and not trial and not quota:
            continue
        expires = trial.get("expires") or ""
        days_left = None
        expired = False
        if expires:
            try:
                d = (datetime.date.fromisoformat(expires) - datetime.date.fromisoformat(now)).days
                days_left = d
                expired = d < 0
            except ValueError:
                pass
        rows.append({
            "provider_id": pid,
            "lifecycle": "temporary" if trial else ("permanent" if quota else "unknown"),
            "kind": kind,
            "expires": expires or None,
            "days_left": days_left,
            "expired": expired,
            "auto_reap": bool(trial.get("auto_reap")),
            "on_expiry": trial.get("on_expiry"),
            "quota": quota.get("fact") or quota.get("note"),
            "skip": bool(p.get("skip")),
            "skip_reason": p.get("skip_reason"),
            "owner_word": trial.get("owner_word") or quota.get("owner_word"),
        })
    rows.sort(key=lambda r: (r["lifecycle"], r["provider_id"]))
    return {"ok": True, "today": now, "providers": rows}


def cmd_onboard_temporary(args):
    catalog = load_catalog()
    p = require_provider(catalog, args.provider_id)
    if not args.expires:
        raise SystemExit(json.dumps({"ok": False, "error": "для временного провайдера обязателен --expires"}, ensure_ascii=False))
    if not args.owner_word:
        raise SystemExit(json.dumps({"ok": False, "error": "нужен --owner-word (слово владельца на подключение/срок)"}, ensure_ascii=False))
    trial = p.get("trial") or {}
    trial.update({
        "kind": args.kind or trial.get("kind") or "free_period",
        "started": trial.get("started") or today(),
        "expires": args.expires,
        # регистрация в механизме выпила: без auto_reap срок не сработает
        "auto_reap": True if args.auto_reap is None else args.auto_reap,
        "on_expiry": args.on_expiry or trial.get("on_expiry") or "delete_channels",
        "owner_word": args.owner_word,
    })
    if args.fact:
        trial["fact"] = args.fact
    p["trial"] = trial
    p.pop("quota", None)
    p["skip"] = False
    p.pop("skip_reason", None)
    catalog.setdefault("meta", {})["updated"] = today()
    save_catalog(catalog)
    return {"ok": True, "provider_id": args.provider_id, "trial": trial,
            "note": "провайдер зарегистрирован в механизме выпила (trial_expiry.py)"}


PERMANENT_QUOTA_KINDS = ("free_tier_credits", "daily_quota")


def cmd_onboard_permanent(args):
    # Инвариант C2 (связка добавление↔выпил): временный тип (free_period)
    # регистрируется ТОЛЬКО через onboard-temporary с обязательным --expires.
    # Найденное независимой приёмкой (verifier, 2026-11-19): раньше
    # --quota-kind free_period пропускал временной тип без срока — провайдер
    # оставался в шлюзе навсегда. Закрыто: permanent принимает только kind'ы
    # обновляемой квоты.
    if args.quota_kind and args.quota_kind not in PERMANENT_QUOTA_KINDS:
        raise SystemExit(json.dumps({
            "ok": False,
            "error": ("quota-kind %r — тип со сроком (free_period): он регистрируется "
                      "только через onboard-temporary с обязательным --expires, "
                      "иначе провайдер останется без срока выпила" % args.quota_kind)},
            ensure_ascii=False))
    catalog = load_catalog()
    p = require_provider(catalog, args.provider_id)
    quota = p.get("quota") or {}
    quota.update({
        "kind": args.quota_kind or quota.get("kind") or "free_tier_credits",
        "registered_at": quota.get("registered_at") or today(),
        "fact": args.quota_note or quota.get("fact") or "",
        "owner_word": args.owner_word or quota.get("owner_word") or "",
        "monitor": "probe health + квотный гейт; срок не задан — выпил только по слову владельца",
    })
    p["quota"] = quota
    p.pop("trial", None)
    catalog.setdefault("meta", {})["updated"] = today()
    save_catalog(catalog)
    return {"ok": True, "provider_id": args.provider_id, "quota": quota,
            "note": "постоянная квота: авто-выпил по дате НЕ применяется"}


def cmd_reap(args):
    cmd = [sys.executable, TRIAL_EXPIRY]
    if args.apply:
        cmd.append("--apply")
    if args.owner_word:
        cmd += ["--owner-word", args.owner_word]
    if args.provider:
        cmd += ["--force-provider", args.provider]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        payload = json.loads(out.stdout)
    except json.JSONDecodeError:
        payload = {"ok": False, "raw": out.stdout[-800:], "err": out.stderr[-400:]}
    return payload


def cmd_skip(args):
    catalog = load_catalog()
    p = require_provider(catalog, args.provider_id)
    p["skip"] = True
    p["skip_reason"] = args.reason or "выключен по слову владельца"
    catalog.setdefault("meta", {})["updated"] = today()
    save_catalog(catalog)
    return {"ok": True, "provider_id": args.provider_id, "skip": True, "skip_reason": p["skip_reason"]}


def cmd_clear_skip(args):
    catalog = load_catalog()
    p = require_provider(catalog, args.provider_id)
    p["skip"] = False
    p.pop("skip_reason", None)
    catalog.setdefault("meta", {})["updated"] = today()
    save_catalog(catalog)
    return {"ok": True, "provider_id": args.provider_id, "skip": False}


def main():
    ap = argparse.ArgumentParser(description="Жизненный цикл провайдера с бесплатной квотой")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="таблица провайдеров с квотой")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("onboard-temporary", help="добавить провайдера с бесплатным ПЕРИОДОМ (срок → авто-выпил)")
    s.add_argument("provider_id")
    s.add_argument("--expires", required=True, help="дата сгорания периода YYYY-MM-DD")
    s.add_argument("--kind", default="free_period")
    s.add_argument("--on-expiry", default="delete_channels", choices=["delete_channels", "disable_channels"])
    s.add_argument("--owner-word", required=True)
    s.add_argument("--fact", default="")
    s.add_argument("--auto-reap", dest="auto_reap", action="store_true", default=None)
    s.set_defaults(fn=cmd_onboard_temporary)

    s = sub.add_parser("onboard-permanent", help="добавить провайдера с ПОСТОЯННОЙ обновляемой квотой")
    s.add_argument("provider_id")
    s.add_argument("--quota-kind", default="free_tier_credits",
                   choices=list(PERMANENT_QUOTA_KINDS))
    s.add_argument("--quota-note", default="")
    s.add_argument("--owner-word", default="")
    s.set_defaults(fn=cmd_onboard_permanent)

    s = sub.add_parser("reap", help="выпил по сроку (делегирует trial_expiry.py)")
    s.add_argument("--provider", default="")
    s.add_argument("--owner-word", default="")
    s.add_argument("--apply", action="store_true")
    s.set_defaults(fn=cmd_reap)

    s = sub.add_parser("set-skip", help="выключить провайдера (skip=true)")
    s.add_argument("provider_id")
    s.add_argument("--reason", default="")
    s.set_defaults(fn=cmd_skip)

    s = sub.add_parser("clear-skip", help="включить провайдера обратно")
    s.add_argument("provider_id")
    s.set_defaults(fn=cmd_clear_skip)

    args = ap.parse_args()
    result = args.fn(args)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
