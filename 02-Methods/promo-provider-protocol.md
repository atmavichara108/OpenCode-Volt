---
type: method
status: 🟡
tags: [method, providers, promos, balance-hook]
---
# Promo-provider protocol — проверка и подключение промо/реферальных провайдеров

> Reusable-метод приёмки OpenAI-compatible провайдеров с промо/реферальными
> кредитами (акции, бесплатные и условно-бесплатные балансы, реферальные
> остатки) в экосистему OpenCode. Статус `🟡` — метод и карточки внедрены,
> automation-хук (probe + balance monitor) ещё не реализован (spec:
> /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md).

## Intent и границы

- **Внутри scope:** легальные промо/реферальные кредиты, бесплатные и условно
  бесплатные аккаунты, реферальные остатки, выданные самим провайдером или его
  официальной реферальной программой.
- **Вне scope (запрещено):** обход ToS, обход rate-limit, multi-account abuse,
  шаринг кредов/ключей, любая автоматизация трат без явного решения оператора.
- Метод отвечает за **приёмку и наблюдение** провайдера; тратить баланс —
  решение оператора, а не метода и не хука.

## Lifecycle

```
INBOX → TRIAGE → PROBE → CALIBRATE → CONNECT → VERIFY → ACTIVE
                                                  ↘ DEGRADED → RETIRED
```

- **INBOX** — провайдер упомянут/прислан, ничего не проверено.
- **TRIAGE** — фиксация источника, домена, условий, ownership, expiry.
- **PROBE** — read-only диагностика endpoint'а и списка моделей.
- **CALIBRATE** — сверка фактического usable balance vs displayed/referral.
- **CONNECT** — подключение по правилу ID (см. ниже), без ключей в конфиге.
- **VERIFY** — независимое подтверждение (smoke-чат, verifier/свидетельство).
- **ACTIVE** — рабочий провайдер, мониторится хуком.
- **DEGRADED** — отвечает, но `data: []` / баланс непригоден / 4xx-5xx / proxy
  обязателен. НЕ становится default.
- **RETIRED** — decommissioned, карточка переведена в архив-статус.

## TRIAGE

Перед любым запросом фиксируется: **source** (откуда узнали/реферальная
программа), **domain/endpoint**, **условия промо** (что обещано, на чём
держится), **ownership** (чей аккаунт/ключ), **expiry** (когда сгорает).
Неопределённые поля помечаются `[проверить]`.

## PROBE (read-only)

Порядок, каждый шаг — без мутаций и без вывода секретов:

1. **DNS/TLS** — резолв домена, валидность TLS-цепочки.
2. **`GET /v1/models` с auth** — аутентифицированный запрос; убедиться, что
   endpoint отвечает и контракт OpenAI-compatible.
3. **Непустой model list** — `data` непуст и содержит ID моделей.
4. **Smoke-чат** — один запрос на самой дешёвой/безопасной модели; фиксируется
   факт ответа, не содержимое.
5. **OpenAI-compatible contract** — baseURL `/v1`, формат запросов/ответов.
6. **Proxy requirement** — нужен ли прокси для доступа (да/нет).

Правило: **`data: []` = `DEGRADED`/`BLOCKED`**, даже если dashboard показывает
ненулевой баланс. Пустой список моделей — провайдер не даёт API-доступных
моделей, баланс непригоден, подключение не выполняется.

## CALIBRATE

- **Usable balance** (что реально тратится через API) vs **displayed/referral
  balance** (что показывает dashboard) — могут не совпадать.
- **Currency**, **expiry**, **per-model availability**, **rate limits**,
  **proxy** — фиксируются в карточке.
- Displayed balance без подтверждённой API-спендируемости = `[проверить]`.

## CONNECT

- **Provider ID в конфиге должен совпадать с ID записи в auth-сторе**
  ([[04-Memory/facts]] § LinaliAPI: ID провайдера = ключу записи в auth.json —
  тогда `apiKey` подтягивается автоматически).
- **`apiKey` в конфиге не хранится** — только auth-стор локально.
- TUI / M Code / dotfiles — **отдельные цели подключения**; подключение одного
  не означает подключение остальных.
