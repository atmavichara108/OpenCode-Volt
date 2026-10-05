#!/usr/bin/env python3
"""Deterministic, dependency-free SVG charts for the VibeOS showcase.

Run from the vault root: python3 tools/vibeos-vitrina/charts.py
Inputs are VibeOS.md, TASKS.md and the runbook changelog; no chart values are
duplicated here.
"""
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(exist_ok=True)

def esc(s): return html.escape(str(s))
def svg(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title><style>text{{font-family:monospace;font-size:12px;fill:#b7f774}} .muted{{fill:#6c9b4d}} .grid{{stroke:#31552d;stroke-width:1}} .bar{{fill:#79d34b}} .hot{{fill:#d8ff77}} .blocked{{fill:#ffb347}}</style>{body}</svg>'''

def heatmap():
    text = (ROOT / "VibeOS.md").read_text()
    rows = re.findall(r'^\| \[\[02-Methods/([^|\\]+).*?\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|$', text, re.M)
    rows = [(r[0].replace('\\|',''), r[1].strip(), r[2].strip(), r[3].strip(), r[4].strip()) for r in rows]
    projects = ["SERPlux", "dv-hub", "dotfiles", "vault"]
    x0, y0, cw, ch = 165, 35, 105, 25
    body = ''.join(f'<text x="{x0+i*cw+8}" y="20">{p}</text>' for i,p in enumerate(projects))
    for j, row in enumerate(rows):
        body += f'<text class="muted" x="0" y="{y0+j*ch+17}">{esc(row[0][:22])}</text>'
        for i, val in enumerate(row[1:]):
            color = '#79d34b' if '✅' in val else '#d8ff77' if '🟡' in val or 'stable' in val else '#31552d'
            body += f'<rect x="{x0+i*cw}" y="{y0+j*ch}" width="88" height="20" rx="2" fill="{color}"/><text x="{x0+i*cw+35}" y="{y0+j*ch+15}" fill="#061006">{esc(val[:10])}</text>'
    return svg(600, max(100, y0+len(rows)*ch+15), body, "Внедрение методов по проектам")

def timeline():
    text = (ROOT / "07-Runbooks/vibecoding-changelog.md").read_text()
    vibe = (ROOT / "VibeOS.md").read_text()
    entries = re.findall(r'^###\s+(v?\d+\.\d+(?:\.\d+)?)\s*\(([^)]+)\)', vibe, re.M)
    entries = entries or [(v, d) for v,d in re.findall(r'^###\s+(v?\d+\.\d+(?:\.\d+)?)\s*\(([^)]+)\)', text, re.M)]
    entries = list(dict.fromkeys(entries))
    body = '<line class="grid" x1="65" y1="70" x2="570" y2="70"/>'
    for i,(ver,date) in enumerate(entries):
        x = 75 + i * (495/max(1,len(entries)-1))
        body += f'<circle class="hot" cx="{x:.1f}" cy="70" r="7"/><text x="{x-18:.1f}" y="48">{esc(ver)}</text><text class="muted" x="{x-32:.1f}" y="98">{esc(date[:16])}</text>'
    return svg(620, 125, body, "Timeline версий VibeOS")

def burndown():
    text = (ROOT / "TASKS.md").read_text()
    sections = re.findall(r'^##\s+([^\n]+)(.*?)(?=^##\s+|\Z)', text, re.M|re.S)
    wanted = [("Active", "🟡"), ("Blocked", "⛔"), ("Planned", "🔵"), ("Done", "✅")]
    vals=[]
    for name, mark in wanted:
        block = next((b for h,b in sections if name in h), '')
        vals.append((name, len(re.findall(r'^\|\s*T-\d+', block, re.M))))
    # Include the published snapshot as a visible comparison if table rows are
    # truncated by a future format change; current values are parsed above.
    width=600; body=''; maxv=max([v for _,v in vals] or [1])
    for i,(name,val) in enumerate(vals):
        y=25+i*32; w=400*val/maxv if maxv else 0
        body += f'<text x="0" y="{y+15}">{name}</text><rect class="bar" x="85" y="{y}" width="{w:.1f}" height="20"/><text x="{95+w:.1f}" y="{y+15}">{val}</text>'
    return svg(width, 25+len(vals)*32, body, "TASKS burndown")

if __name__ == '__main__':
    charts = {'methods-heatmap.svg': heatmap(), 'version-timeline.svg': timeline(), 'tasks-burndown.svg': burndown()}
    for name, data in charts.items(): (OUT / name).write_text(data)
    print('\n'.join(str(OUT / n) for n in charts))
