# Task spec: команда /prov (роутинг провайдеров)

## Контекст маршрута
- Пользователь ЯВНО поручил исполнение build и запретил meta/general (нерабочие модели). Делегация запрещена — исполняй САМ, все три правки.
- Правило «librarian не редактирует напрямую» относится к librarian; ты здесь назначенный исполнитель. Повторных подтверждений не запрашивай — scope подтверждён.
- Коммитов нет. Код приложений не трогается.

## Создать файл 1: /home/rudra/.config/opencode/providers.json
Реестр сокращений. Дефолты — ориентиры; актуальные модели команда подтягивает при каждом запуске.

```json
{
  "lnl": { "provider": "linaliapi", "medium": "linaliapi/anthropic/claude-opus-5", "free": "linaliapi/z-ai/glm-5.3", "note": "модели условно равнозначны; режимы — ориентиры" },
  "ocg": { "provider": "opencode-go", "medium": "opencode-go/glm-5.3-flash", "free": null, "note": "free нет: брать бесплатные у провайдера opencode (zen); medium кандидаты: glm-5.3-flash (2x usage), gpt-5.6-luna; добор deepseek/qwen" },
  "oc":  { "provider": "opencode", "medium": null, "free": null, "note": "opencode zen — источник free-моделей для ocg" },
  "orr": { "provider": "openrouter", "medium": null, "free": null, "note": "заглушка, пока не используется" },
  "mst": { "provider": "mistral", "medium": null, "free": null, "note": "заглушка, пока не используется" },
  "jwk": { "provider": "justwoker", "medium": null, "free": null, "note": "заглушка, пока не используется" }
}
```

## Создать файл 2: /home/rudra/.config/opencode/command/prov.md
Дословно:

```markdown
---
description: Роутинг модели провайдера. /prov <сокр> <медиум|фри> [g] — g = глобально (dotfiles), иначе локально (opencode.json текущего проекта)
---

# /prov — роутинг провайдера

Аргументы: `$ARGUMENTS`

## Шаги

1. Разбери `$ARGUMENTS`: `<сокр> <режим> [g]`. Режимы: `медиум|medium` → `medium`, `фри|free` → `free`. Токен `g` = глобальный scope. Пусто/нераспознано — покажи таблицу сокращений из реестра и остановись.
2. Прочитай реестр `/home/rudra/.config/opencode/providers.json`. Неизвестное сокращение — перечисли известные и остановись.
3. Определи целевой файл:
   - локально: `opencode.json` в корне текущего проекта (нет файла — создай минимальный `{"$schema": "https://opencode.ai/config.json"}`);
   - глобально: `/home/rudra/dotfiles/opencode-global/.config/opencode/opencode.jsonc`.
4. Подтяни актуальный список моделей целевого провайдера (`opencode models` CLI; если недоступен — `provider.<id>.models` глобального конфига). Реестр — только сокращения/дефолты; источник правды по моделям — живой список.
5. Особый случай `free` у провайдера без бесплатных моделей (`ocg`): возьми бесплатные модели провайдера `opencode` (zen), итоговая модель = `opencode/<model-id>`.
6. Предложи модель (для `medium` приоритет: glm-5.3-flash (2x usage), gpt-5.6-luna; добор deepseek/qwen, релевантные агенту; для `free` — бесплатные). Дождись явного подтверждения пользователя. Без «да» конфиг не менять.
7. После подтверждения поменяй ТОЛЬКО поле `model` целевого файла (значение `<provider>/<model-id>`), остальное не трогай.
8. Отчёт: провайдер, режим, старая → новая модель, путь. Напомни перезапустить opencode (конфиг не hot-reload).
```

## Правка 3: /home/rudra/Projects/OpenCode-Vault/01-Reference/commands.md
Прочитай файл, найди секцию с таблицей глобальных команд, добавь строку (подстрой под колонки):
`/prov` | `~/.config/opencode/command/prov.md` | Роутинг модели провайдера: `/prov <сокр> <медиум|фри> [g]`

## Верификация (обязательно)
1. `jq . /home/rudra/.config/opencode/providers.json` — валидность.
2. Прочитать первые строки `prov.md` — frontmatter на месте, `$ARGUMENTS` присутствует.
3. Показать абсолютные пути трёх затронутых файлов.

## Запреты
- Не коммитить. Не трогать opencode.json / opencode.jsonc. Не создавать иных файлов.
