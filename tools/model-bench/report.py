"""Генератор сводной матрицы 01-Reference/model-benchmarks/matrix.md.

Читает все ``*.json`` в каталоге (кроме matrix.md), строит markdown-таблицу
модель × гейты. Файл начинается предупреждением об автогенерации. Порядок
детерминированный — sort по (provider_id, model_id).
"""
import argparse
import json
import sys
from pathlib import Path

import tasks

HEADER_WARNING = (
    "<!-- АВТОГЕНЕРАЦИЯ — не редактировать руками (tools/model-bench/report.py) -->\n"
)

GATE_ORDER = ["tools", "build", "reasoning", "fast"]


def load_artifacts(out_dir):
    """Загружает все per-model JSON из каталога (без matrix.md)."""
    results = []
    for p in sorted(out_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            results.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    results.sort(key=lambda d: (d.get("provider_id", ""), d.get("model_id", "")))
    return results


def render_matrix(artifacts):
    """Строит markdown-строку матрицы."""
    lines = [HEADER_WARNING, "# Матрица capability-бенчмарков\n"]
    if not artifacts:
        lines.append("_Нет артефактов бенчмарка._\n")
        return "".join(lines)

    header = ["Модель"]
    for g in GATE_ORDER:
        header.append(g)
    header += ["recommendation", "дата", "benchmark_version", "task_set_hash"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))

    for a in artifacts:
        provider = a.get("provider_id", "")
        model = a.get("model_id", "")
        row = [f"{provider} / {model}"]
        gates = a.get("gates") or {}
        for g in GATE_ORDER:
            meta = gates.get(g) or {}
            if meta.get("status", "OK") == "ERROR":
                row.append("ERROR")
                continue
            score = meta.get("score")
            threshold = tasks.THRESHOLDS.get(g)
            if score is None:
                row.append("—")
            elif threshold is None:
                row.append(f"{score}")
            else:
                mark = "✓" if meta.get("passed_threshold") else "✗"
                row.append(f"{score} / {threshold} {mark}")
        rec = ", ".join(a.get("recommendation") or [])
        row.append(rec or "—")
        row.append(a.get("date", ""))
        row.append(a.get("benchmark_version", ""))
        row.append(a.get("task_set_hash", ""))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Генерация matrix.md")
    parser.add_argument(
        "--out",
        default="01-Reference/model-benchmarks",
        help="каталог артефактов (default: 01-Reference/model-benchmarks)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = load_artifacts(out_dir)
    md = render_matrix(artifacts)
    (out_dir / "matrix.md").write_text(md, encoding="utf-8")
    sys.stdout.write(f"matrix.md записан: {len(artifacts)} моделей\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
