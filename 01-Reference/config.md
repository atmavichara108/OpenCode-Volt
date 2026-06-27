
# OpenCode: Конфигурация

> Выжимка из opencode.ai/docs/config. Проверено: 2026-06-26.

## Файлы конфига
- Глобальный: `~/.config/opencode/opencode.json`
- Проектный: `opencode.json` в корне проекта
- Мёрж: проектный накладывается поверх глобального → общее ядро в глобальном, специфика в проектном.

## Скелет
```
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": true,
  "permission": { ... },
  "agent": { ... },
  "command": { ... }
}
```

## Ключевое для моей схемы
- Общие агенты (verifier) → глобальный конфиг, работают во всех проектах.
- Проектные агенты/права → проектный opencode.json.
- Альтернатива JSON-конфигу — markdown-файлы в .opencode/agent/ и .opencode/command/.
- default agent должен быть primary (build/plan или свой custom).

## Провайдеры/модели
- Формат model: `provider/model-id`.
- Мои проекты на OpenCode Zen: `opencode/claude-sonnet-4-6`.
