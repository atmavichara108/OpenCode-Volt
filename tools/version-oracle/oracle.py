#!/usr/bin/env python3
"""Offline version-oracle: reads only the Vault's already-known version markers."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UNKNOWN_REASON = "механика добычи данных — позже, по спеку"
STUB_COMPONENTS = [
    "SERPlux",
    "dv-hub",
    "dotfiles",
    "recruiting-hr",
    "AndroidOS",
    "ChaT",
    "Pip-Boy host",
]


def known(component: str, version: str, source: str, status: str = "ok", **extra) -> dict:
    item = {"component": component, "version": version, "status": status, "source": source}
    item.update(extra)
    return item


def read_vibeos() -> dict:
    path = ROOT / "VibeOS.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*([^\s#]+)", text, re.MULTILINE)
    return known("VibeOS", match.group(1) if match else "unknown", "VibeOS.md frontmatter", "ok" if match else "unknown")


def read_registry() -> list[dict]:
    path = ROOT / "tools" / "ecosystem-map" / "registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    return [
        known("ecosystem registry schema", str(meta.get("schema", "unknown")), "registry.json → meta.schema", "ok" if meta.get("schema") else "unknown"),
        known("ecosystem registry updated", str(meta.get("updated", "unknown")), "registry.json → meta.updated", "ok" if meta.get("updated") else "unknown"),
    ]


def read_generation_marker() -> dict:
    path = ROOT / "docs" / "vibeos" / "index.html"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"GENERATED FROM VibeOS\.md v([^\s]+) // ([^<]+)", text)
    if not match:
        return known("VibeOS HTML generation", "unknown", "docs/vibeos/index.html", "unknown")
    return known("VibeOS HTML generation", match.group(1), "docs/vibeos/index.html generation marker", "ok", generated=match.group(2))


def collect() -> dict:
    items = [read_vibeos(), *read_registry(), read_generation_marker()]
    items.extend({"component": name, "version": "unknown", "status": "unknown", "source": "stub-reader", "reason": UNKNOWN_REASON} for name in STUB_COMPONENTS)
    known_items = [item for item in items if item["status"] != "unknown"]
    unknown_items = [item for item in items if item["status"] == "unknown"]
    drift = []
    vibeos = next((x for x in items if x["component"] == "VibeOS"), None)
    marker = next((x for x in items if x["component"] == "VibeOS HTML generation"), None)
    if vibeos and marker and vibeos["version"] != "unknown" and marker["version"] != "unknown":
        drift.append({"check": "VibeOS ↔ HTML marker", "status": "ok" if vibeos["version"] == marker["version"] else "drift", "left": vibeos["version"], "right": marker["version"]})
    return {"oracle": "version-oracle", "mode": "version-oracle каркас", "items": items, "known": known_items, "unknown": unknown_items, "drift": drift}


def render_html(report: dict) -> str:
    template = (Path(__file__).parent / "panel.html").read_text(encoding="utf-8")
    rows = []
    for item in report["items"]:
        version = html.escape(str(item["version"]))
        status = html.escape(item["status"])
        source = html.escape(item["source"])
        rows.append(f'<tr><td>{html.escape(item["component"])}</td><td><code>{version}</code></td><td class="{status}">{status}</td><td class="dim">{source}</td></tr>')
    unknown = "<br>".join(html.escape(x["component"]) for x in report["unknown"])
    template = re.sub(r"<!-- ORACLE_ROWS_START -->.*?<!-- ORACLE_ROWS_END -->", "<!-- ORACLE_ROWS_START -->\n" + "\n".join(rows) + "\n<!-- ORACLE_ROWS_END -->", template, flags=re.S)
    return template.replace("<!-- ORACLE_UNKNOWN -->", unknown)


def text_report(report: dict) -> str:
    lines = ["VERSION-ORACLE // offline report", "", "Известно:"]
    lines.extend(f"  {x['component']}: {x['version']} [{x['status']}] ({x['source']})" for x in report["known"])
    lines.append("\nUnknown / стаб:")
    lines.extend(f"  {x['component']}: unknown — {x['reason']}" for x in report["unknown"])
    lines.append("\nПроверки расхождений:")
    if report["drift"]:
        lines.extend(f"  {x['check']}: {x['status']} ({x['left']} vs {x['right']})" for x in report["drift"])
    else:
        lines.append("  нет сопоставимых известных значений")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline version-oracle")
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report")
    output = report.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true")
    output.add_argument("--html", action="store_true")
    args = parser.parse_args()
    data = collect()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.html:
        print(render_html(data))
    else:
        print(text_report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
