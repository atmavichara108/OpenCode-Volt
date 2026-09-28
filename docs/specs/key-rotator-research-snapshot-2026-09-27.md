---
type: Research Snapshot
title: Key Rotator — research snapshot 2026-09-27
description: Live-состояние провайдеров из .env + маппинг консолидированного списка на vault-инфраструктуру. Вход для спеки key-rotator-probe-hook.md.
tags: [research, providers, key-rotator, balance, free-tier]
timestamp: 2026-09-27
status: draft
---

# Research Snapshot — Key Rotator

## 1. Состояние провайдеров в `.env` (проверено на факте наличия ключа)

> Ключи: `<SET>` = есть в `.env`/auth.json. Статус/баланс — из карточек и
> известных probe-результатов; `[проверить]` — нет доказательств.

| provider_id | env ключ | endpoint | Статус | Баланс/лимит | Заметка |
|-------------|----------|----------|--------|--------------|---------|
| `anymodel` | SET | anymodel.org/v1 | ACTIVE (bench) | 5M токенов (TG) | беспл. модели `am/free`, `am/nemotron`; кодинг-модели платные |
| `ai.hdd.sb` | SET | ai.hdd.sb/v1 | `[проверить]` | ? | free Grok relay |
| `amd-radeon` | SET | developer.amd.com.cn/.../v1 | 🟢 CALIBRATE | днев. лимит **$1** (429) | 7 моделей, ОДИН ключ; DeepSeek-V4-Flash кодинг |
| `eirouter` | SET | eirouter.ai/v1 | `[проверить]` | ? | GPT-6 Astra $1/1M |
| `tokenbom` | SET | (per-provider) | `[проверить]` | ? (рефералы) | биржа провайдеров |
| `tabitoken` | EMPTY | tabitoken.com/v1 | — | ? ($120 раздача) | ключ не заполнен |
| `deepseek.bloodthemes` | SET | deepseek.bloodthemes.ru/v1 | `[проверить]` | ? (безлимит?) | relay |
| `freeai.railway` | EMPTY | freeai.up.railway.app/v1 | — | ? ($10k? для Opus 5) | ключ не заполнен |
| `nova.vcrauo` | SET | nova.vcrauo.com/v1 | `[проверить]` | ? (нужен GitHub 1+ год) | шлюз |
| `ai.furry.vg` | SET | ai.furry.vg/v1 | `[проверить]` | ? | GPT-6 Astra, Claude Fable 5 |
| `htai91` | SET | htai91.com/v1 | `[проверить]` | ? ($50) | поштучная |
| `tokenin.my.id` | SET | tokenin.my.id/v1 | `[проверить]` | ? (FREE: Kimi K3, DeepSeek V4 Pro, GPT 5.6 Sol) | free-модели |
| `linaliapi` | (auth.json) | api.linaliapi.com/v1 | ✅ ACTIVE | unknown `[проверить]` | 6 моделей, шлюз |
| `justwoker` | SET | api.justwoker.icu/v1 | ⛔ BLOCKED | — | нет моделей |
| `apinex` | SET | (vault) | ACTIVE (bench) | free tier | весь провайдер free |
| `vercel` | SET (auth) | — | `[проверить]` | ? | ai sdk |
| `google`/`mistral`/`openrouter`/`opencode-go`/`agentrouter` | SET (auth) | — | ACTIVE | платные/подписка | opencode-go — текущая активная подписка |

## 2. Ключевые выводы для ротатора

1. **Ядро бесплатного кодинга** (сейчас): `opencode-go` (подписка) — это
   базовая платная опора. Среди free-провайдеров реально подтверждён рабочий
   кодинг-канал — **`amd-radeon` DeepSeek-V4-Flash** (но дневной лимит $1,
   часто 429). Остальные free-релеи `[проверить]`.
2. **Много `[проверить]`** — больше половины провайдеров не прошли probe
   (нет карточек выше CALIBRATE). Первая итерация ротатора = **только
   read-only probe всех**, чтобы снять `[проверить]`.
