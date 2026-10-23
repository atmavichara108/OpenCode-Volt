import json
import pathlib
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DD = ROOT / "10-Deck"

def nid(s):
    return f"n{zlib.crc32(s.encode()) & 0xffffff:06x}"

def text(i, t, x, y, w=420, h=170, color=None):
    n = {"id": i, "type": "text", "text": t, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def file(i, f, x, y, w=520, h=420, color=None):
    n = {"id": i, "type": "file", "file": f, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def edge(i, a, b, label=None):
    e = {"id": i, "fromNode": a, "toNode": b, "fromSide": "bottom", "toSide": "top"}
    if label:
        e["label"] = label
    return e

nodes = [
    text(nid("root"), "# 🚪 Deck — одна дверь\n\nЖивые виды из frontmatter. Статичных снимков нет: меняется реестр — меняется вид.", -260, -520, 820, 150, "4"),
    file(nid("quests"), "10-Deck/quests.base", -260, -260, 820, 460, "3"),
    file(nid("deck"), "10-Deck/deck.md", -260, 260, 820, 520),
    file(nid("depts"), "10-Deck/map-departments.canvas", 620, -260, 560, 460, "1"),
]

edges = [
    edge(nid("e1"), nid("root"), nid("quests"), "открывает"),
    edge(nid("e2"), nid("root"), nid("deck"), "как это устроено"),
    edge(nid("e3"), nid("root"), nid("depts"), "кто на борту"),
]

(DD / "DECK.canvas").write_text(
    json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")
print(f"DECK.canvas: {len(nodes)} узлов, {len(edges)} рёбер")