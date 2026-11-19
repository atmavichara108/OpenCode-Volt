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

## Применимость (критерии пригодности)

Перед применением метода прогони задачу через рубрику семи критериев
пригодности (см. [[fail-fast]]): эффективность, применимость, эволюция,
жизнестойкость, воспроизводимость, универсальность, антихрупкость.
Двустороннее правило владельца: метод, релевантный задаче, применяется
безусловно и безупречно — целиком, со всеми шагами и гейтами, без выборочных
пропусков и вольностей; метод, не релевантный задаче, не применяется вовсе.
Напоминание владельца не требуется.

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

## Правило bench-gate для New API router (2026-09-28)

**Модель попадает в роутер New API ТОЛЬКО с пройденным бенчем.** ACTIVE-статус
провайдера (probe прошёл, endpoint жив) — необходимое, но НЕ достаточное
условие. Прежде чем модель станет каналом New API:

1. Прогон `tools/model-bench` по модели (гейты tools/build/reasoning).
2. **PASS** по порогам бенча (иначе модель кодит говнокод / криво понимает /
   выполняет случайные и вредные действия — ровно то, что канал должен
   исключить).
3. Только после PASS — регистрация канала (`newapi_sync`/admin API).

Провайдер может быть ACTIVE, но его конкретные модели — вне New API, пока не
прошли бенч. Реле (tokenin/htai91/ai-hdd-sb/ai-furry-vg/deepseek-bloodthemes)
проходят это правило строже прямых вендоров: заявленный флагман ≠ рабочий.
Архитектура слоя: [[docs/specs/newapi-gateway-layer]].

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

## Срок бесплатного периода → выпил (протокол, 2026-11-18)

Слово владельца (basis: quoted, 2026-11-18): «anymodel нужно выкинуть как и некоторых
других провайдеров которых я подключал на бесплатные периоды - для этого нужно
выработать протокол чтобы иметь механизм удаления таких провайдеров по истечении
бесплатного периода».

### Данные — блок `trial` в `tools/key-rotator/providers.json`

```json
"trial": {
  "kind": "free_period | free_tier_credits | daily_quota",
  "started": "YYYY-MM-DD",
  "expires": "YYYY-MM-DD",
  "auto_reap": true,
  "on_expiry": "delete_channels | disable_channels",
  "owner_word": "дата и суть слова владельца",
  "fact": "что подтверждено пробой"
}
```

| Поле | Смысл | Гейт |
|------|-------|------|
| `expires` | дата конца бесплатного периода | обязательна для авто-выпила |
| `auto_reap` | разрешён ли автоматический выпил по наступлении даты | `true` только по слову владельца |
| `on_expiry` | что делать с каналами: удалить или отключить (status=2) | по умолчанию `delete_channels` |
| `owner_word` | ссылка на слово владельца | обязательна для apply |

### Механизм — `tools/key-rotator/trial_expiry.py`

- `python3 tools/key-rotator/trial_expiry.py` — план (dry-run, ничего не мутирует).
- `--apply --owner-word "<слово>"` — выпил истёкших провайдеров: каналы New API
  удаляются (или отключаются), провайдер получает `skip: true` + `skip_reason`,
  в `control-plane/telemetry/provider-health.jsonl` пишется строка
  `SKIPPED / trial_expired`.
- `--force-provider <id>` — выпил по ПРЯМОМУ слову владельца, независимо от даты
  (для случая «выкинуть сейчас»: дата не подделывается, основание — owner_word).
- Без `--owner-word` — apply отказывает. Трогаются только провайдеры с явным
  `trial.expires` в прошлом И `auto_reap: true` (или прямо перечисленные в
  `--force-provider`). Платный провайдер без блока `trial` неприкосновенен.

### Регламент (кто что делает)

1. **Владелец** говорит: «провайдер X на бесплатном периоде до <дата>, убрать,
   когда истечёт» (или «выкинуть сейчас»).
2. **Ротатор** вносит блок `trial` в каталог (дата, auto_reap, on_expiry,
   owner_word) — и до даты провайдер работает как обычно.
3. **Ротатор** запускает `trial_expiry.py` (в начале хода или по таймеру):
   dry-run → отчёт владельцу → apply с owner_word.
4. **Отчёт** владельцу: что выпилено, что осталось, какие сроки ещё не заданы.

### Страховки и риски

| Риск | Защита |
|------|--------|
| Снести живого платного провайдера | только записи с явным `trial`; `auto_reap` по умолчанию false |
| Ошибка в дате | dry-run обязателен; apply требует owner_word; `fact` хранит основание |
| Провайдер понадобится снова | запись каталога остаётся (skip + skip_reason + дата) — вернуть = снять skip и перезапустить sync |
| Каналы в БД шлюза | удаление идёт по имени `provider_id|…`, abilities чистятся тем же проходом |

### Что ещё требует срока (каркас внесён, срок уточнить у владельца)

`amd-radeon` (free-ключ, суточный лимит 1 pt/день), `google` (free-ключ),
`nvidia` (free tier 1000 кредитов), `mistral` (experiment tier), `vercel`
(free-ключ). Для каждого нужно слово владельца с датой — без даты `auto_reap`
остаётся выключенным.

## Протокол добавления: временный период ↔ постоянная квота (2026-11-18)

Слово владельца (basis: quoted, 2026-11-18): «"amd-radeon, google, nvidia, mistral" —
постоянная бесплатная квота. "vercel" нужно проверять отдельно, потенциально бесплатно
с низкой квотой. нужно ещё добавить опенроутер, там очень маленькая квота, но она есть …
дополнительно создай протокол для добавления как провайдеров с бесплатным периодом
(временные) так и провайдеров с обновляемой бесплатной квотой (постоянные), причем
протокол добавления временных должен быть связан с протоколом удаления временных».

