---
type: Reference
title: Abuse Providers Inbox — таблица промо-провайдеров из Telegram
description: Рабочая таблица для triage промо/реферальных провайдеров из темы «Абуз» (@inbox_tools). Lifecycle: [[02-Methods/promo-provider-protocol]].
tags: [reference, providers, abuse, promo-provider]
timestamp: 2026-09-23
---

# Abuse Providers Inbox

> Рабочая таблица для отслеживания промо-провайдеров из Telegram-темы «Абуз».
> Lifecycle и протокол приёмки: [[02-Methods/promo-provider-protocol]].
> Карточки создаются только после успешного probe (статус ≥ CALIBRATE).

## Таблица провайдеров

| ID | Название | Endpoint | Env Variable | Предложение | Источник | Статус | Приоритет | Заметки |
|----|----------|----------|-------------|----------|--------|-----------|---------|
| A-001 | **AnyModel** | `https://anymodel.org/v1` | `ANYMODEL_API_KEY` | 5M токенов за привязку Telegram; 55 моделей через один OpenAI-совместимый эндпоинт: GPT-6 Astra `cx/gpt-6-astra` $0.40/1M (1.1M конт, 96.4%), Claude Opus 5 `cc/claude-opus-5` $0.30 (93%), GPT-5.6 Sol `cx/gpt-5.6-sol` $0.20 (97.1%), Kimi K3 `kmc/k3` $0.15 (97.3%), Grok 4.6/4.7, GLM-5.3; **бесплатно: `am/free` auto-router 99.4%, `am/nemotron-3-ultra` $0.00 (97.7%)**. Ghost Mode zero-retention, оплата картой РФ | [post 831](https://t.me/inbox_tools/831) | ✅ connected | 🔥 HIGH | TRIAGE 2026-09-23: ✅ endpoint жив (401 без ключа), ✅ публичная страница аптайма, ✅ прозрачные цены (коэф×5¢/1M). ⚠️ ID моделей с вендорными префиксами (cx/, cc/, kmc/, glm/, am/). PROBE+CONNECT 2026-09-23: 85 моделей, smoke 3/3 (free/nemotron/opus-5), 6 моделей в конфиги, auth TUI+M Code. Balance ladder 404 — fallback estimated |
| A-002 | **ai.hdd.sb** | `https://ai.hdd.sb/v1` | `HDD_SB_API_KEY` | Бесплатный Grok через сторонний relay (New API style) | [post 830](https://t.me/inbox_tools/830) | 🟤 inbox | 🟡 MEDIUM | Нет истории аптайма, не гонять чувствительные данные, только text (без image/video) |
| A-003 | **AMD Radeon Cloud Token Factory** | `https://developer.amd.com.cn/radeon/api/v1` | `AMD_RADEON_API_KEY` | Официальный бесплатный API от AMD: DeepSeek-V4-Flash, DeepSeek-V4-Flash-Vision-Exp (1M контекст), Qwen3.8-Flash-Next (262K). Лимиты: 20 RPM, 8 параллельных, дневная квота ~$10 | [post 829](https://t.me/inbox_tools/829) | ✅ connected | 🔥 HIGH | **Официальный вендор**, OpenAI + Anthropic Messages, CONNECTED 2026-09-23: ✅ 3 модели (DeepSeek-V4-Flash, Qwen3.8-Flash-Next, MiMo-V2.6-Flash), ✅ один ключ для всех, ✅ добавлен в TUI/M Code/dotfiles |
| A-004 | **EIRouter** | `https://eirouter.ai` | `EIROUTER_API_KEY` | GPT-6 Astra $1/1M, Claude Fable 5.1 $2.55/1M, Claude Opus 5 $1.28/1M (в 10x дешевле официального). $5 на баланс за регистрацию | [post 799](https://t.me/inbox_tools/799) | 🟤 inbox | 🔥 HIGH | Новый сервис, требует probe |
| A-005 | **TokenBom** | `https://tokenbom.com` | `TOKENBOM_API_KEY` | Биржа провайдеров: 500-750 кредитов на старте, бесконечный баланс через рефералов (+200 за каждого). GPT-5.6, Grok-4.6, DeepSeek-v4, Claude. API-ключ под конкретную модель + провайдера | [post 787](https://t.me/inbox_tools/787) | 🟤 inbox | MEDIUM | Интересен для масштабирования, но сложнее подключение |
| A-006 | **TabiToken** | `https://tabitoken.com` | `TABITOKEN_API_KEY` | Раздача 10 ключей по $120 каждый | [post 789](https://t.me/inbox_tools/789) | 🟤 inbox | MEDIUM | Требует проверки актуальности ключей |
| A-007 | **DeepSeek bloodthemes** | `https://deepseek.bloodthemes.ru/v1` | `DEEPSEEK_BLOODTHEMES_API_KEY` | Безлимитный DeepSeek: v4 pro, v4 flash, expert, reasoner | [post 791](https://t.me/inbox_tools/791) | 🟤 inbox | 🟡 MEDIUM | Сторонний relay, требует probe |
| A-008 | **freeai.up.railway.app** | `https://freeai.up.railway.app/v1` | `FREEAI_RAILWAY_API_KEY` | $10,000 для Claude Opus 5 (модель `claude-opus-5`) | [post 798](https://t.me/inbox_tools/798) | 🟤 inbox | 🟡 MEDIUM | API key redacted в посте, нужно запросить |
| A-009 | **nova.vcrauo.com** | неизвестен | `NOVA_VCRAUO_API_KEY` | Новый шлюз с официальными моделями, бонус за регистрацию (нужен GitHub с отлегой 1 год) | [post 796](https://t.me/inbox_tools/796) | 🟤 inbox | 🟡 MEDIUM | Требует GitHub 1+ год |
| A-010 | **ai.furry.vg** | неизвестен | `AI_FURRY_VG_API_KEY` | GPT-6 Astra, Claude Fable 5, бонус за регистрацию | [post 795](https://t.me/inbox_tools/795) | 🟤 inbox | 🟡 MEDIUM | Под абуз |
| A-011 | **htai91.com** | неизвестен | `HTAI91_API_KEY` | $50 на баланс, GPT-5.6-Thinking, Claude Sonnet 5 Thinking, DeepSeek-v4-flash, GLM-5.2, Minimax-m3, Step-3.7, Grok (4.20, 4.3, 4.6). Поштучная тарификация: $0.01-0.05 за запрос | [post 790](https://t.me/inbox_tools/790) | 🟤 inbox | 🟡 MEDIUM | Закрытые корпоративные пулы (префиксы m365, nv, gk) |
| A-012 | **tokenin.my.id** | неизвестен | `TOKENIN_MY_ID_API_KEY` | FREE модели: Kimi K3, DeepSeek V4 Pro, GPT 5.6 Sol | [post 786](https://t.me/inbox_tools/786) | 🟤 inbox | MEDIUM | Referral code A8E44FFB43 |
| A-013 | **Meta Muse** | `https://introducing.muse.ai/` | — | Персональный агент Muse, до 100M токенов в неделю бесплатно, работает на Muse Spark 1.3 | [post 824](https://t.me/inbox_tools/824) | 🟤 inbox | 🟡 MEDIUM | iOS/Android, пока отдельные регионы, не API-шлюз |
| A-014 | **NVIDIA build.nvidia.com** | `https://build.nvidia.com` | — | MoonshotAI Kimi K3 (и другие модели) | [post 816](https://t.me/inbox_tools/816) | 🟤 inbox | 🟡 MEDIUM | Официальный NVIDIA, требует проверки |
| A-015 | **free-coding-models** | `https://github.com/vava-nessa/free-coding-models` | — | Каталог бесплатных моделей кодирования от 20+ провайдеров в реальном времени | [post 812](https://t.me/inbox_tools/812) | 🟤 inbox | 🟡 MEDIUM | Агрегатор/каталог, не провайдер |

## Статусы

- 🟤 **inbox** — добавлено из Telegram, не проверено
-  **triage** — первичная оценка источника и условий
- 🔵 **probe** — проверка endpoint, `/v1/models`, smoke-чат
- 🟢 **calibrate** — оценка баланса, лимитов, proxy
- ✅ **connected** — подключено в конфиги (TUI/M Code/dotfiles)
- ❌ **blocked** — не работает (нет моделей, недоступен, ToS violation)
- ⚫ **retired** — абуз умер, отключено

## Приоритеты

- 🔥 **HIGH** — официальный вендор или очень выгодное предложение
- 🟡 **MEDIUM** — интересно, но требует осторожности
-  **LOW** — низкий приоритет

## Следующий шаг

Начинаем с **A-003 AMD Radeon Cloud Token Factory** (официальный вендор, стабильность).

---

## История изменений

- **2026-09-23:** Создана таблица, добавлено 15 провайдеров из темы «Абуз» (posts 785-831)
