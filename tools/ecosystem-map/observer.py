#!/usr/bin/env python3
"""Ecosystem observer — read-only deterministic snapshot CLI (MVP).

Читает (только чтение, никаких мутаций входов):
  - 03-Projects/*.md        — карточки проектов (frontmatter: repo/kind/stack/status)
  - TASKS.md                — оперативный трекер (статусы задач по секциям)
  - 04-Memory/route-log/*.md — route log entries (frontmatter)
  - tools/ecosystem-map/registry.json — canonical registry (cards/agents)
  - git (vault only): rev-parse HEAD, status --porcelain, log -1 (read-only plumbing)

Пишет (единственная мутация — собственный output):
  - tools/ecosystem-map/generated/snapshot.json  (или --output PATH)
  - --dry-run: печать в stdout без записи файла

Гарантии:
  - no network, no root, no commits, no mutation входов
  - детерминизм: одинаковый вход -> идентичный output (без wall-clock;
    input_digest = sha256 по отсортированным хешам входов)
  - snapshot НЕ источник правды: canonical = registry.json + карточки волта

Exit codes: 0 = ok; 1 = ошибка ввода; 2 = ошибка записи.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = VAULT_ROOT / "tools" / "ecosystem-map" / "registry.json"
DEFAULT_OUTPUT = VAULT_ROOT / "tools" / "ecosystem-map" / "generated" / "snapshot.json"

ALLOWED_LIFECYCLE = [
    "IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD",
    "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED",
]
ALLOWED_LAYERS = ["L0", "L1", "L2", "L3", "L4"]
ALLOWED_FACETS = ["memory", "routing", "telemetry", "verification", "knowledge", "interface"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_frontmatter(text: str) -> dict:
    """Минимальный YAML frontmatter-парсер (ключ: значение, без вложений)."""
    fm = {}
    if not text.startswith("---"):
        return fm
    end = text.find("\n---", 3)
    if end == -1:
        return fm
    block = text[3:end].strip("\n")
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("'\"")
    return fm


def read_projects() -> tuple[list[dict], dict[str, str]]:
    """Карточки проектов: (список, {путь: sha256})."""
    projects = []
    hashes = {}
    cards_dir = VAULT_ROOT / "03-Projects"
    for path in sorted(cards_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        hashes[str(path.relative_to(VAULT_ROOT))] = sha256_file(path)
        projects.append({
            "id": path.stem,
            "repo": fm.get("repo", ""),
            "kind": fm.get("kind", ""),
            "stack": fm.get("stack", ""),
            "status": fm.get("status", ""),
        })
    return projects, hashes


def read_tasks() -> tuple[dict, dict[str, str]]:
    """TASKS.md: {секция: [ID...]}, хеши входа.

    Секции Kanban: Active, Blocked, Planned, Backlog, Done.
    """
    path = VAULT_ROOT / "TASKS.md"
    text = path.read_text(encoding="utf-8")
    hashes = {"TASKS.md": sha256_file(path)}
    sections: dict[str, list[str]] = {"Active": [], "Blocked": [], "Planned": [], "Backlog": [], "Done": []}
    current = None
    for line in text.splitlines():
        heading = re.match(r"^##\s+.*", line)
        if heading:
            h = line.lower()
            if "active" in h:
                current = "Active"
            elif "blocked" in h:
                current = "Blocked"
            elif "planned" in h:
                current = "Planned"
            elif "backlog" in h:
                current = "Backlog"
            elif "done" in h:
                current = "Done"
            else:
                current = None
            continue
        if current:
            for tid in re.findall(r"\bT-\d{3}\b", line):
                if tid not in sections[current]:
                    sections[current].append(tid)
    return sections, hashes


def read_route_log() -> tuple[list[dict], dict[str, str]]:
    """Route-log entries: frontmatter + route_id из тела."""
    entries = []
    hashes = {}
    rl_dir = VAULT_ROOT / "04-Memory" / "route-log"
    for path in sorted(rl_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        hashes[str(path.relative_to(VAULT_ROOT))] = sha256_file(path)
        m = re.search(r"\*\*route_id:\*\*\s*`([^`]+)`", text)
        entries.append({
            "file": path.name,
            "date": fm.get("date", ""),
            "status": fm.get("status", ""),
            "route_id": m.group(1) if m else "",
        })
    return entries, hashes


def read_registry() -> tuple[dict, dict[str, str], list[str]]:
    """Canonical registry + хеш + schema warnings (read-only)."""
    hashes = {"tools/ecosystem-map/registry.json": sha256_file(REGISTRY_PATH)}
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    warnings = []
    for cid, card in registry.get("cards", {}).items():
        if card.get("layer") not in ALLOWED_LAYERS:
            warnings.append(f"{cid}: unknown layer {card.get('layer')!r}")
        if card.get("lifecycle") not in ALLOWED_LIFECYCLE:
            warnings.append(f"{cid}: unknown lifecycle {card.get('lifecycle')!r}")
        facets = card.get("facets", [])
        for facet in facets:
            if facet not in ALLOWED_FACETS:
                warnings.append(f"{cid}: unknown facet {facet!r}")
        for dep in card.get("depends_on", []):
            if dep not in registry.get("cards", {}):
                warnings.append(f"{cid}: unknown dependency {dep!r}")
    return registry, hashes, warnings


def git_state() -> tuple[dict, dict[str, str]]:
    """Read-only git plumbing (vault only): HEAD, porcelain, последняя дата коммита."""
    hashes = {}

    def run(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(VAULT_ROOT), *args],
            capture_output=True, text=True, check=True,
        ).stdout.strip()

    head = run("rev-parse", "HEAD")
    porcelain = run("status", "--porcelain")
    last_commit_date = run("log", "-1", "--format=%cI")
    # Нормализация porcelain: сортировка строк -> детерминизм
    dirty = sorted(line for line in porcelain.splitlines() if line.strip())
    hashes["git:HEAD"] = head
    state = {
        "head": head,
        "dirty_files": dirty,
        "last_commit_date": last_commit_date,
    }
    return state, hashes


def drift_signals(
    projects: list[dict],
    registry: dict,
    tasks: dict,
    git: dict,
    warnings: list[str],
) -> list[dict]:
    """Минимальный детерминированный drift-детектор (read-only)."""
    signals = []
    for p in projects:
        repo = p.get("repo", "")
        if repo and not Path(repo).exists():
            signals.append({
                "type": "repo_missing",
                "subject": p["id"],
                "detail": f"карточка заявляет repo={repo}, путь не существует",
            })
    for cid, card in registry.get("cards", {}).items():
        for artifact in card.get("artifacts", []):
            apath = VAULT_ROOT / artifact
            if not apath.exists():
                signals.append({
                    "type": "artifact_missing",
                    "subject": cid,
                    "detail": f"artifact {artifact} не существует",
                })
    for tid in tasks.get("Blocked", []):
        signals.append({
            "type": "task_blocked",
            "subject": tid,
            "detail": "TASKS.md: секция Blocked/Frozen",
        })
    for w in warnings:
        signals.append({"type": "registry_schema", "subject": "registry", "detail": w})
    return signals


def build_snapshot() -> dict:
    projects, h1 = read_projects()
    tasks, h2 = read_tasks()
    routes, h3 = read_route_log()
    registry, h4, warnings = read_registry()
    git, h5 = git_state()

    input_hashes = {**h1, **h2, **h3, **h4, **h5}
    digest = hashlib.sha256(
        "\n".join(f"{k}:{v}" for k, v in sorted(input_hashes.items())).encode("utf-8")
    ).hexdigest()

    cards_summary = {
        cid: {
            "title": card.get("title", ""),
            "layer": card.get("layer", ""),
            "lifecycle": card.get("lifecycle", ""),
            "owner": card.get("owner", ""),
        }
        for cid, card in sorted(registry.get("cards", {}).items())
    }

    return {
        "meta": {
            "schema": "ecosystem-snapshot/1.0",
            "generated": True,
            "deterministic": True,
            "live": False,
            "note": "Read-only deterministic snapshot; НЕ источник правды (canonical: registry.json + карточки волта). Real-time не заявляется.",
            "input_digest": digest,
            "vault_head": git["head"],
        },
        "projects": sorted(projects, key=lambda p: p["id"]),
        "tasks": tasks,
        "route_log": routes,
        "registry_cards": cards_summary,
        "agents": {
            aid: {"role": a.get("role", ""), "status": a.get("status", "")}
            for aid, a in sorted(registry.get("agents", {}).items())
        },
        "git": git,
        "drift_signals": drift_signals(projects, registry, tasks, git, warnings),
        "registry_warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only deterministic ecosystem snapshot")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="путь output JSON")
    parser.add_argument("--dry-run", action="store_true", help="печать в stdout без записи")
    args = parser.parse_args()

    try:
        snapshot = build_snapshot()
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"observer: ошибка ввода: {e}", file=sys.stderr)
        return 1

    payload = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)
    if args.dry_run:
        print(payload)
        return 0

    out = Path(args.output)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    except OSError as e:
        print(f"observer: ошибка записи {out}: {e}", file=sys.stderr)
        return 2
    try:
        rel = out.relative_to(VAULT_ROOT)
    except ValueError:
        rel = out
    print(f"observer: snapshot -> {rel} (digest {snapshot['meta']['input_digest'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
