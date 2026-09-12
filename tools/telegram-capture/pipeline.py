"""pipeline.py — детерминированный intake-pipeline capture → signals.

Связывает слои экосистемы: сырые посты из группы @inbox_tools превращаются в
«signals-артефакт» — читаемые самой картой (tools/ecosystem-map) кандидаты
апгрейда по проектам. Читается как библиотека (функции) и как CLI.

Фазы (все чисты, без wall-clock и без сетевых вызовов):
  1. flatten       — captures_all.json (topics → list[post]) → плоский список
  2. classify      — classify_batch() из classify.py (категория/repo/title/lang)
  3. score         — relevance scoring (0..N) детерминированными правилами
  4. map project   — категория → проект (dotfiles/serplux/dv-hub/vault/new)
  5. upgrade path  — что с этим постом делать (направление кандидата)
  6. artifact      — signals JSON с input_digest (sha256) для детерминизма

Гарантии: read-only (пишет только собственный output), no network, no commits.
Мутация входов отсутствует; единственная мутация — сигнатурный артефакт.

Использование:
    python pipeline.py --input captures_all.json --output signals.json
    python pipeline.py --input captures_all.json --dry-run   # печать в stdout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import classify


def _resolve_captures(directory: Path | None = None) -> Path:
    """Локализовать входной captures-файл (устойчиво к date-suffixing).

    Каноническое имя captures_all.json; если оно отсутствует (активный сбор
    переименовал его в captures_all-<date>.json), берём последний датированный
    снимок. Данные не трогаем — только поиск. `directory` по умолчанию — каталог
    этого модуля; параметр нужен для тестов.
    """
    d = directory or Path(__file__).resolve().parent
    canonical = d / "captures_all.json"
    if canonical.exists():
        return canonical
    dated = sorted(d.glob("captures_all-*.json"))
    return dated[-1] if dated else canonical


DEFAULT_INPUT = _resolve_captures()
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "signals.json"

# Категория классификатора → проект экосистемы (идентификатор карточки 03-Projects).
# error / неизвестная категория не дают сигнала (None).
CATEGORY_TO_PROJECT = {
    "dotfiles": "dotfiles",
    "serplux": "SERPlux",
    "dv-hub": "dv-hub",
    "vibeos": "vault",
    "new": "new",
    "error": None,
}

# Направление апгрейда по проекту (детерминированная фраза для signals).
PROJECT_UPGRADE_PATH = {
    "dotfiles": "кандидат на установку/интеграцию в dotfiles (Linux UX)",
    "SERPlux": "кандидат фичи/инструмента SERPlux (scraping/SEO/API)",
    "dv-hub": "кандидат связи/интеграции dv-hub",
    "vault": "кандидат в методы/агенты волта (VibeOS)",
    "new": "новый проект/направление — триаж в 99-Inbox",
}


def flatten_captures(data: dict) -> list[dict]:
    """captures_all.json ({topics: {topic: [post]}}) → плоский список с 'topic'.

    Детерминированный порядок: темы в порядке ключей, посты в порядке списка.
    """
    topics = data.get("topics", {})
    flat: list[dict] = []
    for topic, posts in topics.items():
        for p in posts:
            flat.append({**p, "topic": topic})
    return flat


def load_input(path: Path) -> list[dict]:
    """Прочитать вход: captures_all.json (topics-структура) ИЛИ JSONL-очередь.

    - `.jsonl` — строчки inbox_queue (уже плоские, с topic/text) → как есть;
    - иначе `{topics:{...}}` → flatten_captures.
    Детерминированный порядок сохраняется (jsonl — порядок строк).
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        flat: list[dict] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                flat.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return flat
    data = json.loads(text)
    # Три формы: (a) list [post...] — новый формат активного сбора (уже с topic);
    # (b) dict {topics:...} — старый captures_all.json; (c) dict-пост.
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "topics" in data:
        return flatten_captures(data)
    return [data]


