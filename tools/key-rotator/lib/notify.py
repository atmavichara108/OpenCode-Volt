"""Ненавязчивые push-уведомления (ntfy) — транспорт CURL, не urllib.

urllib запрещён брифом key-rotator (Cloudflare 1010 режет urllib по отпечатку).
Без топика уведомление МОЛЧА пропускается (skipped), не ошибка — ротация
должна работать и без настроенных пушей.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import http_client

DEFAULT_HOST = "https://ntfy.sh"


def send(message, *, topic=None, priority="default", title="Key Rotator",
         timeout=6):
    topic = topic or os.environ.get("PIPBOY_NTFY", "")
    if not topic:
        return {"ok": False, "skipped": "no_topic"}
    host = os.environ.get("PIPBOY_NTFY_HOST") or DEFAULT_HOST
    url = f"{host.rstrip('/')}/{topic}"
    resp = http_client.single_request(
        "POST", url,
        headers={
            "Title": title,
            "Priority": priority or "default",
            "Content-Type": "text/plain; charset=utf-8",
            "Tags": "arrows_counterclockwise",
        },
        body=message if isinstance(message, str) else str(message),
        timeout=timeout,
    )
    ok = bool(resp.get("ok")) and resp.get("status") is not None and 200 <= resp["status"] < 300
    if ok:
        body = (resp.get("body") or "").strip()
        return {"ok": True, "topic": topic, "status": resp["status"],
                "id": body.splitlines()[-1] if body else ""}
    return {"ok": False, "error": resp.get("error") or f"HTTP {resp.get('status')}"}


def format_switch(agent, scope, project, old_model, new_model, reason,
                  dry_run=False):
    """Короткий текст уведомления о смене модели."""
    head = "Ротация (dry-run)" if dry_run else "Ротация"
    where = f"{scope}:{agent}" + (f"@{project}" if project else "")
    return f"{head}: {where} — {old_model} → {new_model} ({reason})"
