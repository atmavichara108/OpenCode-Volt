#!/usr/bin/env python3
"""Pip-Boy actions — серверные действия по командам из Pip-Boy.

Браузер не может сам поднимать tmux/nvim/браузер, поэтому действия исполняет
этот маленький CLI (stdlib, без зависимостей). pipboy.py пробрасывает их через
безопасный /action endpoint (whitelist в Handler.do_ACTION).

Команды:
  workspace-open <project> [--no-term] [--windows LIST]
      открыть/создать tmux-сессию pb-<project> с окнами main/files/tests/
      logs/local; --no-term = только создать detached (тест/сервер), без
      alacritty attach.
  workspace-status <project>
      JSON: есть ли tmux-сессия, окна, docker контейнеры (если PIPBOY_DOCKER=1),
      локальные порты.
  link-open <target> [--mode nvim|browser|tmux]
      резолв и открытие wikilink/пути/URL. nvim = alacritty -e nvim,
      browser = xdg-open, tmux = новый tmux-окно (cd в каталог файла).

Контракт вывода: одна строка JSON {"ok": true, ...} или {"ok": false, "error": ...}.
Exit code 0/1. Все внешние запуски — stdlib subprocess.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
SERVE_DIR = Path(__file__).resolve().parent

DEFAULT_TERM = "alacritty"
DEFAULT_WINDOWS = "main,files,tests,logs,local"

# известные проекту порты (id -> [(порт, имя)]). Расширяется здесь/в registry.
PROJECT_PORTS = {
    "SERPlux": [(8000, "API"), (5173, "preview")],
    "vault": [(8123, "pip-boy")],
}


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """subprocess.run с обрезанным env (без AppImage-маунтов в LD_LIBRARY_PATH)."""
    env = dict(os.environ)
    if "LD_LIBRARY_PATH" in env:
        env["LD_LIBRARY_PATH"] = ":".join(
            p for p in env["LD_LIBRARY_PATH"].split(":") if ".mount_" not in p
        )
    kw.setdefault("env", env)
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    return subprocess.run(cmd, **kw)


def spawn(cmd: list[str]) -> None:
    """Fire-and-forget запуск GUI-процесса: не блокирует сервер (иначе запуск
    alacritty/nvim повисает, пока окно открыто). Детей чистим от AppImage-маунтов."""
    env = dict(os.environ)
    if "LD_LIBRARY_PATH" in env:
        env["LD_LIBRARY_PATH"] = ":".join(
            p for p in env["LD_LIBRARY_PATH"].split(":") if ".mount_" not in p
        )
    subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def tmux(args: list[str]) -> subprocess.CompletedProcess:
    return run(["tmux", *args])


def term() -> str:
    return os.environ.get("PIPBOY_TERM") or shutil.which(DEFAULT_TERM) or DEFAULT_TERM


def which_exe(name: str) -> str | None:
    return shutil.which(name)


def session_name(project: str) -> str:
    # tmux-сессия: pb-<project>, безопасные символы
    safe = "".join(c if c.isalnum() else "-" for c in project).strip("-")[:40]
    return f"pb-{safe}"


def project_repo(project: str) -> Path | None:
    """repo карточки проекта из observer-снимка (03-Projects)."""
    snap = SERVE_DIR / "generated" / "snapshot.json"
    if snap.exists():
        try:
            data = json.loads(snap.read_text(encoding="utf-8"))
            for p in data.get("projects", []):
                if p.get("id") == project and p.get("repo"):
                    path = Path(p["repo"]).expanduser()
                    if path.is_dir():
                        return path
        except (OSError, json.JSONDecodeError):
            pass
    # fallback: 03-Projects frontmatter
    cards = VAULT_ROOT / "03-Projects"
    for md in cards.glob("*.md") if cards.is_dir() else []:
        text = md.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip() == f"repo: {project}":
                # repo — путь в другом поле, упрощённо ищем repo: <path> по id файла
                pass
    return None


def _repo_from_card(project: str) -> Path | None:
    cards = VAULT_ROOT / "03-Projects"
    if not cards.is_dir():
        return None
    for md in sorted(cards.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        if f"title: {project}" in text or md.stem == project:
            for line in text.splitlines():
                if line.startswith("repo:"):
                    val = line.split(":", 1)[1].strip().strip("'\"")
                    if val:
                        path = Path(val).expanduser()
                        if path.is_dir():
                            return path
    return None


def repo_for(project: str) -> Path | None:
    return project_repo(project) or _repo_from_card(project)


def windows_arg(project: str) -> list[str]:
    """Окна по умолчанию: main(workdir=repo) + files(nvim) + tests/logs/local."""
    repo = repo_for(project)
    cwd = str(repo) if repo else str(VAULT_ROOT)
    return [
        f"main:{cwd}",     # OpenCode/терминал
        f"files:{cwd}",    # nvim
        f"tests:{cwd}",
        f"logs:{cwd}",
        f"local:{cwd}",
    ]


def do_workspace_open(project: str, no_term: bool) -> dict:
    if not which_exe("tmux"):
        return {"ok": False, "error": "tmux не найден в PATH"}
    name = session_name(project)
    repo = repo_for(project)
    if not repo:
        return {"ok": False, "error": f"repo проекта '{project}' не найден (нет карточки с repo=/путь к каталогу)"}

    exists = tmux(["has-session", "-t", name]).returncode == 0
    wins: list[str] = []
    if not exists:
        wins = windows_arg(project)
        # создать detached: window 0 = main (workdir), последующие = окна
        first = wins[0].split(":", 1)
        wname, wdir = first[0], first[1] if ":" in wins[0] else str(VAULT_ROOT)
        r = run(["tmux", "new-session", "-d", "-s", name, "-n", wname, "-c", wdir])
        if r.returncode != 0:
            return {"ok": False, "error": f"tmux new-session: {r.stderr.strip()}"}
        for w in wins[1:]:
            wn, wd = (w.split(":", 1) + [str(VAULT_ROOT)])[0:2]
            tmux(["new-window", "-t", name, "-n", wn, "-c", wd])
        # files-окно — nvim
        if which_exe("nvim"):
            tmux(["send-keys", "-t", f"{name}:files", "nvim", "Enter"])
    final_wins = [w.split(":", 1)[0] for w in wins] if not exists else _session_windows(name)

    if no_term:
        return {"ok": True, "session": name, "project": project, "repo": str(repo or ""),
                "windows": final_wins, "detached": True}

    # attach в терминале (fire-and-forget: терминал живёт своей жизнью)
    t = term()
    spawn([t, "-e", "tmux", "attach-session", "-t", name])
    return {"ok": True, "session": name, "project": project, "repo": str(repo or ""),
            "windows": _session_windows(name)}


def _session_windows(name: str) -> list[str]:
    r = tmux(["list-windows", "-t", name, "-F", "#{window_name}"])
    if r.returncode != 0:
        return []
    return [w.strip() for w in r.stdout.splitlines() if w.strip()]


def _docker_containers(repo: Path | None) -> list[str]:
    if os.environ.get("PIPBOY_DOCKER") != "1":
        return []
    if not which_exe("docker"):
        return []
    try:
        args = ["docker", "ps", "--format", "{{.Names}} {{.Status}} {{.Ports}}"]
        if repo:
            # ограничить по compose-каталогу не просто; пока все
            pass
        r = run(args, timeout=4)
        if r.returncode == 0:
            return [l.strip() for l in r.stdout.splitlines() if l.strip()]
    except (subprocess.TimeoutExpired, OSError):
        pass
    return []


def _port_health(port: int) -> bool:
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def do_workspace_status(project: str) -> dict:
    name = session_name(project)
    exists = which_exe("tmux") and tmux(["has-session", "-t", name]).returncode == 0
    repo = repo_for(project)
    windows = _session_windows(name) if exists else []
    ports = []
    for port, label in PROJECT_PORTS.get(project, []):
        ports.append({"port": port, "label": label, "healthy": _port_health(port)})
    return {
        "ok": True, "project": project, "session": name, "tmux_running": exists,
        "windows": windows, "repo": str(repo or ""),
        "ports": ports,
        "docker": _docker_containers(repo),
        "docker_enabled": os.environ.get("PIPBOY_DOCKER") == "1",
    }


def do_capture_scan(regen: bool, limit: int) -> dict:
    """Отдаёт intake-сигналы из signals.json (read-only ключ к входам capture).

    signals.json — артефакт tools/telegram-capture/pipeline.py. Если файла нет
    или передан --run, дёргаем pipeline (--dry-run) и читаем его stdout —
    но НЕ трогаем captures_all.json и НЕ проставляем реакции.
    """
    pipe = VAULT_ROOT / "tools" / "telegram-capture" / "pipeline.py"
    if not pipe.exists():
        return {"ok": False, "error": "pipeline.py не найден в tools/telegram-capture/"}

    if regen:
        # --dry-run: pipeline печатает только JSON в stdout, ничего не пишет
        r = run(["python3", str(pipe), "--dry-run"], timeout=60)
        if r.returncode != 0:
            return {"ok": False, "error": f"pipeline exit {r.returncode}: {(r.stderr or '').strip()[:200]}"}
        try:
            dat = json.loads(r.stdout.strip() or "{}")
        except json.JSONDecodeError:
            return {"ok": False, "error": "pipeline: не-JSON вывод"}
    else:
        sig = VAULT_ROOT / "tools" / "telegram-capture" / "signals.json"
        if not sig.exists():
            return {"ok": False, "error": "signals.json отсутствует — передай --run или запусти pipeline.py вручную"}
        try:
            dat = json.loads(sig.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            return {"ok": False, "error": f"не читается signals.json: {e}"}

    meta = dat.get("meta") or {}
    sigs = dat.get("signals") or []
    return {
        "ok": True,
        "digest": meta.get("input_digest", "")[:12],
        "total_posts": meta.get("total_posts", 0),
        "total_signals": meta.get("total_signals", len(sigs)),
        "projects": dat.get("projects") or {},
        "signals": sigs[:limit],
        "truncated": len(sigs) > limit,
    }


# --- link resolver ---------------------------------------------------------

def classify(target: str) -> str:
    t = target.strip()
    if t.startswith("http://") or t.startswith("https://"):
        return "url"
    if t.startswith("localhost") or t.startswith("127.0.0.1"):
        return "url"
    if t.startswith("[["):
        return "wikilink"
    if t.startswith("/") or t.startswith("~/") or t.startswith("~"):
        return "path"
    return "path"


def resolve_wikilink(link: str) -> Path | None:
    """[[name]] -> файл в vault. Имя может быть путём от корня vault или словом."""
    inner = link.strip().strip("[").strip("]").strip()
    if not inner:
        return None
    # 1) прямой путь от vault
    direct = (VAULT_ROOT / inner).resolve()
    if direct.exists() and direct.is_file():
        return direct
    if direct.is_dir():
        return direct
    # 2) путь без расширения
    if direct.with_suffix(".md").exists() or direct.suffix == "":
        withmd = (VAULT_ROOT / (inner if inner.endswith(".md") else inner + ".md")).resolve()
        if withmd.exists():
            return withmd
    # 3) поиск по имени (stem) во всём vault, кроме node_modules/.git/venv
    stem = Path(inner).stem.lower()
    skip = {".git", ".venv", "node_modules", "__pycache__"}
    for p in VAULT_ROOT.rglob("*.md"):
        if any(s in p.parts for s in skip):
            continue
        if p.stem.lower() == stem or p.name.lower() == inner.lower():
            return p
    return None


def do_link_open(target: str, mode: str) -> dict:
    kind = classify(target)
    if kind == "wikilink":
        path = resolve_wikilink(target)
        if not path:
            return {"ok": False, "error": f"wikilink не резолвится: {target}"}
        return open_path(str(path), mode)
    if kind == "url":
        return open_url(target, mode)
    # path
    path = str(Path(target).expanduser())
    return open_path(path, mode)


def do_link_resolve(target: str) -> dict:
    """Резолв без открытия: что это и куда ведёт (для предпросмотра в LinkModule)."""
    kind = classify(target)
    if kind == "wikilink":
        path = resolve_wikilink(target)
        return {"ok": True, "kind": kind, "target": target,
                "resolved": str(path) if path else None,
                "exists": bool(path)}
    if kind == "url":
        return {"ok": True, "kind": kind, "target": target, "resolved": target, "exists": True}
    p = Path(target).expanduser()
    return {"ok": True, "kind": kind, "target": target,
            "resolved": str(p), "exists": p.exists()}


def open_url(url: str, mode: str) -> dict:
    if mode in ("browser", ""):
        spawn(["xdg-open", url])
        return {"ok": True, "opened": url, "mode": "browser"}
    return {"ok": False, "error": f"URL открывается только в браузере (mode={mode})"}


def open_path(path: str, mode: str) -> dict:
    p = Path(path)
    if mode == "nvim":
        if not which_exe("nvim"):
            return {"ok": False, "error": "nvim не найден"}
        t = term()
        spawn([t, "-e", "nvim", str(p)])
        return {"ok": True, "opened": str(p), "mode": "nvim"}
    if mode == "tmux":
        if not which_exe("tmux"):
            return {"ok": False, "error": "tmux не найден"}
        cwd = str(p.parent if p.is_file() else p)
        target = "pb-vault" if tmux(["has-session", "-t", "pb-vault"]).returncode == 0 else None
        if target:
            tmux(["new-window", "-t", target, "-c", cwd])
        else:
            tmux(["new-session", "-d", "-s", "pb-vault", "-c", cwd])
            t = term()
            spawn([t, "-e", "tmux", "attach-session", "-t", "pb-vault"])
        return {"ok": True, "opened": str(p), "mode": "tmux"}
    # default: browser (xdg-open умеет каталоги и файлы)
    spawn(["xdg-open", str(p)])
    return {"ok": True, "opened": str(p), "mode": "browser"}


# --- ecosystem read-only queries (custom tools backend) --------------------

LIFECYCLE_ORDER = [
    "IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD",
    "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED",
]
PRIORITY_ORDER = ["P0", "P1", "P2", "P3", "P4"]


def _load_ecosystem() -> dict:
    """Читает canonical registry.json + generated/snapshot.json (read-only)."""
    reg_path = SERVE_DIR / "registry.json"
    snap_path = SERVE_DIR / "generated" / "snapshot.json"
    reg = {}
    snap = {}
    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    try:
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return {"registry": reg, "snapshot": snap}


def _frozen_tasks(card: dict, snap: dict) -> list[str]:
    blocked = set(snap.get("tasks", {}).get("Blocked", []))
    frozen = set(snap.get("tasks", {}).get("Frozen", []))
    return [t for t in card.get("tasks", []) if t in blocked or t in frozen]


def _dep_ok(card: dict, cards: dict, stage: str | None = None) -> tuple[bool, list[str]]:
    """depends_on закрыты для стадии карточки (или для заданной target-стадии)."""
    lifecycle = stage or card.get("lifecycle", "IDEA")
    need = 0
    if lifecycle in ("IDEA", "RESEARCH"):
        need = 0
    elif lifecycle == "DESIGN":
        need = LIFECYCLE_ORDER.index("DESIGN")
    else:
        need = LIFECYCLE_ORDER.index("APPROVED")
    bad = []
    for d in card.get("depends_on", []):
        dc = cards.get(d)
        if not dc:
            bad.append(f"{d} (нет в registry)")
            continue
        dl = dc.get("lifecycle", "IDEA")
        if dc.get("retired") or dl == "RETIRED":
            bad.append(f"{d} (RETIRED)")
            continue
        if LIFECYCLE_ORDER.index(dl) < need:
            bad.append(f"{d} ({dl})")
    return (len(bad) == 0), bad


def _readiness(cid: str, card: dict, cards: dict, snap: dict) -> dict:
    """nextInfo-эквивалент (READY/blocked/verify/flight/done). No silent mutation."""
    if card.get("retired") or card.get("lifecycle") == "RETIRED":
        return {"state": "done", "reasons": []}
    ok, bad_deps = _dep_ok(card, cards)
    reasons = []
    if not ok:
        reasons.append("deps: " + ", ".join(bad_deps))
    for t in _frozen_tasks(card, snap):
        reasons.append(f"frozen: {t}")
    if "BLOCKED" in (card.get("status_note") or "").upper():
        reasons.append("status_note: BLOCKED")
    lc = card.get("lifecycle", "IDEA")
    if lc in ("LIVE", "OBSERVE", "IMPROVE"):
        return {"state": "done", "reasons": []}
    if lc in ("BUILD", "REVIEW"):
        state = "blocked" if reasons else "flight"
    elif lc == "VERIFY":
        state = "blocked" if reasons else "verify"
    elif lc in ("APPROVED", "DESIGN", "RESEARCH", "IDEA"):
        state = "blocked" if reasons else "ready"
    else:
        state = "blocked" if reasons else "ready"
    return {"state": state, "reasons": reasons, "next": lc, "priority": card.get("priority", ""),
            "project": card.get("project") or "", "owner": card.get("owner", ""), "title": card.get("title", "")}


def do_query(q: str, facet: str, project: str) -> dict:
    eco = _load_ecosystem()
    cards = eco["registry"].get("cards", {})
    ql = (q or "").lower()
    out = []
    for cid, c in cards.items():
        hay = " ".join([cid, c.get("title", ""), c.get("owner", ""),
                        c.get("lifecycle", ""), c.get("layer", ""),
                        c.get("project") or "", " ".join(c.get("facets", [])),
                        c.get("priority", ""), c.get("status_note", "")]).lower()
        if ql and ql not in hay:
            continue
        if facet and facet not in c.get("facets", []):
            continue
        if project and (c.get("project") or "") != project:
            continue
        out.append({"id": cid, "title": c.get("title", ""), "lifecycle": c.get("lifecycle", ""),
                    "owner": c.get("owner", ""), "priority": c.get("priority", ""),
                    "project": c.get("project") or "", "layer": c.get("layer", ""),
                    "facets": c.get("facets", [])})
    return {"ok": True, "count": len(out), "cards": out}


def do_blockers() -> dict:
    eco = _load_ecosystem()
    cards = eco["registry"].get("cards", {})
    snap = eco["snapshot"]
    blocked_cards = []
    for cid, c in cards.items():
        r = _readiness(cid, c, cards, snap)
        if r["state"] == "blocked":
            blocked_cards.append({"id": cid, "title": c.get("title", ""),
                                  "reasons": r["reasons"]})
    drift = [{"type": s.get("type"), "subject": s.get("subject"), "detail": s.get("detail")}
             for s in snap.get("drift_signals", [])]
    frozen_by_task = {}
    blocked_tasks = set(snap.get("tasks", {}).get("Blocked", [])) | set(snap.get("tasks", {}).get("Frozen", []))
    for cid, c in cards.items():
        for t in c.get("tasks", []):
            if t in blocked_tasks:
                frozen_by_task.setdefault(t, []).append(cid)
    return {"ok": True, "blocked_cards": blocked_cards, "drift_signals": drift,
            "frozen_tasks": [{"task": t, "cards": cards} for t, cards in sorted(frozen_by_task.items())]}


def do_next(limit: int) -> dict:
    eco = _load_ecosystem()
    cards = eco["registry"].get("cards", {})
    snap = eco["snapshot"]
    rows = []
    for cid, c in cards.items():
        r = _readiness(cid, c, cards, snap)
        rows.append({"id": cid, **r})
    ready = sorted([r for r in rows if r["state"] == "ready"],
                   key=lambda r: (PRIORITY_ORDER.index(r["priority"]) if r["priority"] in PRIORITY_ORDER else 9, r["id"]))
    blocked = sorted([r for r in rows if r["state"] == "blocked"],
                     key=lambda r: (PRIORITY_ORDER.index(r["priority"]) if r["priority"] in PRIORITY_ORDER else 9, r["id"]))
    verify = [r for r in rows if r["state"] == "verify"]
    flight = [r for r in rows if r["state"] == "flight"]
    return {"ok": True,
            "ready": ready[:limit],
            "blocked": blocked[:limit],
            "verify": verify,
            "in_flight": flight,
            "counts": {"ready": len(ready), "blocked": len(blocked),
                       "verify": len(verify), "in_flight": len(flight)}}


# --- proposal queue (алгоритмический ecosystem observer + apply) -----------

NEXT_STAGE = {
    "IDEA": "RESEARCH",
    "RESEARCH": "DESIGN",
    "DESIGN": "APPROVED",
    "APPROVED": "BUILD",
    "BUILD": "REVIEW",
    "REVIEW": "VERIFY",
    "VERIFY": "LIVE",
}

PROPOSALS_LOG = SERVE_DIR / "generated" / "proposals-applied.jsonl"


def _proposal_id(kind: str, card_id: str) -> str:
    return f"{kind}:{card_id}"


def do_proposals() -> dict:
    """Генерирует предложения (read-only) — ничего не применяет.

    Типы:
      transition — карточка готова перейти на следующую стадию (deps closed)
      blocked    — карточка заблокирована (deps/frozen/status_note)
      no_owner   — карточка без owner (не retired)
      drift      — сигнал drift из snapshot
    """
    eco = _load_ecosystem()
    cards = eco["registry"].get("cards", {})
    snap = eco["snapshot"]
    proposals = []

    for cid, c in cards.items():
        if c.get("retired") or c.get("lifecycle") == "RETIRED":
            continue
        lc = c.get("lifecycle", "IDEA")
        r = _readiness(cid, c, cards, snap)
        nxt = NEXT_STAGE.get(lc)
        if nxt and r["state"] == "ready":
            # deps должны быть закрыты уже для целевой стадии (не только текущей)
            ok_target, _ = _dep_ok(c, cards, stage=nxt)
            if not ok_target:
                continue
            proposals.append({
                "id": _proposal_id("transition", cid),
                "type": "transition", "card": cid,
                "from": lc, "to": nxt,
                "title": c.get("title", ""),
                "priority": c.get("priority", ""),
                "project": c.get("project") or "",
                "owner": c.get("owner", ""),
                "reason": "dependencies satisfied",
            })
        elif r["state"] == "blocked":
            proposals.append({
                "id": _proposal_id("blocked", cid),
                "type": "blocked", "card": cid,
                "title": c.get("title", ""),
                "lifecycle": lc,
                "reasons": r["reasons"],
            })
        if not c.get("owner"):
            proposals.append({
                "id": _proposal_id("no_owner", cid),
                "type": "no_owner", "card": cid,
                "title": c.get("title", ""),
                "lifecycle": lc,
            })

    for s in snap.get("drift_signals", []):
        proposals.append({
            "id": f"drift:{s.get('subject', '')}",
            "type": "drift",
            "subject": s.get("subject", ""),
            "detail": s.get("detail", ""),
            "kind": s.get("type", ""),
        })

    # порядок: transitions по приоритету, затем blocked, no_owner, drift
    order = {"transition": 0, "blocked": 1, "no_owner": 2, "drift": 3}
    proposals.sort(key=lambda p: (order.get(p["type"], 9), p.get("priority", "P9"), p.get("card", "")))
    return {"ok": True, "proposals": proposals,
            "counts": {t: sum(1 for p in proposals if p["type"] == t)
                       for t in ("transition", "blocked", "no_owner", "drift")}}


def _apply_transition(card_id: str, target: str) -> dict:
    import re

    reg_path = SERVE_DIR / "registry.json"
    try:
        text = reg_path.read_text(encoding="utf-8")
        reg = json.loads(text)
    except (OSError, json.JSONDecodeError) as e:
        return {"ok": False, "error": f"registry: {e}"}
    cards = reg.get("cards", {})
    card = cards.get(card_id)
    if not card:
        return {"ok": False, "error": f"нет карточки {card_id}"}
    if card.get("retired") or card.get("lifecycle") == "RETIRED":
        return {"ok": False, "error": f"{card_id} retired — переходы запрещены"}
    lc = card.get("lifecycle", "IDEA")
    expected = NEXT_STAGE.get(lc)
    if target != expected:
        return {"ok": False, "error": f"{card_id}: {lc} → {target} недопустимо (ожидалось {expected or 'terminal'})"}
    # deps должны быть закрыты для целевой стадии
    eco = _load_ecosystem()
    ok_deps, bad = _dep_ok(card, eco["registry"].get("cards", {}), stage=target)
    if not ok_deps:
        return {"ok": False, "error": f"{card_id}: deps не закрыты: {', '.join(bad)}"}

    # хирургическая правка текста (не json round-trip — сохраняет формат файла)
    m = re.search(rf'("{re.escape(card_id)}"\s*:\s*\{{.*?"lifecycle"\s*:\s*)"[A-Z]+"', text, re.DOTALL)
    if not m:
        return {"ok": False, "error": f"{card_id}: не найден lifecycle в registry.json"}
    text = text[:m.end(1)] + f'"{target}"' + text[m.end():]
    # обновить meta.updated
    today = time.strftime("%Y-%m-%d")
    text = re.sub(r'("updated"\s*:\s*)"[0-9-]+"', rf'\1"{today}"', text, count=1)
    tmp = reg_path.with_suffix(".json.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(reg_path)

    # audit log
    try:
        os.makedirs(PROPOSALS_LOG.parent, exist_ok=True)
        with open(PROPOSALS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "card": card_id,
                                "from": lc, "to": target}, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return {"ok": True, "card": card_id, "from": lc, "to": target, "applied": True}


def do_apply(card_id: str, target: str) -> dict:
    """Применить предложение (явное действие пользователя, не silent)."""
    if not card_id or not target:
        return {"ok": False, "error": "нужны card и target"}
    return _apply_transition(card_id, target)


def do_dependencies(card_id: str) -> dict:
    eco = _load_ecosystem()
    cards = eco["registry"].get("cards", {})
    blocks = {}
    for cid, c in cards.items():
        for d in c.get("depends_on", []):
            blocks.setdefault(d, []).append(cid)
    # transitive blockers (критический путь)
    def transitive(start: str) -> set[str]:
        seen = set()
        stack = list(blocks.get(start, []))
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(blocks.get(x, []))
        return seen
    ranked = sorted(
        ({cid: transitive(cid) for cid in cards if _is_blocking(cid, cards)}).items(),
        key=lambda kv: (-len(kv[1]), kv[0]))
    ranked = [{"id": cid, "holds": len(s), "blocked": sorted(s)} for cid, s in ranked if s]
    def entry(cid):
        c = cards.get(cid)
        if not c:
            return {"id": cid, "error": "нет в registry"}
        return {"id": cid, "title": c.get("title", ""), "lifecycle": c.get("lifecycle", ""),
                "owner": c.get("owner", ""), "priority": c.get("priority", ""),
                "depends_on": c.get("depends_on", []),
                "blocks": sorted(blocks.get(cid, []))}
    graph_nodes = [{"id": cid, "title": cards[cid].get("title", ""),
                    "lifecycle": cards[cid].get("lifecycle", ""),
                    "owner": cards[cid].get("owner", ""),
                    "depends_on": cards[cid].get("depends_on", [])} for cid in cards]
    graph_edges = [{"source": d, "target": cid} for cid, c in cards.items()
                   for d in c.get("depends_on", []) if d in cards]
    return {"ok": True,
            "card": entry(card_id) if card_id else None,
            "critical_path": ranked[:10],
            "orphans": [cid for cid, c in cards.items()
                        if not c.get("depends_on") and not blocks.get(cid)],
            "no_owner": [cid for cid, c in cards.items()
                         if not c.get("owner") and not c.get("retired")],
            "nodes": graph_nodes,
            "edges": graph_edges,
            "cards": {cid: entry(cid) for cid in (cards if not card_id else [card_id])}
            if card_id else None}


def _is_blocking(cid: str, cards: dict) -> bool:
    c = cards.get(cid, {})
    if c.get("retired") or c.get("lifecycle") == "RETIRED":
        return False
    return c.get("lifecycle") in ("IDEA", "RESEARCH", "DESIGN", "APPROVED")


def term_port(project: str) -> int:
    """Детерминированный порт termproxy для проекта (диапазон 8200..8599)."""
    h = 0
    for ch in project:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return 8200 + (h % 400)


def termproxy_alive(port: int) -> bool:
    return _port_health(port)


def do_term_open(project: str, port: int | None = None) -> dict:
    """Запустить termproxy для проекта (idempotent).

    Если termproxy на порту уже жив — просто вернуть порт. Иначе поднять.
    Порт детерминирован от имени проекта (term_port), если не передан явно.
    """
    port = port or term_port(project)
    if termproxy_alive(port):
        return {"ok": True, "project": project, "port": port, "alive": True}
    termproxy = SERVE_DIR / "termproxy.py"
    if not termproxy.exists():
        return {"ok": False, "error": "termproxy.py не найден"}
    repo = repo_for(project)
    cwd = str(repo) if repo else str(VAULT_ROOT)
    env = dict(os.environ)
    if "LD_LIBRARY_PATH" in env:
        env["LD_LIBRARY_PATH"] = ":".join(
            p for p in env["LD_LIBRARY_PATH"].split(":") if ".mount_" not in p
        )
    python_exe = shutil.which("python3") or shutil.which("python") or sys.executable
    subprocess.Popen(
        [python_exe, str(termproxy), "serve", "--port", str(port), "--cwd", cwd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True, close_fds=True, env=env,
    )
    return {"ok": True, "project": project, "port": port, "alive": False,
            "cwd": cwd}


def do_term_status(project: str) -> dict:
    port = term_port(project)
    return {"ok": True, "project": project, "port": port,
            "alive": termproxy_alive(port)}


def do_term_close(project: str) -> dict:
    """Погасить termproxy проекта: /shutdown HTTP, затем pidfile-фолбэк."""
    port = term_port(project)
    # 1) graceful: /shutdown эндпоинт (не зависит от pidfile, работает и для старых)
    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/shutdown", timeout=3) as r:
            return {"ok": True, "project": project, "port": port,
                    "method": "shutdown", "status": r.status}
    except OSError:
        pass  # уже мёртв или не поднят
    # 2) fallback: pidfile + SIGTERM
    termproxy = SERVE_DIR / "termproxy.py"
    if not termproxy.exists():
        return {"ok": False, "error": "termproxy.py не найден"}
    python_exe = shutil.which("python3") or shutil.which("python") or sys.executable
    r = run([python_exe, str(termproxy), "stop", "--port", str(port)], timeout=10)
    if r.returncode != 0:
        return {"ok": False, "error": f"termproxy stop: {(r.stderr or '').strip()[:200]}"}
    try:
        body = json.loads(r.stdout.strip() or "{}")
    except json.JSONDecodeError:
        body = {"ok": False, "error": "termproxy stop: не-JSON вывод"}
    if not body.get("ok") and "нет pidfile" in str(body.get("error", "")):
        body = {"ok": True, "port": port, "already_dead": True}
    body["project"] = project
    return body


def do_notify(message: str, topic: str, priority: str) -> dict:
    """Отправить push на телефон через ntfy.sh (self-hosted-совместимо).

    Топик из --topic или env PIPBOY_NTFY. Хост из PIPBOY_NTFY_HOST
    (default https://ntfy.sh). Без топика — инструкция, а не ошибка сети.
    """
    t = topic or os.environ.get("PIPBOY_NTFY", "")
    if not t:
        return {"ok": False,
                "error": "ntfy-топик не задан: export PIPBOY_NTFY=<topic> (или --topic)"}
    if not message:
        message = "Pip-Boy: проверка связи"
    host = os.environ.get("PIPBOY_NTFY_HOST", "https://ntfy.sh").rstrip("/")
    url = f"{host}/{t}"
    try:
        import urllib.request
        req = urllib.request.Request(url, data=message.encode("utf-8"), method="POST")
        req.add_header("Title", "Pip-Boy")
        req.add_header("Priority", priority or "default")
        with urllib.request.urlopen(req, timeout=6) as r:
            return {"ok": True, "topic": t, "status": r.status,
                    "id": r.read().decode("utf-8", "replace").strip()}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"ntfy: {e}"}


def main() -> int:
    p = argparse.ArgumentParser(description="Pip-Boy actions (workspace/open, link/open, capture, term-open)")
    sub = p.add_subparsers(dest="cmd", required=True)
    wo = sub.add_parser("workspace-open")
    wo.add_argument("project")
    wo.add_argument("--no-term", action="store_true")
    ws = sub.add_parser("workspace-status")
    ws.add_argument("project")
    lo = sub.add_parser("link-open")
    lo.add_argument("target")
    lo.add_argument("--mode", default="browser", choices=["browser", "nvim", "tmux"])
    lr = sub.add_parser("link-resolve")
    lr.add_argument("target")
    ca = sub.add_parser("capture-scan")
    ca.add_argument("--run", action="store_true",
                    help="прогнать pipeline (перегенерировать signals.json)")
    ca.add_argument("--limit", type=int, default=20,
                    help="сколько сигналов вернуть (default 20)")
    to = sub.add_parser("term-open")
    to.add_argument("project")
    to.add_argument("--port", type=int, default=None)
    ts = sub.add_parser("term-status")
    ts.add_argument("project")
    tc = sub.add_parser("term-close")
    tc.add_argument("project")
    qq = sub.add_parser("query")
    qq.add_argument("--q", default="", help="текстовый поиск по карточкам")
    qq.add_argument("--facet", default="", help="фильтр по facet")
    qq.add_argument("--project", default="", help="фильтр по project")
    qb = sub.add_parser("blockers")
    qn = sub.add_parser("next")
    qn.add_argument("--limit", type=int, default=10)
    qd = sub.add_parser("dependencies")
    qd.add_argument("--card", default="", help="конкретная карточка (опционально)")
    nt = sub.add_parser("notify")
    nt.add_argument("--message", default="", help="текст пуша")
    nt.add_argument("--topic", default="", help="ntfy-топик (или env PIPBOY_NTFY)")
    nt.add_argument("--priority", default="default",
                    choices=["default", "low", "high", "urgent", "min", "max"])
    pp = sub.add_parser("proposals")
    ap = sub.add_parser("apply")
    ap.add_argument("--card", required=True, help="id карточки")
    ap.add_argument("--target", required=True, help="целевая стадия")
    args = p.parse_args()
    try:
        if args.cmd == "workspace-open":
            res = do_workspace_open(args.project, args.no_term)
        elif args.cmd == "workspace-status":
            res = do_workspace_status(args.project)
        elif args.cmd == "link-open":
            res = do_link_open(args.target, args.mode)
        elif args.cmd == "link-resolve":
            res = do_link_resolve(args.target)
        elif args.cmd == "capture-scan":
            res = do_capture_scan(args.run, args.limit)
        elif args.cmd == "term-open":
            res = do_term_open(args.project, args.port)
        elif args.cmd == "term-status":
            res = do_term_status(args.project)
        elif args.cmd == "term-close":
            res = do_term_close(args.project)
        elif args.cmd == "query":
            res = do_query(args.q, args.facet, args.project)
        elif args.cmd == "blockers":
            res = do_blockers()
        elif args.cmd == "next":
            res = do_next(args.limit)
        elif args.cmd == "dependencies":
            res = do_dependencies(args.card)
        elif args.cmd == "notify":
            res = do_notify(args.message, args.topic, args.priority)
        elif args.cmd == "proposals":
            res = do_proposals()
        elif args.cmd == "apply":
            res = do_apply(args.card, args.target)
        else:
            res = {"ok": False, "error": "unknown command"}
    except Exception as e:  # noqa: BLE001 — вернуть JSON вместо traceback
        res = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())