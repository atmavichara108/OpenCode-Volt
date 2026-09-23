---
type: Provider Card
title: AMD Radeon Cloud Token Factory — provider card
description: Операционная карточка провайдера AMD Radeon Cloud Token Factory. Официальный бесплатный API от AMD. Status CALIBRATE: probe пройден, DeepSeek-V4-Flash работает.
tags: [reference, provider-card, providers, amd, radeon]
timestamp: 2026-09-23
---

# AMD Radeon Cloud Token Factory — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | AMD Radeon Cloud Token Factory |
| `provider_id` | `amd-radeon` |
| `endpoint` | `https://developer.amd.com.cn/radeon/api/v1` |
| `compatibility` | OpenAI-compatible |
| `status` | 🟢 `CALIBRATE` |
| `checked_at` | 2026-09-23 |
| `source` | официальный бесплатный API от AMD |
| `account_kind` | `promotional/free` |
| `initial_balance` | бесплатно (дневная квота ~$10, не подтверждена) |
| `current_balance` | неизвестно (квота не видна в UI) `[проверить]` |
| `models` | 7 моделей: DeepSeek-V4-Flash, GLM-5.3-Flash, MiMo-V2.6-Flash, MinerU2.5-Pro, MiniCPM5-2B, Qwen3.8-27B, Qwen3.8-Flash-Next |
| `proxy` | не нужен (работает напрямую из РФ) |
| `expiry` | неизвестен `[проверить]` |
| `risks` | китайский домен (возможны гео-ограничения), **ОДИН ключ работает для всех моделей** (подтверждено 2026-09-23), квота не видна |

## Probe результаты (2026-09-23)

### ✅ Пройдено
- DNS резолвинг: `143.64.80.214` (IPv4)
- `/v1/models`: 7 моделей доступно
- DeepSeek-V4-Flash chat: ответ "OK", 14 токенов (prompt=12, completion=2)
- Прокси: не нужен

### ️ Проблемы
- Qwen3.8-Flash-Next: ✅ работает с ключом DeepSeek (Hello → 27 токенов, reasoning 16)
- GLM-5.3-Flash: at capacity (100% загрузка)
- MinerU2.5-Pro: 0% idle + LIMITED FREE
- MiniCPM5-2B: слишком маленькая (2B параметров)
- Qwen3.8-27B: большая, но медленная (11.7% idle)

### Модельные ID (для конфига)
```json
{
  "DeepSeek-V4-Flash": { "name": "DeepSeek V4 Flash", "attachment": false, "reasoning": false, "tool_call": true, "temperature": true },
  "Qwen3.8-Flash-Next": { "name": "Qwen 3.8 Flash Next (Vision)", "attachment": true, "reasoning": false, "tool_call": true, "temperature": true },
  "MiMo-V2.6-Flash": { "name": "MiMo V2.6 Flash (Vision)", "attachment": true, "reasoning": false, "tool_call": true, "temperature": true }
}
```

## Статус

`🟢 CALIBRATE`. Probe пройден, DeepSeek-V4-Flash работает. Следующий шаг — подключение в конфиги OpenCode (TUI global, dotfiles, M Code).

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[01-Reference/providers]] — обзор провайдеров.
- [[01-Reference/abuse-providers-inbox]] — таблица всех промо-провайдеров.
- [[04-Memory/facts]] · [[04-Memory/active-context]]