- **Никогда не делать непроверенного провайдера default.**

## Provider card schema

Файл-карточка: `01-Reference/provider-cards/<provider_id>.md`. Поля:

| Поле | Описание |
|------|----------|
| `provider_id` | ID провайдера (должен = auth-store ID) |
| `endpoint` | baseURL `/v1` |
| `compatibility` | OpenAI-compatible / New API / One API / иное |
| `status` | INBOX/TRIAGE/PROBE/CALIBRATE/CONNECT/VERIFY/ACTIVE/DEGRADED/BLOCKED/RETIRED |
| `checked_at` | дата последней проверки |
| `source` | источник/реферальная программа |
| `account_kind` | promotional/provider account, user/promotional referral, … |
| `initial_balance` | `{amount, currency, kind, observed_at}` |
| `current_balance` | `{amount, currency, kind, observed_at, source}` |
| `models` | список подтверждённых ID моделей |
| `probe_evidence` | что проверено и чем (TUI smoke, /v1/models, чат-проб) |
| `proxy` | требуется / нет / optional |
| `expiry` | когда сгорает баланс/промо |
| `risks` | явные риски и `[проверить]` |
| `next_action` | следующий шаг |
| `config_targets` | TUI / M Code / dotfiles — куда подключён |

В карточке явно отделяются **подтверждённые факты** от `[проверить]`. Ключи API
в карточку не попадают.

## Balance hook contract

Hook (spec: /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md) — read-only
наблюдатель, не тратит и не мутирует:

- **Read-only** и **opt-in** (запускается только для провайдеров из карточек с
  явным opt-in).
- **Без вывода секретов** — ключи читаются только из локального auth-стора,
  в лог/JSON не попадают.
- **Refresh interval** — периодический re-probe (напр. раз в сутки или по
  событию).
- **Warning thresholds** — 25% / 10% / 0% usable баланса.
- **Stale/error states** — если probe не отработал (сеть/4xx/5xx) — статус
  `DEGRADED`/`ERROR`, не «всё ок».
- **No automatic spending, no config mutation.**
- **Notification sink** — отдан на реализацию dotfiles (desktop/Telegram
  adapter опционально); метод фиксирует только контракт, не реализацию.

## Acceptance checklist

- [ ] Карточка в `01-Reference/provider-cards/` с полным schema.
- [ ] PROBE пройден: непустой `data`, smoke-чат на дешёвой модели, контракт
      OpenAI-compatible, proxy зафиксирован.
- [ ] CALIBRATE: usable vs displayed balance задокументированы, `[проверить]`
      на неподтверждённых полях.
- [ ] CONNECT: provider ID = auth-store ID, `apiKey` вне конфига.
- [ ] VERIFY: независимое свидетельство (verifier/повторный smoke) — без него
      статус не ACTIVE.
- [ ] Hook opt-in оформлен (после внедрения dotfiles).

## Decommission procedure

1. Проверить, что провайдер не default и не зашит в конфиг-блоках TUI/M Code.
2. Удалить/отключить config-блок и auth-запись (ключ не выводить).
3. Перевести карточку в `RETIRED` с причиной и датой; факты — в
   [[04-Memory/facts]] при необходимости.

## Reserved: telemetry slot

Место под будущую measured-телеметрию `control-plane/telemetry/provider-usage.jsonl` (append-only, schema: provider_id/model_id/tokens/cost_estimate/source/checked_at). Реализуется отдельной сессией. Провайдеры без balance-API (AnyModel, AMD-вероятно) будут feed'ить туда из usage полей ответов.

## Ссылки

- [[01-Reference/providers]] — обзор провайдеров и бесплатных лимитов.
- [[01-Reference/provider-cards/linaliapi]] · [[01-Reference/provider-cards/justwoker]] — первые карточки.
- [[02-Methods/model-routing]] — политика выбора модели под роль.
- [[04-Memory/facts]] — реестр фактов (ID= auth-store ID и др.).
- [[04-Memory/active-context]] · [[TASKS]] — текущий фокус и задачи.
- /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md — spec hook'а.
