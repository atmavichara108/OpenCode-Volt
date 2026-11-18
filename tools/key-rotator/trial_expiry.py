#!/usr/bin/env python3
"""trial_expiry — выпил провайдеров по истечении бесплатного периода.

Механизм протокола [[02-Methods/promo-provider-protocol]] (раздел «Срок
бесплатного периода → выпил»). Читает блок `trial` в
`tools/key-rotator/providers.json` и по наступившей дате выводит провайдера
из активной ротации: каналы New API удаляются (или отключаются), провайдер
помечается `skip`, в телеметрию пишется строка.

Безопасность (гейты):
  * dry-run по умолчанию — ничего не мутируется;
  * `--apply` требует `--owner-word` — слово владельца, по которому
    провайдер уходит (иначе отказ);
  * трогаются ТОЛЬКО провайдеры с явным `trial.expires` в прошлом И
    `trial.auto_reap: true` — платный/живой провайдер без блока `trial`
    неприкосновенен;
  * `trial.on_expiry: disable_channels` — каналы не удаляются, а
    отключаются (status=2), если владелец предпочитает сохранить запись.

Использование:
    python3 tools/key-rotator/trial_expiry.py                  # план (dry-run)
    python3 tools/key-rotator/trial_expiry.py --apply --owner-word "2026-11-18: выкинуть"
"""
import argparse
import datetime
import json
import os
import sqlite3
import sys

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG_PATH = os.path.join(VAULT_ROOT, "tools", "key-rotator", "providers.json")
HEALTH_LOG = os.path.join(VAULT_ROOT, "control-plane", "telemetry", "provider-health.jsonl")
NEWAPI_DB = os.path.expanduser("~/.local/share/newapi/one-api.db")


def today() -> str:
    return datetime.date.today().isoformat()


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_catalog(catalog):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")


def evaluate(catalog, now=None):
    """Разбор каталога → список решений по провайдерам с блоком trial."""
    now = now or today()
    decisions = []
    for pid, pconf in (catalog.get("providers") or {}).items():
        trial = pconf.get("trial")
        if not trial:
            continue
        expires = trial.get("expires") or ""
        expired = bool(expires) and expires < now
        decisions.append({
            "provider_id": pid,
            "expires": expires,
            "kind": trial.get("kind") or "free_period",
            "auto_reap": bool(trial.get("auto_reap")),
            "on_expiry": trial.get("on_expiry") or "delete_channels",
            "owner_word": trial.get("owner_word") or "",
            "expired": expired,
            "days_overdue": (datetime.date.fromisoformat(now) - datetime.date.fromisoformat(expires)).days if expired else 0,
            "skip": bool(pconf.get("skip")),
        })
    return decisions


def channels_of(provider_id):
    """Каналы New API провайдера (если БД доступна)."""
    if not os.path.exists(NEWAPI_DB):
        return []
    con = sqlite3.connect(NEWAPI_DB)
    try:
        cur = con.cursor()
        cur.execute("SELECT id, name FROM channels WHERE name LIKE ?", (provider_id + "|%",))
        return cur.fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()


def reap(provider_id, mode="delete_channels"):
    """Убирает каналы провайдера из шлюза. Возвращает (n_deleted, n_disabled)."""
    if not os.path.exists(NEWAPI_DB):
        return 0, 0
    con = sqlite3.connect(NEWAPI_DB)
    try:
        cur = con.cursor()
        cur.execute("SELECT id FROM channels WHERE name LIKE ?", (provider_id + "|%",))
        ids = [r[0] for r in cur.fetchall()]
        deleted = disabled = 0
        for cid in ids:
            cur.execute("DELETE FROM abilities WHERE channel_id=?", (cid,))
            if mode == "disable_channels":
                cur.execute("UPDATE channels SET status=2 WHERE id=?", (cid,))
                disabled += 1
            else:
                cur.execute("DELETE FROM channels WHERE id=?", (cid,))
                deleted += 1
        con.commit()
        return deleted, disabled
    finally:
        con.close()


