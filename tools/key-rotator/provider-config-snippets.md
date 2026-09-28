# Provider config snippets — расширение opencode.jsonc

> Готовые блоки для подключения ACTIVE-провайдеров к ротатору. Составлены из
> **живых** каталогов `/v1/models` (2026-09-28), отобраны только агентские
> модели (tool-calling + сильное следование инструкциям + приличный контекст).
> Слабые (<=2B) и узкоспециальные (парсеры/tts/image/embed) исключены.
>
> **Зачем:** ротатор (`tools/key-rotator/rotate.py`) и `model-router` роутят
> ТОЛЬКО модели, объявленные в provider-блоках конфига. Сейчас OpenCode/M Code
> видят 8 провайдеров; probe находит 14 ACTIVE. Эти блоки открывают разницу.
>
> **Почему не внёс сам:** `opencode.jsonc`/`mcode.json` — встроенный red-line
> M Code (edit запрещён на уровне ядра). Это ручная вставка оператора.

## Куда вставлять

Файлы (в каждом — ДВА блока провайдеров, надо дополнить оба):
- `~/dotfiles/opencode-global/.config/opencode/opencode.jsonc`
  (= `~/.config/opencode` = `~/.config/mcode` — симлинки на него)
  - объект `"provider"` (v1-форма: `npm` + `options`)
  - объект `"providers"` (v2-форма: `package` + `settings`)
- `~/.local/share/m-code-data/config/opencode.jsonc` (отдельный runtime M Code Desktop) — тем же содержимым

После правок: **перезапуск OpenCode и M Code** (конфиг не hot-reload).

---

## Шаг 1. Ключи в auth.json

google и mistral уже в `~/.local/share/opencode/auth.json`. Для остальных —
добавь записи (id = имя провайдера, значение — из vault `.env`). Ключи НЕ
храню в этом файле; бери из `.env`:

| provider id | .env переменная |
|---|---|
| `deepseek-bloodthemes` | `DEEPSEEK_BLOODTHEMES_API_KEY` |
| `tokenin-my-id` | `TOKENIN_MY_ID_API_KEY` |
| `ai-hdd-sb` | `HDD_SB_API_KEY` |
| `ai-furry-vg` | `AI_FURRY_VG_API_KEY` |
| `htai91` | `HTAI91_API_KEY` |

Формат записи в auth.json:
```json
"deepseek-bloodthemes": { "type": "api", "key": "<значение из .env>" }
```
(Альтернатива — inline `"apiKey": "<ключ>"` внутри `options`/`settings` блока
провайдера; auth.json чище и не светит ключ в конфиге.)

---

## Шаг 2A. Дополнить существующий `amd-radeon` (+4 модели)

Вставь ВНУТРЬ `models` обоих блоков `amd-radeon` (v1 и v2), рядом с
существующими тремя:

```json
        "DeepSeek-V4.1-Flash": { "name": "DeepSeek V4.1 Flash (1M, Vision)", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "DeepSeek-V4-Flash-Vision-Exp": { "name": "DeepSeek V4 Flash Vision Exp (1M)", "attachment": true, "reasoning": false, "tool_call": true, "temperature": true },
        "GLM-5.3-Flash": { "name": "GLM 5.3 Flash (256K)", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "Qwen3.8-27B": { "name": "Qwen 3.8 27B (Vision, 256K)", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
```

---

## Шаг 2B. Новые провайдеры — форма v1 (в объект `"provider"`)

