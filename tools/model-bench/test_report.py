"""Тесты report.py: matrix.md из фикстурных JSON, детерминированный порядок."""
import json

import report


def _write_artifact(out_dir, provider, model, rec):
    data = {
        "provider_id": provider,
        "model_id": model,
        "benchmark_version": "0.1.0",
        "date": "2026-09-23T00:00:00Z",
        "gates": {
            "tools": {"score": 1.0, "passed_threshold": True},
            "build": {"score": 0.75, "passed_threshold": True},
            "reasoning": {"score": 0.5, "passed_threshold": False},
            "fast": {"score": None, "passed_threshold": None},
        },
        "recommendation": rec,
        "advisory": True,
        "task_set_hash": "deadbeef1234",
    }
    (out_dir / f"{provider}__{model.replace('/', '_')}.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def test_render_matrix_deterministic_order(tmp_path):
    _write_artifact(tmp_path, "anymodel", "am/free", ["tools"])
    _write_artifact(tmp_path, "anymodel", "am/nemotron-x", [])
    _write_artifact(tmp_path, "amd-radeon", "DeepSeek-V4-Flash", ["reasoning"])

    arts = report.load_artifacts(tmp_path)
    md = report.render_matrix(arts)

    assert md.startswith("<!-- АВТОГЕНЕРАЦИЯ")
    # Детерминированный порядок: amd-radeon раньше anymodel (по provider_id)
    assert md.index("amd-radeon") < md.index("anymodel")
    # внутри anymodel: am/free раньше am/nemotron-x
    assert md.index("am/free") < md.index("am/nemotron-x")
    assert "0.1.0" in md
    assert "deadbeef1234" in md


def test_render_matrix_empty(tmp_path):
    md = report.render_matrix([])
    assert "Нет артефактов" in md


def test_main_writes_matrix(tmp_path):
    _write_artifact(tmp_path, "anymodel", "am/free", ["tools"])
    code = report.main(["--out", str(tmp_path)])
    assert code == 0
    matrix = (tmp_path / "matrix.md").read_text(encoding="utf-8")
    assert "АВТОГЕНЕРАЦИЯ" in matrix
    assert "am/free" in matrix
