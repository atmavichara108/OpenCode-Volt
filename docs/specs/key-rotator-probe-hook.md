---
type: Execution Spec
title: Key Rotator — probe + balance + live model switch (vault)
status: implemented
scope: vault
date: 2026-09-27
owner: sysop / dotfiles-agents (impl), librarian (oversight)
---

# Key Rotator — probe + balance + live model switch

> **Статус (2026-09-27):** Iter-0 (probe) и Iter-1 (rotate) **реализованы**,
> 61 тест зелёный, живая верификация (apply + бэкап + откат) пройдена.
> Реализация: `tools/key-rotator/` (см. README). Balance-эндпоинты
> (usable_balance) ещё не подключены — `balance: null` везде; Iter-2/3 по плану.

> Надстройка над [[02-Methods/promo-provider-protocol]] и существующим
> read-only probe-хуком (dotfiles spec:
> `promo-provider-probe-balance-hook.md`). Здесь ротатор **активно**
> выбирает рабочий провайдер/модель и пишет active-модель в конфиг.
> Read-only probe + balance мониторинг — из dotfiles-спеки; этот спек
> добавляет слой **выбора и переключения**.

## 1. Intent

На фоне многих промо/реферальных провайдеров (часть жива, часть без баланса,
часть с ежедневными лимитами) нужен автоматический выбор **рабочего**
провайдера и модели для агентного кодинга, с фоллбэк-цепочкой и без ручного
подбора. Ротатор:

1. **probe** каждого провайдера (read-only: `/v1/models` + опциональный smoke).
2. Собирает **live-карту доступности** (статус, модели, usable-баланс, лимиты).
3. **выбирает** лучшего кандидата по приоритету роли (кодинг/vision/скорость).
4. **переключает** active-модель в конфиге (opencode.json / dotfiles), с
   верификацией до и после.

## 2. Scope

**In (vault + dotfiles конфиги):**
- CLI `tools/key-rotator/rotator.py` (Python, stdlib + urllib, паттерн model-bench).
- Декларативный конфиг провайдеров `tools/key-rotator/providers.json` (без секретов).
- Авто-переключение active-модели в `opencode.json` (и target-конфигах dotfiles).
- Live-отчёт в `control-plane/telemetry/provider-health.jsonl` (append-only).

**Out:**
- Ключи в репо/логах (запрещено; redaction обязательна).
- Обход ToS / мультиаккаунт-фарминг / автоматизация трат без opt-in (запрещено).
- Автономный **поиск** новых провайдеров — НЕ здесь (отдельный спек "abuz scout").

## 3. Существующее (что переиспользуем, НЕ пишем заново)

| Компонент | Путь | Зачем |
|-----------|------|-------|
| OpenAI-compatible клиент | `tools/model-bench/client.py` | `chat()`, `estimate_cost_usd`, redaction, retry |
| Резолвер ключа/провайдера | `tools/model-bench/config.py` | `resolve_key()`, `resolve_provider()`, `redact()`, proxy |
| Метод приёмки | `02-Methods/promo-provider-protocol.md` | lifecycle INBOX→…→ACTIVE→DEGRADED→RETIRED |
| Read-only probe spec | `dotfiles/.../promo-provider-probe-balance-hook.md` | probe + баланс, thresholds 25/10/0%, exit-статусы |
| Карточки провайдеров | `01-Reference/provider-cards/*.md` | канонический источник по статусу/эндпоинту |
| Inbox таблица | `01-Reference/abuse-providers-inbox.md` | все промо-провайдеры, triage |
| Актуальные ключи | `~/.local/share/opencode/auth.json` + `.env` | ключ читается только оттуда, не хардкодится |

## 4. Inputs

- Список провайдеров: `providers.json` (id, endpoint, role-профиль, приоритет,
  `balance_endpoint`/`balance_selector`/`denominator` — из карточек).
- Ключи: резолв через `config.resolve_key(provider_id)` (env → .env → auth.json).
- `--smoke` opt-in для тратящего smoke-чата; иначе только `/v1/models`.

## 5. Pipeline

```
providers.json
   └→ probe каждому (read-only, параллельно, таймаут)
         ├ GET /v1/models            → models[], status
         ├ (опц.) balance_endpoint   → usable_balance / balance_kind
         └ (опц. --smoke) chat       → факт ответа
   └→ live-карта доступности (память/диск)
   └→ select_candidate(role) по приоритету:
         rank = priority(role) · alive(probe) · balance_ok(threshold)
   └→ switch(model_id, provider) в target-конфиге
         ├ backup текущего active
         ├ verify: `opencode models` / smoke на новой
         └ rollback при провале verify
   └→ append в provider-health.jsonl (append-only, redacted)
```

### 5.1 Выбор кандидата (deterministic)

- **role_priority** (из `providers.json`): для `coding` → DeepSeek-V4-Flash /
  Kimi / Qwen-coder; для `vision` → Qwen3.8-Flash-Next / MiMo-V2.6-Flash; для
  `speed` → Groq/Cerebras-класс.
- Учитывать: `probe.status == ACTIVE` → моделей > 0 → usable_balance не
  критичен (< 10%) → не DEGRADED/BLOCKED.