```json
    "google": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Google AI Studio (Gemini free)",
      "options": { "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai" },
      "models": {
        "models/gemini-3.1-flash-lite": { "name": "Gemini 3.1 Flash-Lite", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-3.5-flash": { "name": "Gemini 3.5 Flash", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-3.8-flash": { "name": "Gemini 3.8 Flash", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-flash-lite-latest": { "name": "Gemini Flash-Lite Latest", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
      }
    },
    "mistral": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Mistral La Plateforme",
      "options": { "baseURL": "https://api.mistral.ai/v1" },
      "models": {
        "codestral-latest": { "name": "Codestral (coding)", "attachment": false, "reasoning": false, "tool_call": true, "temperature": true },
        "mistral-medium-latest": { "name": "Mistral Medium", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "mistral-small-latest": { "name": "Mistral Small", "attachment": false, "reasoning": false, "tool_call": true, "temperature": true }
      }
    },
    "deepseek-bloodthemes": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "DeepSeek (bloodthemes relay)",
      "options": { "baseURL": "https://deepseek.bloodthemes.ru/v1" },
      "models": {
        "deepseek-v4-pro": { "name": "DeepSeek V4 Pro", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "deepseek-v4-flash": { "name": "DeepSeek V4 Flash", "attachment": false, "reasoning": false, "tool_call": true, "temperature": true },
        "deepseek-reasoner": { "name": "DeepSeek Reasoner", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true }
      }
    },
    "tokenin-my-id": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "tokenin.my.id",
      "options": { "baseURL": "https://tokenin.my.id/v1" },
      "models": {
        "myt/claude-sonnet-5": { "name": "Claude Sonnet 5", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "myt/gpt-5.6-sol": { "name": "GPT-5.6 Sol", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "myt/gpt-5.6-luna": { "name": "GPT-5.6 Luna", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "myt/gemini-3.1-flash-lite": { "name": "Gemini 3.1 Flash-Lite", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
      }
    },
    "ai-hdd-sb": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "ai.hdd.sb",
      "options": { "baseURL": "https://ai.hdd.sb/v1" },
      "models": {
        "deepseek-v4.1-flash": { "name": "DeepSeek V4.1 Flash", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "deepseek-v4-pro": { "name": "DeepSeek V4 Pro", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "glm-5.3": { "name": "GLM 5.3", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "claude-sonnet-5": { "name": "Claude Sonnet 5", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "kimi-k3": { "name": "Kimi K3", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true }
      }
    },
    "ai-furry-vg": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "ai.furry.vg",
      "options": { "baseURL": "https://ai.furry.vg/v1" },
      "models": {
        "deepseek-ai/deepseek-v4.1-flash": { "name": "DeepSeek V4.1 Flash", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "z-ai/glm-5.3": { "name": "GLM 5.3", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "moonshotai/kimi-k3": { "name": "Kimi K3", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "gpt-5.6-sol": { "name": "GPT-5.6 Sol", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "claude-opus-4-6": { "name": "Claude Opus 4.6", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
      }
    },
    "htai91": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "htai91.com",
      "options": { "baseURL": "https://htai91.com/v1" },
      "models": {
        "m365/claude-sonnet-5": { "name": "Claude Sonnet 5", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "gw/gpt-5.6-luna": { "name": "GPT-5.6 Luna", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "nv/glm-5.3": { "name": "GLM 5.3", "attachment": false, "reasoning": true, "tool_call": true, "temperature": true },
        "cb/qwen-3.8-27b": { "name": "Qwen 3.8 27B", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
      }
    }
```

## Шаг 2C. Те же провайдеры — форма v2 (в объект `"providers"`)

Идентичны, но `npm`→`package: "aisdk:@ai-sdk/openai-compatible"` и
`options`→`settings`. `models` — те же, что выше. Пример на google:

```json
    "google": {
      "package": "aisdk:@ai-sdk/openai-compatible",
      "settings": { "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai" },
      "models": {
        "models/gemini-3.1-flash-lite": { "name": "Gemini 3.1 Flash-Lite", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-3.5-flash": { "name": "Gemini 3.5 Flash", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-3.8-flash": { "name": "Gemini 3.8 Flash", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true },
        "models/gemini-flash-lite-latest": { "name": "Gemini Flash-Lite Latest", "attachment": true, "reasoning": true, "tool_call": true, "temperature": true }
      }
    }
```
Для остальных v2-блоков возьми `models` из соответствующего v1-блока выше и
поменяй обёртку (`package`/`settings`) как у google.

---

## Шаг 3. Проверка после перезапуска

```bash
# сколько провайдеров/моделей теперь видит роутер:
.venv/bin/python tools/ecosystem-map/model-router.py models | python3 -c "import json,sys; d=json.load(sys.stdin); b={}; [b.setdefault(m['provider'],[]).append(m['id']) for m in d['models']]; print({k:len(v) for k,v in b.items()})"

# сухой прогон ротатора — увидит новых кандидатов:
.venv/bin/python tools/key-rotator/rotate.py --dry-run --prefer-better
```

Ожидаемо: провайдеров станет ~15 вместо 8; `rotate --prefer-better` начнёт
предлагать модели новых провайдеров по ролям (см. `rotation.json` preferred).

---

## Заметки по качеству (агентское исполнение)

- **Прямые вендоры** (надёжнее всего): google (Gemini Flash-Lite прошёл все
  гейты бенча), mistral (Codestral — кодинг). Приоритет в `rotation.json` уже
  отражает это.
- **Реле** (`deepseek-bloodthemes`, `tokenin-my-id`, `ai-hdd-sb`, `ai-furry-vg`,
  `htai91`): заявляют флагманы (Claude/GPT/DeepSeek), но реальное качество и
  стабильность `[проверить]` бенчем перед боевым использованием. Подключаем как
  fallback-слой, не как primary.
- **google id требует префикс `models/`** — подтверждено живым запросом
  (`models/gemini-3.1-flash-lite` → 200; без префикса → иначе).
- Флаги `attachment/reasoning/tool_call` проставлены по семейству; уточняются
  прогоном `model-bench` (§ключевые баги бенча уже исправлены, commit 772f045).