def relevance_score(post: dict) -> int:
    """Детерминированный relevance-scoring поста по уже извлечённым полям.

    Шкала 0..10 (целая). Вход — запись из classify_batch (category/repo/title/lang).
    """
    score = 0
    if post.get("repo"):
        score += 3          # есть GitHub-репо — конкретный инструмент
    if post.get("title"):
        score += 2          # извлечли название
    if post.get("lang"):
        score += 1          # понятен язык
    text = post.get("text") or ""
    if len(text) >= 200:
        score += 2          # содержательное описание
    elif len(text) >= 60:
        score += 1
    if re.search(r"github\.com", text, re.IGNORECASE):
        score += 2          # ссылка на репо в теле
    return min(score, 10)


def project_for(category: str) -> str | None:
    """Категория → id проекта (dotfiles/serplux/dv-hub/vault/new; error → None)."""
    return CATEGORY_TO_PROJECT.get(category)


def upgrade_path_for(project: str) -> str:
    """Проект → строка направления апгрейда."""
    return PROJECT_UPGRADE_PATH.get(project, "триаж")


def build_signals(flat: list[dict]) -> dict:
    """Полный pipeline: классификация + скоринг + маппинг → signals-артефакт.

    Чистая функция: одинаковый вход → идентичный выход. Поля blog-обёртки нет,
    wall-clock не используется; digest считается по канонической сериализации.
    """
    classified = classify.classify_batch(flat)
    records = classified["posts"]

    # текст поста для скоринга: message_id → text (один проход, O(n))
    text_by_id = {p.get("message_id"): p.get("text") or "" for p in flat}

    signals: list[dict] = []
    project_counts: dict[str, int] = {}
    seen_repos: set[str] = set()

    # digest — по каноническому JSON входов (для неизменности ответа)
    digest = hashlib.sha256(
        json.dumps(flat, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    for rec in records:
        cat = rec["category"]
        project = project_for(cat)
        if project is None:
            continue  # error — не даёт сигнала

        # де-дуп по repo (уже помеченные error в classify здесь не попадают,
        # но повторяющиеся repo могли пройти как одинаковые из разных тем)
        repo = rec.get("repo") or ""
        repo_key = repo.rstrip("/").lower()
        if repo and repo_key in seen_repos:
            continue
        if repo:
            seen_repos.add(repo_key)

        score = relevance_score({**rec, "text": text_by_id.get(rec["message_id"], "")})
        signals.append({
            "message_id": rec["message_id"],
            "topic": rec["topic"],
            "title": rec["title"],
            "lang": rec["lang"],
            "repo": repo,
            "category": cat,
            "project": project,
            "relevance": score,
            "upgrade_path": upgrade_path_for(project),
        })
        project_counts[project] = project_counts.get(project, 0) + 1

    signals.sort(key=lambda s: (-s["relevance"], s["project"], s["message_id"]))

    return {
        "meta": {
            "schema": "capture-signals/1.0",
            "input_digest": digest,
            "total_posts": len(records),
            "total_signals": len(signals),
        },
        "summary": classified["summary"],
        "projects": project_counts,
        "signals": signals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Intake-pipeline capture → signals-артефакт (read-only)."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT),
                        help="captures_all.json или inbox-queue.jsonl")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help="куда писать signals.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="печать в stdout без записи файла")
    args = parser.parse_args()

    src = Path(args.input)
    try:
        flat = load_input(src)
    except OSError as e:
        print(f"pipeline: не читается {src}: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"pipeline: битый JSON {src}: {e}", file=sys.stderr)
        return 2

    signals = build_signals(flat)
    out = json.dumps(signals, ensure_ascii=False, indent=2)

    if args.dry_run:
        # stdout — только JSON (для пайпов и /action), сводка идёт в stderr
        print(out)
        _log_summary(signals, file=sys.stderr)
    else:
        try:
            Path(args.output).write_text(out + "\n", encoding="utf-8")
        except OSError as e:
            print(f"pipeline: ошибка записи {args.output}: {e}", file=sys.stderr)
            return 2
        _log_summary(signals)
    return 0


def _log_summary(signals, file=None):
    m = signals["meta"]
    print(f"pipeline: posts={m['total_posts']} signals={m['total_signals']} "
          f"digest={m['input_digest'][:12]}", file=file)
    for proj, n in sorted(signals["projects"].items()):
        print(f"  {proj}: {n}", file=file)


if __name__ == "__main__":
    sys.exit(main())