- Первый в цепочке с фоллбэком: если кандидат на прогоне дал 429/401/пусто —
  перейти к следующему в ранге. Записать причину фоллбэка в health-лог.

## 6. Output (health-лог, append-only JSONL)

```json
{"ts":"2026-09-27T00:00:00Z","provider_id":"amd-radeon","status":"DEGRADED",
 "models_count":7,"usable_balance":null,"balance_kind":"promotional/free",
 "warning":"daily_limit_exhausted","latency_ms":410,"redacted":true}
```

Отдельно событие **switch**:
```json
{"ts":"...","event":"switch","from":"opencode-go/glm-5.3-flash",
 "to":"amd-radeon/deepseek-v4-flash","reason":"balance","verified":true}
```

## 7. Exit-статусы / статусы провайдера

Наследуем из dotfiles-спеки: `ACTIVE | DEGRADED | BLOCKED | ERROR` (0/1/2/3).
Ротатор добавляет уровень **цели**: `SWITCHED | NO_CANDIDATE | ROLLED_BACK`.

## 8. Пороги и stale-семантика

- Пороги баланса 25/10/0% — как в dotfiles-спеке.
- Stale probe (сеть/4xx/5xx) → DEGRADED/ERROR, НЕ ACTIVE; не выбираем stale.
- Balance unknown → `usable_balance: null`, warning `balance_unknown`, не
  дисквалифицирует, но понижает ранг (не доверяем неизвестному балансу).

## 9. Безопасность / границы

- **Redaction обязательна** — ключ не в output, логах, ошибках (переисп.
  `config.redact`).
- **Никогда не тратим** кредиты без явного `--smoke`/`--spend` opt-in.
- **Never мультиаккаунт-фарминг**, обход лимитов, шаринг ключей.
- Backups перед switch; авто-rollback при провале verify.
- Только 1 активный провайдер на роль в момент времени (детерминизм).

## 10. Acceptance (fixture-based, no-network)

- `probe` пустой `data: []` → BLOCKED, не кандидат.
- 401/403 → BLOCKED/DEGRADED, не кандидат.
- 429 (daily_limit) → DEGRADED + warning, следующий в ранге.
- Баланс < 10% → warning, понижение ранга.
- redaction: ключа нет в JSON/лог/health.
- select_candidate: первый живой + не низкий баланс → выбран; фоллбэк корректен.
- switch: backup + verify + rollback на провале; `verified:true` только после успеха.
- **Independent verifier обязателен** перед переводом в implemented.

## 11. Файлы

Реализовано в `tools/key-rotator/`:
- `probe.py` — Iter-0 CLI (read-only probe + opt-in smoke).
- `rotate.py` — Iter-1 CLI (failover/upgrade выбор → apply → notify).
- `providers.json` — каталог 22 провайдеров (без секретов) + итоги probe.
- `rotation.json` — роли агентов + preferred-модели по роли + пороги статусов.
- `lib/http_client.py` — curl-транспорт, 429-ретраи, 1010-детект.
- `lib/keys.py` — резолв ключа (env → .env → auth.json).
- `lib/redact.py` — краска секретов.
- `lib/notify.py` — ntfy-пуш (curl).
- `lib/router.py` — обёртка model-router (list/models/apply, kind).
- `tests/` — 61 unittest, no-network.
- `control-plane/telemetry/provider-health.jsonl` — health + switch-events.
- `tools/ecosystem-map/model-router.py` — добавлен `--kind file|config` (для
  агентов-дублей file+config в одном проекте).
- `tools/model-bench/config.py` / `client.py` — не дублируются; паттерн
  резолва/redact переиспользован в `lib/`.

## 12. Реализация: итерации

- **Iter-0 (ГОТОВО):** read-only probe по `providers.json` → live-статусы в
  health-лог (14 ACTIVE / 3 BLOCKED / 2 ERROR / 3 SKIPPED, прогон 2026-09-27).
  Без авто-switch, smoke только opt-in.
- **Iter-1 (ГОТОВО):** failover-ротация — probe/health-log → выбор кандидата
  по роли и priority → `model-router apply` (flock+backup+kind) → ntfy-пуш →
  switch-event в health-log. Dry-run по diff; `--prefer-better` апгрейд;
  провайдер здоров → агент не трогается.
- **Iter-2 (план):** onboarding NIM/Groq/Cerebras/Mistral/DeepSeek + OpenRouter
  ($10) → ключи, карточки, каталог.
- **Iter-3 (план):** cron/systemd-timer (probe+rotate) + abuz-scout (TG
  `@inbox_tools` + веб, полуавто). Balance-эндпоинты → пороги 25/10/0%.

## 13. Ссылки

- [[02-Methods/promo-provider-protocol]]
- [[01-Reference/providers]] · [[01-Reference/abuse-providers-inbox]]
- [[01-Reference/provider-cards/amd-radeon]] (пример daily-limit $1)
- dotfiles spec `promo-provider-probe-balance-hook.md`
- `tools/model-bench/client.py` · `config.py`
- [[04-Memory/facts]] · [[TASKS]]