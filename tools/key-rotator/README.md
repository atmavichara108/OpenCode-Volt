# tools/key-rotator — ротация бесплатных моделей

Итерации над `docs/specs/key-rotator-probe-hook.md`:
**Iter-0 (probe)** и **Iter-1 (rotate)** реализованы и проверены (2026-09-27).

## Архитектура

```
providers.json (каталог, без секретов)
      ↓
probe.py   read-only: GET /models → ACTIVE|DEGRADED|BLOCKED|ERROR|SKIPPED
      ↓ append-only
control-plane/telemetry/provider-health.jsonl
      ↓
rotation.json (роли агентов + preferred-модели по роли)
      ↓
rotate.py  failover-выбор → model-router apply (flock+backup) → ntfy-пуш (curl)
      ↓
switch-event → health-log (event: switch)
```

Секреты нигде не хранятся: резолв `env → vault .env → auth.json`,
весь вывод через `redact` (ключи никогда в JSON/логи не попадают).

## Команды

```bash
# Iter-0: probe всех провайдеров (read-only, ничего не тратит)
.venv/bin/python tools/key-rotator/probe.py
# только выбранные, со свежим каталогом
.venv/bin/python tools/key-rotator/probe.py --provider amd-radeon --provider google
# оплачиваемый smoke-чат — только opt-in и только явной моделью:
.venv/bin/python tools/key-rotator/probe.py --provider X --smoke --smoke-model MODEL

# Iter-1: ротация (по умолчанию читает health-log, без сети)
.venv/bin/python tools/key-rotator/rotate.py                 # проверить (dry? нет — только failover)
.venv/bin/python tools/key-rotator/rotate.py --dry-run       # план без записи
.venv/bin/python tools/key-rotator/rotate.py --probe         # свежий probe перед выбором
.venv/bin/python tools/key-rotator/rotate.py --prefer-better # апгрейд на лучший доступный
.venv/bin/python tools/key-rotator/rotate.py --agent build --dry-run
```

## Правила ротации (Iter-1)

- Агент **не трогается**, если его провайдер здоров (`ACTIVE|SKIPPED|DEGRADED`)
  — никакого дёрганья без причины.
- **Failover** только при `BLOCKED|ERROR` текущего провайдера.
- `--prefer-better` — явный апгрейд на провайдера с бо́льшим `priority`.
- Кандидат обязан: быть healthy, подходить по роли, **быть виден
  model-router** (иначе модель не заработает у OpenCode), не быть current.
- Модель кандидата: `preferred`-подстрока по роли → иначе первая доступная.
- DEGRADED **не** вызывает ротацию (rate-limit — это «подожди», не «умер»).

## Гарантии записи

- Правка конфига **только** через `model-router.py apply` — flock + бэкап
  (`.model-router-backups/`) + atomic replace; файл не переписывается целиком.
- Дубли агентов (file + config) разрешаются флагом `--kind file|config`
  (добавлен в model-router в этой итерации).
- Модель применяется с рестарта инструмента / новой сессии (hot-reload нет).
- **Не править конфиги во время активного прогона агента.**

## Транспорт (по key-rotator-brief)

- HTTP **только curl** (fallback requests) — urllib режется Cloudflare 1010.
- `403 + error code: 1010` = виноват клиент, не ключ → `BLOCKED` +
  `cloudflare_1010_client_fingerprint`, ключ не «сжигается» в ретраях.
- `429` = ретрай до 2 раз с паузой 20с (`--retries/--pause`).
- Ловится `http.client.HTTPException` (BadStatusLine от прокси).
- `usage` из API **не используется** для учёта (anymodel +2000, скрытые
  подсказки cc/* — источник правды панель биллинга).

## Уведомления

ntfy через curl: топик `PIPBOY_NTFY`, хост `PIPBOY_NTFY_HOST` (default
ntfy.sh). Без топика уведомление молча пропускается (`skipped: no_topic`),
ротация от этого не зависит. Текст:
`Ротация: scope:agent — old → new (reason)`.

## Тесты

```bash
.venv/bin/python -m pytest tools/key-rotator/tests/ -q   # 61 тест, no-network
```

## Дальше (не реализовано)

- **New API gateway layer** (решение 2026-09-28, `docs/specs/newapi-gateway-layer.md`):
  все агенты → единый endpoint `newapi/<alias>`, failover per-request внутри
  New API; ротатор для key-based тира сдвигается в управление каналами
  (`newapi_sync.py`, планируется) вместо правки конфигов. **Правило: модель →
  канал New API только после bench-PASS.** zen/go free остаются на config-
  ротации (client-locked, шлюзом не покрываются).
- **Iter-2** — onboarding новых провайдеров (NIM, Groq, Cerebras, Mistral,
  DeepSeek, OpenRouter-пополнение) → ключи в env/auth, карточки, каталог.
- **Iter-3** — cron/systemd-timer (probe+rotate) + scout новых моделей
  (TG `@inbox_tools` + веб, полуавто: регистрация ключей вручную).
- Balance-эндпоинты (сейчас `balance: null` везде — пороги 25/10/0% ждут
  per-provider счётчиков).

## Связанные

- `docs/specs/key-rotator-probe-hook.md` — спека фичи.
- `docs/specs/key-rotator-research-snapshot-2026-09-27.md` — research-снапшот.
- `tools/ecosystem-map/model-router.py` — правка моделей агентов.
- `tools/model-bench/` — бенч моделей (отдельный контур).
- `01-Reference/abuse-providers-inbox.md` · `02-Methods/promo-provider-protocol.md`.
