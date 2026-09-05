---
type: Reference
title: Model Modes — Режимы выбора моделей
description: Конфигурация 3-х режимов выбора моделей для агентов: Free (бесплатный), Medium (баланс), Premium (топовый)
tags: [opencode, modes, config, routing]
timestamp: 2026-09-01
---

# Model Modes — 3 Режима выбора моделей

## Обзор

Для экономичного использования OpenCode создаются **3 программно переключаемых режима**:

| Режим | Назначение | Цена | Лучшие модели |
|-------|------------|------|---------------|
| **FREE** 🆓 | 100% бесплатные модели | $0 | Nemotron Ultra, Minimax M3, DeepSeek Flash-Free |
| **MEDIUM** ⚖️ | Сильные + бесплатные | ~$0.02/1K токенов | GPT-5.6 Luna (сильная+дешёвая), DeepSeek Free |
| **PREMIUM** 💎 | Топовые модели | ~$3-5/1K токенов | Claude Opus 5, Sonnet 4.6, GPT Codex |

---

## Реализация через OpenCode Config

### Метод 1: Model Variants (рекомендуется)

OpenCode поддерживает `variants` — разные конфигурации одной модели:

**Файл:** `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/claude-sonnet-4-6",
  "small_model": "opencode/deepseek-v4-flash-free",
  "provider": {
    "opencode": {
      "models": {
        "nemotron-3-ultra-free": {
          "variants": {
            "free": {
              "model": "opencode/nemotron-3-ultra-free"
            },
            "medium": {
              "model": "openrouter/minimax-m3:free"
            },
            "premium": {
              "model": "opencode/claude-opus-5"
            }
          }
        }
      }
    },
    "openrouter": {
      "models": {
        "gpt-5.6-luna": {
          "variants": {
            "free": { "model": "openrouter/glm-5.2:free" },
            "medium": { "model": "opencode-go/gpt-5.6-luna" },
            "premium": { "model": "openrouter/openrouter/auto" }
          }
        }
      }
    }
  },
  "permission": {
    "task": "ask",
    "edit": "ask"
  }
}
```

**Переключение:** Keybind `variant_cycle` (по умолчанию `Ctrl+Shift+V`)

---

### Метод 2: Переменные окружения

Создайте скрипт `~/bin/switch-model-mode.sh`:

```bash
#!/bin/bash
# Переключение режима моделей
# Usage: switch-model-mode.sh [free|medium|premium]

MODE=${1:-free}

case $MODE in
  free)
    export OPENCODE_MODEL="opencode/nemotron-3-ultra-free"
    export OPENCODE_SMALL_MODEL="opencode/deepseek-v4-flash-free"
    echo "✅ Mode: FREE — 100% бесплатные модели"
    echo "   Primary: opencode/nemotron-3-ultra-free"
    echo "   Small: opencode/deepseek-v4-flash-free"
    ;;
  medium)
    export OPENCODE_MODEL="opencode-go/gpt-5.6-luna"
    export OPENCODE_SMALL_MODEL="opencode/deepseek-v4-flash-free"
    echo "✅ Mode: MEDIUM — Сильные + бесплатные"
    echo "   Primary: opencode-go/gpt-5.6-luna"
    echo "   Small: opencode/deepseek-v4-flash-free"
    ;;
  premium)
    export OPENCODE_MODEL="opencode/claude-opus-5"
    export OPENCODE_SMALL_MODEL="opencode/gemini-3.7-flash"
    echo "✅ Mode: PREMIUM — Топовые модели"
    echo "   Primary: opencode/claude-opus-5"
    echo "   Small: opencode/gemini-3.7-flash"
    ;;
  *)
    echo "Usage: $0 [free|medium|premium]"
    exit 1
    ;;
esac

exec opencode
```

**Сделать исполняемым:**
```bash
chmod +x ~/bin/switch-model-mode.sh
```

---

