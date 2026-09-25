# tools/model-bench — детерминированный capability-probe моделей

Скрипт-инструмент VibeOS. Прогоняет фиксированный, версионированный набор
задач через 4 авто-проверяемых гейта (tools/build/reasoning/fast) без
LLM-судей и выдаёт **advisory** рекомендацию модель→роль. Выход кормит
[[02-Methods/model-routing]], **не подменяя** его: probe не меняет конфиг и
не влияет на роутинг автоматически.

Спека: `docs/specs/model-capability-bench.md`.

## Архитектура

```
[opencode config] → resolve_provider (baseURL + модели)
[auth.json / env] → resolve_key
[env proxy]       → proxies_from_env
        ↓
[client.chat] urllib → /chat/completions (OpenAI-compatible)
        ↓
[graders] детерминированная проверка (JSON-schema / subprocess / golden / exact)
        ↓
[bench.py] → 01-Reference/model-benchmarks/<provider>__<model>.json
[report.py] → 01-Reference/model-benchmarks/matrix.md
```

## Установка

Проект использует direnv + `.venv` (как принято в волте). Зависимости —
только `python-dotenv` (HTTP — стандартный `urllib`, без requests/httpx).

```bash
cd /home/rudra/Projects/OpenCode-Vault
python -m venv .venv
direnv allow
pip install python-dotenv pytest
```

## Запуск

```bash
# План без сетевых вызовов
python tools/model-bench/bench.py --provider anymodel --model am/free --dry-run

# Полный прогон (все 4 гейта, k=1)
python tools/model-bench/bench.py --provider anymodel --model am/free

# Выборочные гейты, 3 повтора (для приёмки), принудительно сверх бюджета
python tools/model-bench/bench.py --provider anymodel --model cx/gpt-6-astra \
    --gates tools,build --k 3 --force

# Генерация сводной матрицы (после каждого прогона — авто; --skip-matrix отключает)
python tools/model-bench/report.py --out 01-Reference/model-benchmarks
```

Логи — в stderr, финальный JSON-итог — в stdout. Per-model JSON пишется в
`01-Reference/model-benchmarks/` (каталог создаётся при прогоне).

## Гейты и пороги

| Гейт | Что проверяет | Порог рекомендации |
|------|---------------|--------------------|
| `tools` | 5 задач strict JSON (schema-валидация) | 5/5 (1.0) |
| `build` | 4 кодинг-задачи (subprocess-прогон) + 1 edit-задача (golden-подстроки) | ≥75% |
| `reasoning` | 4 задачи (math / decompose / trap / compare), точное совпадение | ≥70% |
| `fast` | 3 ping-запроса (latency, tokens) | — (информативный) |

`recommendation` — список гейтов, прошедших порог; `fast` в него не входит.

### Status / error semantics

Каждый гейт в артефакте несёт поле `status`: `"OK"` (числовой score и порог)
или `"ERROR"`. Гейт получает `status: "ERROR"`, если хотя бы один запрос
завершился транспортной/парсинговой ошибкой (HTTP 429/503, network, parse и
т. п.) — при этом `score: null`, `passed_threshold: null`, `latency_ms_median:
null`, а в `error_count`/`error_rate`/`error_kinds` (deduplicated sorted list
видов сбоя) фиксируется факт сбоя без тел ответов и ключей. Сырые тексты
ошибок в артефакт не попадают (только redacted-лог в stderr). Ошибочные
запросы не дают ложный `score: 0` (это
capability-fail) и не попадают в токены/латентность. `build_recommendation`
не включает гейты со `status != "OK"`, а матрица показывает их как `ERROR`.
Старые артефакты без `status` трактуются как `OK`.

## Cost guard

- Предварительная оценка: промпт-токены (1 токен ≈ 4 символа) + `max_tokens`,
  умноженные на эмпирический `client.token_multiplier` (факт/оценка, см.
  `OBSERVED_TOKEN_MULTIPLIER`). Предсказание всегда неточно (разброс
  0.74×..36×) — это лишь сигнал.
- Основная защита — **накопительный останов по фактическому расходу**:
  `--budget` (default `$0.02`) суммирует фактический `cost_usd_est` после
  каждого гейта и, при превышении, останавливает оставшиеся гейты.
- Предварительный cost-guard срабатывает по `min(COST_GUARD_USD, --budget)`.
- `--force` отключает и предварительный guard, и накопительный останов.
- Free-модели (`am/free`, `am/nemotron*`, весь `amd-radeon`) — вне бюджета,
  но токены считаются.
- Неизвестная модель → `cost_usd_est: null` (цену не выдумываем).

В артефакт попадают поля `budget_usd`, `spent_usd_est`, `budget_stop`,
`gates_skipped` (список непрогнанных гейтов).

## Ограничения и безопасность

- **(а) Исполнение кода модели.** `grade_build` запускает код модели в
  отдельном `subprocess` с временным cwd, `timeout=10` секунд и минимальным
  окружением (без прокси и `*_API_KEY`). Однако **полная изоляция и отсутствие
  сети не гарантированы** — не запускайте бенч на недоверенных провайдерах
  без sandbox.
- **(б) Артефакты** не содержат промптов, ответов модели и ключей — только
  score/метрики/заметки (JSON коммитабелен).
- **(в) Advisory.** `advisory: true` всегда; рекомендация не влияет на
  config/роутинг автоматически.
- **(г) Reserved telemetry slot.** Слот телеметрии баланса
  (`control-plane/telemetry/provider-usage.jsonl`) здесь **не реализуется** —
  в `client.emit_telemetry()` оставлен явный no-op хук (TODO для будущей
  сессии).

## Безопасность ключей

Ключ резолвится из env → `.env` (корень волта) → `auth.json`, никогда не
логируется и не попадает в артефакты. Сообщения об ошибках прогоняются через
`redact`. `.env` и `auth.json` не коммитятся.
