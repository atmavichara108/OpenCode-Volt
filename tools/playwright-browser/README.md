# Playwright Browser — детерминированный браузерный тул (T-134)

Реализация [[02-Methods/tool-integration-pattern]]: LLM думает, браузер делает.
Порт семантики Playwright-CLI из M Code Desktop (ECO-031) в TUI-стек.

## Чем полезен
- **JS-рендеринг**: webfetch в TUI не исполняет JS — страницы-«SPA» он не читает.
  Этот тул рендерит полный DOM.
- **Снапшот → element ref**: `goto --snapshot` отдаёт ARIA-снапшот с `[ref=eN]`,
  по которому модель кликает/заполняет без vision-скриншотов (дешевле).
- **Персистентные сессии**: `state-save`/`state-load` хранят cookies/login —
  повторные заходы на авторизованные страницы без логина.
- **Read-only по умолчанию**: мутация страницы только через явные `click`/`fill`.

## Установка (уже выполнено 2026-09-06)
```bash
.venv/bin/pip install playwright
.venv/bin/playwright install chromium   # ~/.cache/ms-playwright
```

## Запуск
direnv-активация `.venv` НЕ срабатывает под GUI M Code (`sys.executable` →
AppImage, `sys.prefix=/usr`). Указывай PYTHONPATH явно:

```bash
cd /home/rudra/Projects/OpenCode-Vault
PYTHONPATH=.venv/lib/python3.14/site-packages python3 tools/playwright-browser/browser.py ...
```

## Команды

| Subcommand | Назначение | Read/write |
|------------|-----------|-----------|
| `goto --url ... [--snapshot] [--screenshot P] [--eval-js E]` | открыть страницу + снапшот/скрин/JS | read (+screenshot-файл) |
| `eval --url ... --js "expr"` | JS-выражение → значение | read |
| `click --url ... --ref eN` | клик по element-ref | **write** |
| `fill --url ... --ref eN --value V` | ввод в поле по ref | **write** |
| `state-save --path P [--url ...]` | сохранить storage state (cookies) | write (файл) |
| `state-load --path P` | сводка сохранённого state (без секретов) | read |

## Нюанс aria-ref
Клик/заполнение по `aria-ref=eN` работает только после `aria_snapshot(mode="ai")`
на том же page-instance (снапшот засеивает карту ref→element). В CLI это уже
сделано внутри `click`/`fill`. Рефы детерминированы ДОМом.

## Гарантии
- JSON на stdout (для анализа агентом); логи/progress — stderr.
- Ошибки — тоже JSON (`{"error": ..., "message": ...}`), не traceback.
- Секреты не логируются: `state-load` отдаёт только count cookies/origins.
- Сессии изолированы: storage state передаётся явно через `--state-path`/`--path`.

## Связанные
- Реализует: [[02-Methods/tool-integration-pattern]]
- Референс семантики: [[01-Reference/mcode-desktop]] § «Playwright-CLI»
- Спеки: [[06-Specs/Vault/ecosystem-registry]] (ECO-031)
- Задача: [[TASKS]] T-134, [[DEVELOPMENT-ROADMAP]] P6 #40