### Метод 3: Резервные конфиги

Создайте отдельные конфиги для каждого режима:

```bash
# Создать директорию на конфиги
mkdir -p ~/.config/opencode/modes/

# FREE конфиг
cat > ~/.config/opencode/modes/free.json << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/nemotron-3-ultra-free",
  "small_model": "opencode/deepseek-v4-flash-free"
}
EOF

# MEDIUM конфиг
cat > ~/.config/opencode/modes/medium.json << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/gpt-5.6-luna",
  "small_model": "opencode/deepseek-v4-flash-free"
}
EOF

# PREMIUM конфиг
cat > ~/.config/opencode/modes/premium.json << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/claude-opus-5",
  "small_model": "opencode/gemini-3.7-flash"
}
EOF
```

**Переключение:**
```bash
# Копировать нужный конфиг
cp ~/.config/opencode/modes/free.json ~/.config/opencode/opencode.json
cp ~/.config/opencode/modes/medium.json ~/.config/opencode/opencode.json
cp ~/.config/opencode/modes/premium.json ~/.config/opencode/opencode.json

# Перезапустить OpenCode
```

---

## Модели по ролям (детальная карта)

### FREE Mode (полностью бесплатный)

| Роль | Модель | Провайдер | Комментарий |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode/nemotron-3-ultra-free` | Zen | Самая сильная бесплатная Zen |
| **Complex Tasks** | `opencode/nemotron-3-ultra-free` | Zen | Для сложной декомпозиции |
| **Research** | `opencode/deepseek-v4-flash-free` | Zen | Быстрая, дешёвая, отличная для поиска |
| **Navigation** | `opencode/deepseek-v4-flash-free` | Zen | Файловый поиск, grep |
| **Build / Implementation** | `openrouter/minimax-m3:free` | OpenRouter | 🔥 Лучшая бесплатная для кода |
| **Review** | `opencode/ling-3.0-flash-free` | Zen | Детерминированная, дешёвая |
| **Verifier** | `opencode/ling-3.0-flash-free` | Zen | Быстрый фикс проходов |
| **Fallback** | `openrouter/openrouter/free` | OpenRouter | Автоматический fallback |

### MEDIUM Mode (баланс цена/качество)

| Роль | Модель | Провайдер | Комментарий |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode-go/gpt-5.6-luna` | Go | **Сильная и дешёвая** — основная лошадка |
| **Complex Planning** | `opencode-go/gpt-5.6-luna` | Go | Для сложной декомпозиции (невозможно экономить) |
| **Build / Implementation** | `opencode-go/gpt-5.6-luna` | Go | 79%+ SWE-bench, отличный tool-calling |
| **Research** | `opencode/deepseek-v4-flash-free` | Zen | Бесплатная, быстрая для навигации |
| **Navigation** | `opencode/deepseek-v4-flash-free` | Zen | Гrep, поиск файлов |
| **Review** | `opencode/ling-3.0-flash-free` | Zen | Дешёвая review качество |
| **Verifier** | `opencode/deepseek-v4-flash-free` | Zen | Быстрый, дешёвый verifier |
| **Fallback** | `opencode/claude-sonnet-4-6` | Zen | Резерв на случай ошибок Luna |

### PREMIUM Mode (топовые модели)