### Два типа провайдеров с бесплатной квотой

| Тип | Что значит | Поле в каталоге | Что происходит при исчерпании | Выпил |
|-----|-----------|-----------------|-------------------------------|-------|
| **ВРЕМЕННЫЙ** | бесплатный период с датой сгорания (акция, триал) | `trial` (`expires`, `auto_reap`, `on_expiry`, `owner_word`) | каналы перестают работать | **по дате, автоматически** (`trial_expiry.py`) |
| **ПОСТОЯННЫЙ** | обновляемая квота (free tier, суточный лимит) | `quota` (`kind`, `fact`, `owner_word`, `monitor`) | деградация (DEGRADED/ERROR) + сигнал владельцу | **только по слову владельца** |

Временный и постоянный — не «лучше/хуже», а разные жизненные циклы: у временного
конечна неопределённость даты (срок горит), у постоянного конечен ресурс, но срок
не горит (квота возвращается).

### Связка добавления и удаления (обязательная)

Добавление временного провайдера **не завершено**, пока не зарегистрирован срок
выпила: `onboard-temporary` пишет в каталог блок `trial` в том же формате, который
читает `trial_expiry.py`. Провайдер без `trial.expires` не может быть временным —
иначе он навсегда останется в шлюзе.

```
слово владельца (подключить + срок)
   └─ provider_lifecycle.py onboard-temporary <pid> --expires <дата> --owner-word "..."
        └─ блок trial в providers.json → тот же механизм, что читает trial_expiry.py
             └─ по наступлении даты: trial_expiry.py --apply --owner-word "..."
                  └─ каналы удалены/отключены, провайдер skip=true, health SKIPPED/trial_expired
```

### Постоянная квота: квотный гейт вместо выпила по дате

1. `onboard-permanent <pid>` → блок `quota` (без срока, `auto_reap` не выставляется).
2. `probe` пишет health-строку: ACTIVE / DEGRADED / ERROR + `balance_unknown`.
3. Исчерпание квоты → DEGRADED/ERROR → сигнал владельцу («квота кончилась, каналы
   деградировали») — решение (выкинуть / докупить / оставить) принимает владелец.
4. Если владелец решил убрать — `set-skip` + `trial_expiry.py --force-provider` (тот
   же путь выпила, что и у временных).

### Команды (`tools/key-rotator/provider_lifecycle.py`)

```bash
python3 tools/key-rotator/provider_lifecycle.py status
python3 tools/key-rotator/provider_lifecycle.py onboard-temporary <pid> --expires 2026-12-01 --owner-word "..." [--on-expiry delete_channels|disable_channels]
python3 tools/key-rotator/provider_lifecycle.py onboard-permanent <pid> [--quota-kind free_tier_credits|daily_quota] [--quota-note "..."]
python3 tools/key-rotator/provider_lifecycle.py reap [--provider <pid>] [--owner-word "..."] [--apply]
python3 tools/key-rotator/provider_lifecycle.py set-skip <pid> [--reason "..."] | clear-skip <pid>
```

`reap` — делегат к `trial_expiry.py` (одна точка входа, один гейт: owner_word).

### Регламент (кто что делает)

1. **Владелец** говорит: «подключить X, бесплатный период до <дата>, убрать когда
   истечёт» (временный) ИЛИ «подключить Y, у него постоянная бесплатная квота» (постоянный).
2. **Ротатор** вносит провайдера в каталог через `provider_lifecycle.py` (тип выбирает
   по слову владельца), затем PROBE → бенч → `newapi_sync --apply` (каналы — только
   с bench-PASS).
3. **Ротатор** держит `status` в актуальном состоянии; при наступлении срока
   (временный) — выпил с owner_word; при исчерпании квоты (постоянный) — сигнал владельцу.
4. **Отчёт** владельцу: кто временный (сколько дней осталось), кто постоянный (состояние квоты).

### Текущий реестр (18.11)

| Провайдер | Тип | Факт |
|-----------|-----|------|
| anymodel | временный (истёк 18.11) | выкинут по слову владельца: 14 каналов удалены |
| amd-radeon | постоянный (`daily_quota`) | free-ключ, суточный лимит 1 pt/день |
| google | постоянный (`free_tier_credits`) | бесплатный ключ, квота возобновляется |
| nvidia | постоянный (`free_tier_credits`) | free tier 1000 кредитов / 40 RPM |
| mistral | постоянный (`free_tier_credits`) | experiment tier, data opt-in |
| openrouter | постоянный (`free_tier_credits`) | очень маленькая квота, но есть (слово владельца) |
| vercel | `verify` | потенциально бесплатно с низкой квотой — проверяется отдельно |

## Reserved: telemetry slot

Место под будущую measured-телеметрию `control-plane/telemetry/provider-usage.jsonl` (append-only, schema: provider_id/model_id/tokens/cost_estimate/source/checked_at). Реализуется отдельной сессией. Провайдеры без balance-API (AnyModel, AMD-вероятно) будут feed'ить туда из usage полей ответов.

## Ссылки

- [[01-Reference/providers]] — обзор провайдеров и бесплатных лимитов.
- [[01-Reference/provider-cards/linaliapi]] · [[01-Reference/provider-cards/justwoker]] — первые карточки.
- [[02-Methods/model-routing]] — политика выбора модели под роль.
- [[04-Memory/facts]] — реестр фактов (ID= auth-store ID и др.).
- [[04-Memory/active-context]] · [[TASKS]] — текущий фокус и задачи.
- /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md — spec hook'а.