def log_health(provider_id, mode, deleted, disabled, owner_word):
    row = {
        "ts": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "provider_id": provider_id,
        "status": "SKIPPED",
        "models_count": 0,
        "usable_balance": None,
        "balance_kind": None,
        "warnings": ["trial_expired"],
        "latency_ms": None,
        "redacted": True,
        "source": "trial_expiry",
        "detail": "free period expired; on_expiry=%s; channels_deleted=%d; channels_disabled=%d; owner_word=%s" % (mode, deleted, disabled, owner_word),
    }
    os.makedirs(os.path.dirname(HEALTH_LOG), exist_ok=True)
    with open(HEALTH_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Выпил провайдеров по истечении бесплатного периода")
    ap.add_argument("--apply", action="store_true", help="применить (иначе dry-run план)")
    ap.add_argument("--owner-word", default="", help="слово владельца, по которому провайдер уходит")
    ap.add_argument("--provider", action="append", default=[], help="только эти провайдеры")
    ap.add_argument("--force-provider", action="append", default=[],
                    help="выпилить по прямому слову владельца, независимо от даты (нужен --owner-word)")
    ap.add_argument("--quiet", action="store_true", help="только итоговая строка JSON")
    args = ap.parse_args()

    catalog = load_catalog()
    decisions = evaluate(catalog)
    if args.provider:
        decisions = [d for d in decisions if d["provider_id"] in set(args.provider)]

    forced = set(args.force_provider)
    plan = []
    for d in decisions:
        chans = channels_of(d["provider_id"])
        action = "keep"
        if d["provider_id"] in forced:
            # прямое слово владельца на выпил — дата не обязательна
            action = d["on_expiry"] if not d["skip"] else "already_reaped"
            d["forced"] = True
        elif d["expired"] and d["auto_reap"] and not d["skip"]:
            action = d["on_expiry"]
        elif d["expired"] and d["auto_reap"] and d["skip"]:
            action = "already_reaped"
        elif d["expired"]:
            action = "expired_no_autoreap"
        plan.append({**d, "channels": len(chans), "action": action,
                     "channel_names": [c[1] for c in chans][:20]})

    if not args.apply:
        out = {"ok": True, "mode": "dry-run", "today": today(), "plan": plan}
        print(json.dumps(out, ensure_ascii=False, indent=1) if not args.quiet else json.dumps({"ok": True, "mode": "dry-run", "actions": sum(1 for p in plan if p["action"] not in ("keep", "already_reaped", "expired_no_autoreap"))}, ensure_ascii=False))
        return 0

    if not args.owner_word:
        print(json.dumps({"ok": False, "error": "для --apply нужно --owner-word (слово владельца на выпил)"}, ensure_ascii=False))
        return 2

    applied = []
    for p in plan:
        if p["action"] not in ("delete_channels", "disable_channels"):
            continue
        deleted, disabled = reap(p["provider_id"], p["action"])
        pconf = catalog["providers"][p["provider_id"]]
        pconf["skip"] = True
        pconf["skip_reason"] = "free period expired %s (%s)" % (p["expires"], args.owner_word)
        trial = pconf.setdefault("trial", {})
        trial["auto_reap"] = False
        trial["reaped_at"] = today()
        trial["reaped_by"] = args.owner_word
        log_health(p["provider_id"], p["action"], deleted, disabled, args.owner_word)
        applied.append({**p, "deleted": deleted, "disabled": disabled})

    if applied:
        catalog.setdefault("meta", {})["updated"] = today()
        save_catalog(catalog)

    out = {"ok": True, "mode": "apply", "today": today(), "applied": applied,
           "skipped": [p for p in plan if p["action"] not in ("delete_channels", "disable_channels")]}
    print(json.dumps(out, ensure_ascii=False, indent=1) if not args.quiet else json.dumps({"ok": True, "applied": len(applied)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