| Роль | Модель | Провайдер | Комментарий |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode/claude-opus-5` | Zen | Лучшая координация/планирование |
| **Complex Planning** | `opencode/claude-opus-5` | Zen | Максимальное качество декомпозиции |
| **Build / Implementation** | `opencode/claude-sonnet-4-6` | Zen | 79.6% SWE-bench, стандарт исполнителя |
| **Code Review** | `opencode/gpt-5.3-codex` | Zen | Самый дотошный на баги/безопасность |
| **Research** | `opencode/gemini-3.7-flash` | Zen | Огромный контекст, быстрая |
| **Navigation** | `opencode/claude-sonnet-4-5` | Zen | Быстрый поиск |
| **Verifier** | `opencode/claude-sonnet-4-6` | Zen | Качественная верификация |
| **Fallback** | `opencode/claude-opus-4-6` | Zen | Максимальная надёжность |

---

## Цены (апрель 2026, ориентировочно)

| Модель | Провайдер | Ввод (входящие) | Вывод (исходящие) | Примечание |
|--------|-----------|-----------------|------------------|------------|
| **GPT-5.6 Luna** | opencode-go | ~$0.01 | ~$0.02 | Самая дешёвая strong модель |
| **Claude Sonnet 4.6** | opencode | ~$3 | ~$15 | Стандартный ценник |
| **Claude Opus 5** | opencode | ~$5 | ~$25 | Топ цена |
| **Gemini 3.7 Flash** | opencode | ~$0.03 | ~$0.12 | Дешёвая, огромный контекст |
| **DeepSeek V4 Flash-Free** | Zen | $0 | $0 | Бесплатный |
| **Nemotron 3 Ultra-Free** | Zen | $0 | $0 | Бесплатный |

---

## Примеры использования

### Быстрая навигация по проекту (FREE)
```bash
# В MEDIUM/PREMIUM режиме используйте DeepSeek для навигации
# Чтобы сэкономить токены, делайте ревью сначала на DeepSeek, потом Sonnet

# Пример: поиск функции
/research "как реализованы middleware в этом проекте?"
```

### Сложная реализация (MEDIUM/PREMIUM)
```bash
# GPT-5.6 Luna для сложной декомпозиции
/plan "создать REST API для управления пользователями с auth JWT"

# Затем build на том же Luna для точности
/build
```

### Критически важный код (PREMIUM)
```bash
# Claude Opus для сложнейших архитектурных решений
/plan "смоделировать распределённую систему с кворумом согласования"

# Claude Sonnet для кода
/build

# Review на Codex для поиска багов
/review
```

---

## Автоматизация

### Скрипт переключения с сохранением контекста

```bash
#!/bin/bash
# ~/bin/opencode-mode.sh

MODE_FILE="$HOME/.config/opencode/current-mode"

save_mode() {
  echo "$MODE" > "$MODE_FILE"
  echo "✅ Сохранён режим: $MODE"
}

load_mode() {
  if [ -f "$MODE_FILE" ]; then
    cat "$MODE_FILE"
  else
    echo "free"
  fi
}

case "$1" in
  "free")
    sed -i 's/"model":.*"/"model": "opencode\/nemotron-3-ultra-free"/' ~/.config/opencode/opencode.json
    sed -i 's/"small_model":.*"/"small_model": "opencode\/deepseek-v4-flash-free"/' ~/.config/opencode/opencode.json
    save_mode
    ;;
  "medium")
    sed -i 's/"model":.*"/"model": "opencode-go\/gpt-5.6-luna"/' ~/.config/opencode/opencode.json
    sed -i 's/"small_model":.*"/"small_model": "opencode\/deepseek-v4-flash-free"/' ~/.config/opencode/opencode.json
    save_mode
    ;;
  "premium")
    sed -i 's/"model":.*"/"model": "opencode\/claude-opus-5"/' ~/.config/opencode/opencode.json
    sed -i 's/"small_model":.*"/"small_model": "opencode\/gemini-3.7-flash"/' ~/.config/opencode/opencode.json
    save_mode
    ;;
  "status")
    echo "Текущий режим: $(load_mode)"
    ;;
  *)
    echo "Usage: opencode-mode.sh [free|medium|premium|status]"
    ;;
esac
```

---

## Связанные документы

- [[providers]] — Исследование провайдеров
- [[model-routing]] — Политика выбора модели под роль
- [[capability-routing]] — Маршрутизация по capability (ортогонально model-routing)
- [[config]] — Общая конфигурация OpenCode