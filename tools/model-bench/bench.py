"""CLI capability-probe: прогон 4 гейтов против модели, per-model JSON-артефакт.

Логи — в stderr, финальный JSON-итог — в stdout. Промпты и ответы модели в
артефакт НЕ попадают (только score/метрики/заметки без содержимого ответов).

Артефакт содержит, помимо гейтов, поля бюджета: ``budget_usd``, ``spent_usd_est``,
``budget_stop``, ``gates_skipped`` (см. build_artifact/main).
"""
import argparse
import datetime
import json
import logging
import math
import os
import re
import statistics
import sys
from pathlib import Path

import client
import config
import graders
import report
import tasks

log = logging.getLogger("model-bench")

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT_DIR = VAULT_ROOT / "01-Reference" / "model-benchmarks"


def slugify(model_id):
    """Заменяет ``/`` и небезопасные символы на ``_``."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", model_id)


def estimate_run_cost(provider_id, model_id, gates, k):
    """Оценка стоимости прогона по промпт-токенам + max_tokens + множителю.

    Эвристика промпт-токенов: 1 токен ≈ 4 символа (грубо, по латинице/кириллице
    вперемешку). Скрытые reasoning-токены непредсказуемы — их накрывает
    ``client.token_multiplier`` (эмпирические множители, см. client.py).

    Возвращает кортеж ``(cost_usd, total_tokens_est)``. ``cost_usd`` — float
    или None (неизвестная модель — не выдумываем цену); ``total_tokens_est`` —
    int, возвращается всегда.
    """
    base_tokens = 0
    for gate in gates:
        for task in tasks.TASKS_BY_GATE[gate]:
            prompt_tokens_est = len(task["prompt"]) // 4
            base_tokens += (prompt_tokens_est + task["max_tokens"]) * k
    total_est = int(base_tokens * client.token_multiplier(provider_id, model_id))
    coeff = client._coefficient(provider_id, model_id)
    if coeff is None:
        return None, total_est
    cost = client.COST_BASE_USD_PER_1M * coeff * total_est / 1_000_000
    return cost, total_est


def run_gate(gate, provider_id, model_id, base_url, key, proxies, k):
    """Прогоняет гейт, возвращает метрики гейта (score, tokens, latency...)."""
    task_list = tasks.TASKS_BY_GATE[gate]
    scores = []
    total_tokens = 0
    latencies = []
    cost_usd = None
    for task in task_list:
        for _ in range(k):
            reply, usage, latency_ms, err = client.chat(
                base_url, key, model_id, task["prompt"], task["max_tokens"],
                proxies=proxies,
            )
            if err:
                log.warning("gate=%s task=%s error: %s", gate, task["id"], err)
                scores.append(0)
                continue
            latencies.append(latency_ms)
            total_tokens += (usage or {}).get("total_tokens", 0)
            ok = _grade_one(task, reply)
            scores.append(1 if ok else 0)
    score = sum(scores) / len(scores) if scores else 0.0
    cost = client.estimate_cost_usd(
        provider_id, model_id, {"total_tokens": total_tokens}
    )
    median = statistics.median(latencies) if latencies else None
    return {
        "score": round(score, 4),
        "passed_threshold": _passed(score, gate),
        "cost_tokens": total_tokens,
        "cost_usd_est": cost,
        "latency_ms_median": median,
        "notes": "",
    }


def _passed(score, gate):
    threshold = tasks.THRESHOLDS.get(gate)
    if threshold is None:
        return None
    return score >= threshold


def _grade_one(task, reply):
    gate = task["gate"]
    if gate == "tools":
        return graders.grade_tools(reply, task["schema"])
    if gate == "build":
        if "tests" in task:
            return graders.grade_build(reply, task["tests"])
        return graders.grade_build_edit(
            reply, task["must_contain"], task["must_not_contain"]
        )
    if gate == "reasoning":
        return graders.grade_reasoning(reply, task["expected"])
    if gate == "fast":
        return True
    return False


def build_recommendation(gates_result):
    """Список гейтов/ролей, прошедших порог (fast не включается)."""
    rec = []
    for gate, meta in gates_result.items():
        if gate == "fast":
            continue
        if meta.get("passed_threshold") is True:
            rec.append(gate)
    return rec


def build_artifact(provider_id, model_id, gates_result, k):
    """Формирует per-model JSON по схеме из спеки §6.1."""
    return {
        "provider_id": provider_id,
        "model_id": model_id,
        "benchmark_version": config.BENCHMARK_VERSION,
        "date": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "gates": gates_result,
        "recommendation": build_recommendation(gates_result),
        "advisory": True,
        "task_set_hash": tasks.TASK_SET_HASH,
        "k": k,
    }


def dry_run_plan(provider_id, model_id, gates, k):
    """Печатает план прогона без сетевых вызовов."""
    lines = []
    lines.append(f"DRY-RUN: provider={provider_id} model={model_id} k={k}")
    total_requests = 0
    for gate in gates:
        n = len(tasks.TASKS_BY_GATE[gate])
        total_requests += n * k
        lines.append(f"  gate={gate}: {n} задач × {k} повтор(ов) = {n * k} запросов")
    lines.append(f"  всего запросов: {total_requests}")
    cost, tokens_est = estimate_run_cost(provider_id, model_id, gates, k)
    lines.append(f"  оценка токенов: ~{tokens_est} (с множителем {client.token_multiplier(provider_id, model_id)})")
    if cost is None:
        lines.append("  оценка бюджета: неизвестная модель (cost_usd_est=null)")
    else:
        lines.append(f"  оценка бюджета: ${cost:.6f}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Model capability probe")
    parser.add_argument("--provider", required=True, help="provider_id")
    parser.add_argument("--model", required=True, help="model_id")
    parser.add_argument(
        "--gates", default="tools,build,reasoning,fast",
        help="список гейтов через запятую (default: tools,build,reasoning,fast)",
    )
    parser.add_argument("--k", type=int, default=1, help="число повторов (default 1)")
    parser.add_argument("--dry-run", action="store_true", help="план без сетевых вызовов")
    parser.add_argument("--force", action="store_true", help="игнорировать cost-guard")
    parser.add_argument(
        "--budget",
        type=float,
        default=0.02,
        help="лимит фактических расходов прогона в USD (default 0.02); превышение останавливает оставшиеся гейты",
    )
    parser.add_argument("--skip-matrix", action="store_true", help="не генерировать matrix.md")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="каталог артефактов")
    args = parser.parse_args(argv)

    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")

    if not math.isfinite(args.budget) or args.budget <= 0:
        log.error(
            "Некорректный --budget: %r. Ожидается конечное положительное число USD.",
            args.budget,
        )
        return 3

    gates = [g.strip() for g in args.gates.split(",") if g.strip()]
    for g in gates:
        if g not in tasks.TASKS_BY_GATE:
            log.error("Неизвестный гейт: %s", g)
            return 3

    seen = set()
    deduped = []
    for g in gates:
        if g not in seen:
            seen.add(g)
            deduped.append(g)
    if len(deduped) != len(gates):
        log.warning("Повторяющиеся гейты убраны: %s", ", ".join(gates))
    gates = deduped

    if args.dry_run:
        sys.stdout.write(dry_run_plan(args.provider, args.model, gates, args.k) + "\n")
        return 0

    base_url, models = config.resolve_provider(args.provider)
    if not base_url:
        log.error("Не найден baseURL для провайдера %s", args.provider)
        return 3
    key = config.resolve_key(args.provider)

    # Cost guard (предварительный): лимит = min(COST_GUARD_USD, budget).
    est_cost, _est_tokens = estimate_run_cost(args.provider, args.model, gates, args.k)
    guard_limit = min(config.COST_GUARD_USD, args.budget)
    if est_cost is not None and est_cost > guard_limit and not args.force:
        log.error(
            "Cost-guard: ожидаемая стоимость $%.6f превышает лимит $%.6f. "
            "Используйте --force для продолжения.",
            est_cost, guard_limit,
        )
        return 2

    proxies = config.proxies_from_env()

    gates_result = {}
    gates_skipped = []
    spent_usd = 0.0
    budget_stop = False
    for idx, gate in enumerate(gates):
        gates_result[gate] = run_gate(
            gate, args.provider, args.model, base_url, key, proxies, args.k
        )
        spent_usd += gates_result[gate].get("cost_usd_est") or 0.0
        remaining = gates[idx + 1:]
        if spent_usd > args.budget and remaining and not args.force:
            log.warning(
                "Budget-guard: фактический расход $%.6f превысил лимит $%.6f — "
                "останавливаю оставшиеся гейты: %s",
                spent_usd, args.budget, ", ".join(remaining),
            )
            gates_skipped = remaining
            budget_stop = True
            break

    artifact = build_artifact(args.provider, args.model, gates_result, args.k)
    artifact["budget_usd"] = args.budget
    artifact["spent_usd_est"] = round(spent_usd, 6)
    artifact["budget_stop"] = budget_stop
    artifact["gates_skipped"] = gates_skipped

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{args.provider}__{slugify(args.model)}.json"
    out_path = out_dir / fname
    out_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not args.skip_matrix:
        try:
            artifacts = report.load_artifacts(out_dir)
            md = report.render_matrix(artifacts)
            (out_dir / "matrix.md").write_text(md, encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            log.warning("matrix.md не сгенерирован (артефакт уже записан): %s", exc)

    sys.stdout.write(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
