"""Тесты state.py — идемпотентность, append-only, flock при конкурентном append."""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import state
from conftest import MODULE_DIR


def _msg(mid: str, text: str) -> dict:
    return {"message_id": mid, "subject": text[:20], "body": text}


def test_mark_and_processed_roundtrip(sandbox: Path):
    path = sandbox / "state" / "processed.jsonl"
    msgs = [_msg("<1@x>", "первое письмо"), _msg("<2@x>", "второе письмо")]

    assert state.mark(msgs, path) == 2
    assert state.is_processed(msgs[0], path)
    assert state.is_processed(msgs[1], path)
    assert not state.is_processed(_msg("<3@x>", "третье письмо"), path)


def test_repeat_mark_is_idempotent(sandbox: Path):
    path = sandbox / "processed.jsonl"
    msgs = [_msg("<1@x>", "одно и то же письмо")]
    assert state.mark(msgs, path) == 1
    assert state.mark(msgs, path) == 0  # повторный запуск не дублирует
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1


def test_state_grows_append_only(sandbox: Path):
    path = sandbox / "processed.jsonl"
    state.mark([_msg("<1@x>", "а")], path)
    first = path.read_text(encoding="utf-8")
    state.mark([_msg("<2@x>", "б")], path)
    second = path.read_text(encoding="utf-8")
    assert second.startswith(first)  # ничего не перезаписано
    assert len(second.splitlines()) == 2


def test_filter_new_excludes_processed_and_batch_dupes(sandbox: Path):
    path = sandbox / "processed.jsonl"
    msgs = [_msg("<1@x>", "а"), _msg("<2@x>", "б")]
    state.mark([msgs[0]], path)
    batch = msgs + [dict(msgs[1]), _msg("<2@x>", "б")]  # дубль id внутри батча
    out = state.filter_new(batch, path)
    assert [m["message_id"] for m in out] == ["<2@x>"]


def test_processed_detected_by_digest_without_message_id(sandbox: Path):
    path = sandbox / "processed.jsonl"
    msg = {"subject": "без идентификатора", "body": "просто текст письма"}
    state.mark([msg], path)
    assert state.is_processed(dict(msg), path)  # тот же текст → уже обработано


def test_broken_lines_do_not_break_state(sandbox: Path):
    path = sandbox / "processed.jsonl"
    state.mark([_msg("<1@x>", "а")], path)
    with path.open("a", encoding="utf-8") as f:
        f.write("{битая строка\n")
    assert state.is_processed(_msg("<1@x>", "а"), path)


def test_state_row_schema(sandbox: Path):
    path = sandbox / "processed.jsonl"
    state.mark([_msg("<1@x>", "а")], path)
    row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert row["message_id"] == "<1@x>"
    assert len(row["digest"]) == 64  # sha256
    assert "processed_at" in row


def test_concurrent_mark_flock_no_duplicates(sandbox: Path):
    """6 процессов дописывают одни и те же 20 писем одновременно."""
    path = sandbox / "concurrent.jsonl"
    msgs = [_msg(f"<{i}@x>", f"письмо номер {i}") for i in range(20)]
    payload = json.dumps(msgs, ensure_ascii=False)

    script = textwrap.dedent(
        """
        import json, sys
        import state
        state.mark(json.loads(sys.argv[1]), path=None if len(sys.argv) < 3 else __import__('pathlib').Path(sys.argv[2]))
        """
    )
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", script, payload, str(path)],
            cwd=str(MODULE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        for _ in range(6)
    ]
    for p in procs:
        _, err = p.communicate(timeout=60)
        assert p.returncode == 0, err.decode()

    rows = [
        json.loads(l)
        for l in path.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    ids = [r["message_id"] for r in rows]
    assert len(ids) == 20, "flock не сработал — state задублирован"
    assert len(set(ids)) == 20
