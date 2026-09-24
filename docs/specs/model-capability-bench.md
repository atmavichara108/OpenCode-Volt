---
type: Spec
title: Model capability bench — детерминированный capability-probe силы моделей
description: Execution spec для Vault build-агента: детерминированный прогон 4 auto-verifiable гейтов (tools/build/reasoning/fast) для назначения ролей моделям. Advisory-выход (не блокирует роутинг). Python в tools/model-bench/.
tags: [spec, vault, model-bench, capability-probe, routing, advisory]
timestamp: 2026-09-23
status: planned
kind: task
owner: Vault build-агент (tools/) + verifier (приёмка)
related: "[[02-Methods/model-routing]] · [[02-Methods/promo-provider-protocol]] · [[02-Methods/verifier-pattern]]"
---

# Spec: Model capability bench (детерминированный capability-probe)

> Владелец исполнения — **Vault build-агент** (`tools/model-bench/`), приёмка —
> независимый **verifier**. librarian не реализует.
> Ключевые решения приняты оператором 2026-09-23 (см. §12).
> Метод: [[02-Methods/model-routing]]. Контракт баланса: [[02-Methods/promo-provider-protocol]].

## 1. Intent

Ответить на вопрос «какие задачи можно ставить модели» **до** её назначения в
роль. Capability-probe прогоняет фиксированный, версионированный набор задач
без LLM-судей и выдаёт **advisory** рекомендацию модель→роль. Выход кормит
[[02-Methods/model-routing]], **не подменяя** его: probe не меняет конфиг и не
влияет на роутинг автоматически.

## 2. Scope

**In (Vault only):**
- Реализация `tools/model-bench/` (Python, по образцу `tools/telegram-capture`:
  `.env`-ключи, proxy-aware).
- Артефакты в `01-Reference/model-benchmarks/` (per-model JSON + сводная matrix).
- Reserved schema-slot телеметрии баланса (без реализации, см. §10).

**Out:**
- Auto-routing / любая мутация конфига или роутинга (advisory only).
- Balance API-интеграции (только schema-slot).
- UI.
- Сравнение качества текстовыми LLM-судьями.

## 3. Gates (4, auto-verifiable)

Без LLM-судей. Фиксированные наборы задач, каждый с версией/hash задачи — чтобы
прогон был детерминирован и воспроизводим. Пороги — рекомендательные.

### 3.1 `tools`
5 задач strict JSON/tool-calling: parse + schema-валидация ответа. Порог
рекомендации **5/5**. Ошибка — невалидный JSON, лишние ключи, нарушение schema.

### 3.2 `build`
4 кодинг-задачи с pytest/golden-diff + 1 edit-задача (точечная правка файла по
инструкции). Порог рекомендации **≥75%**.

### 3.3 `reasoning`
4 задачи с детерминированным ответом: math / decomposition / trap-detection.
Порог рекомендации **≥70%**. Ответ проверяется точным совпадением, не оценкой
судьи.

### 3.4 `fast`
ping-серия: median latency, TTFT (где применим), tokens, оценка стоимости
`$/1K` по публичному прайсингу провайдера. Порога-прохода нет (информативный
гейт), но метрики обязательны к фиксации.

## 4. Cost guard

- Бюджет ≤ **$0.05** на модель за стандартный прогон (`k=1`).
- `k=3` (3 повтора) — только для финальной приёмки модели в роль, с указанием
  бюджета в прогоне.
- Free-модели — вне бюджета, но с подсчётом сожжённых токенов.
- Учесть: reasoning-модели раздувают smoke до ~9K токенов → в probe-заданиях
  обязательно `max_tokens`-ограничение.

## 5. Provider source

- Конфиг-селектор `provider_id` → `baseURL` из opencode config.
- Ключ из `auth.json` / env; **никогда не печатается** в логах/артефактах.
- Proxy fallback: некоторые endpoints за гео (опыт amd/anymodel) — прогон
  обязан уметь идти через настроенный прокси.

## 6. Output artifacts

### 6.1 Per-model JSON
`01-Reference/model-benchmarks/<provider_id>__<model_slug>.json`

```json
{
  "provider_id": "anymodel",
  "model_id": "model-slug",
  "benchmark_version": "0.1.0",
  "date": "2026-09-23T00:00:00Z",
  "gates": {
    "<gate>": {
      "score": 5,
      "passed_threshold": true,
      "cost_tokens": 1234,
      "cost_usd_est": 0.0,
      "latency_ms_median": 812,
      "notes": ""
    }
  },
  "recommendation": ["tools", "build"],
  "advisory": true
}
```

Промпты/содержимое задач в артефакт **не попадают** (только score/метрики) —
чтобы JSON был коммитабелен.

### 6.2 Matrix
`01-Reference/model-benchmarks/matrix.md` — сводная матрица модели × гейты.
**Перегенерируется** прогоном, руками не редактируется.

## 7. Recommendation (advisory)

`recommendation` — список ролей, которые модель подходит; `advisory: true`
всегда. Не влияет на config/роутинг автоматически (см. Acceptance (c)).

## 8. Telemetry slot (reserved)

**Не реализуется в этой задаче.** Резервируется место в схеме под будущую
сессию телеметрии баланса:

- Файл: `control-plane/telemetry/provider-usage.jsonl` (append-only).
- Schema строки:
  `{"ts","provider_id","model_id","source":"bench|chat","prompt_tokens","completion_tokens","reasoning_tokens","cost_usd_est","balance_source":"api|estimated|none"}`
- Feed'еры: bench-прогоны (эта задача) + будущий balance-hook.
- Пороги оповещений 25/10/0 — наследуются из promo-provider hook spec.

## 9. Security

- Ключи не в логах и не в артефактах (redaction обязателен).
- Benchmark JSON не содержит содержимого промптов (только score/метрики).

## 10. Acceptance

- (a) **Fixture-only прогон офлайн** (без сети): unit tests всех 4 gate-градеров.
- (b) **Live smoke**: 1 бесплатная модель с одним реальным прогоном.
- (c) **Advisory-выход** (`recommendation`) не влияет на config/роутинг
  автоматически — проверяется отсутствием мутаций.
- (d) Независимый **verifier** по evidence.
- (e) `git diff --check` чистый.

## 11. Out of scope

- Auto-routing.
- Balance API-интеграции (только slot).
- UI.
- Сравнение качества текстовыми LLM-судьями.

## 12. Ключевые решения (оператор, 2026-09-23)

1. Гейты — **advisory** (рекомендация модель→роль, НЕ блокировка роутинга).
2. Телеметрия баланса — отдельная будущая сессия; в этой задаче только
   резервирование места в схеме JSONL.
3. Реализация — Python в `tools/model-bench/` (по образцу tools/telegram-capture:
   `.env`-ключи, proxy-aware), **не в этой задаче**; ownership — Vault
   build-агент для `tools/` + verifier для приёмки.

## 13. Related

- [[02-Methods/model-routing]]
- [[02-Methods/promo-provider-protocol]]
- [[01-Reference/abuse-providers-inbox]]
- [[01-Reference/provider-cards/anymodel]] (free-модели как дешёвые стенды)
- [[02-Methods/verifier-pattern]]