3. **`justwoker` BLOCKED** — нет моделей; исключить из кандидатов.
4. **`tabitoken`, `freeai.railway`** — ключи пустые; probe вернёт ERROR
   (нет auth), либо пропустить.
5. **Ежедневные лимиты** (amd-radeon $1) → ротатор должен иметь фоллбэк-цепочку
   и не залипать на одном daily-limited провайдере.

## 3. Маппинг консолидированного списка (из сессии) на vault

| Источник (из списка) | Тип | Куда в vault | Ключ нужен? | Приоритет |
|----------------------|-----|--------------|-------------|-----------|
| NVIDIA NIM (build.nvidia.com) | чистый API, $0 | `providers.json` + карточка | да (регистрация) | 🔥 высший — добавить |
| Groq | чистый API, $0 | `providers.json` + карточка | да | 🔥 высший — добавить |
| Cerebras | чистый API, free tier | `providers.json` + карточка | да | высший — добавить |
| Mistral La Plateforme (Experiment) | чистый API, $0 | `providers.json` + карточка | да | высший |
| DeepSeek direct | 5M кредитов | `providers.json` + карточка | да | высший |
| Cloudflare Workers AI | $0 дневной | `providers.json` + карточка | да | средний |
| SambaNova Cloud | 200K/день | `providers.json` + карточка | да + **карта** ⚠️ | средний |
| Together AI | signup-кредит | `providers.json` + карточка | да | средний |
| b.ai / TokenRouter(.com) / AnyAPI / LLM7 / Pollinations | агрегаторы/роутеры | `providers.json` | да | fallback-слой |
| FreeLLMAPI | self-host агрегатор | метод, отдельно | нет | инструмент (не ключ) |
| Cline Desktop / Qoder / Devin | agentic платформы (не API) | вне ротатора | — | параллельный контур |

> **Важно:** провайдеры из списка (Groq/Cerebras/NIM/Mistral/SambaNova и т.д.)
> НЕ в `.env` и НЕ в `providers.json` — их ключи ещё не заведены. Это не
> ротатор, а onboarding-задача (регистрация → probe → карточка → в ротатор).

## 4. Разрыв (gap) между инфраструктурой и целью

| Что есть | Что нужно ротатору | Действие |
|----------|--------------------|----------|
| probe-хук (read-only, dotfiles) | активный выбор + switch | спек `key-rotator-probe-hook.md` |
| model-bench client/config | переиспользовать | импортировать, не копировать |
| карточки: только 4 провайдера | карточки для Groq/Cerebras/NIM/... | onboarding новых |
| `providers.json` нет | декларативный конфиг | создать |
| нет live-карты | health-лог | создать `provider-health.jsonl` |
| TG-capture `@inbox_tools` | scout новых провайдеров | отдельный спек (не здесь) |

## 5. Следующие шаги (по приоритету)

1. ~~**Iter-0 (read-only):** probe всех провайдеров из `.env` → live-карта~~ ✅ 2026-09-27
   (14 ACTIVE / 3 BLOCKED / 2 ERROR / 3 SKIPPED → `provider-health.jsonl`)
2. ~~**Iter-1:** авто-select + switch active-модели с verify/rollback~~ ✅ 2026-09-27
   (`tools/key-rotator/rotate.py`: failover + prefer-better + ntfy, 61 тест)
3. **Iter-2:** onboarding 4-5 топовых чистых API из списка (NIM, Groq, Cerebras,
   Mistral, DeepSeek) → ключи в env/auth, карточки, в ротатор + OpenRouter $10.
4. **Iter-3 (отдельный спек):** abuz-scout — TG + web поиск новых провайдеров;
   cron/timer для периодического probe+rotate; balance-эндпоинты.

## 6. Ссылки

- `docs/specs/key-rotator-probe-hook.md` — спек фичи.
- [[01-Reference/abuse-providers-inbox]] · `01-Reference/provider-cards/`
- [[02-Methods/promo-provider-protocol]] · [[02-Methods/model-routing]]
- `tools/model-bench/config.py` · `client.py`
- `tools/telegram-capture/` (@inbox_tools, тема «Абуз»)