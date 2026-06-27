---
type: project
repo: github.com/atmavichara108/SERPlux
kind: коммерция
stack: Python 3.11+ / requests / gspread / FastAPI / google-generativeai / SQLite
---
# SERPlux

Сбор позиций Google через topvisor Snapshots API, классификация URL, выгрузка в Google Sheets.

**Окружение:** Python venv. Секреты в `.env` (см. `.env.example`).
**Запуск:** `python main.py`
**CI / проверка:** `python -m pytest -q`  [проверить: настроены ли тесты — pytest разрешён в конфиге, но тестовых файлов в дереве не видно]
**Особенность:** webhook.py и apps_script.gs пустые — заготовки на будущее.

## Архитектура (пайплайн)
config → collector (topvisor) → storage (кэш) → labeler (классификация) → exporter (Sheets)

| Модуль | Роль |
|--------|------|
| topvisor.py | run_check / poll_status / get_snapshot → list[Row] |
| collector.py | collect(config) → list[Row] |
| labeler.py | label(rows, mode) → +label; кэш или LLM (Gemini Flash) |
| storage.py | save / get_cached_label / get_history (SQLite) |
| exporter.py | export(rows) → Google Sheets |
| reporter.py | отчётность |
| config.py | конфиг из управляющего Google Sheet |
| webhook.py | FastAPI endpoint (пусто, план) |

Row = {date, searcher, query, geo, position, url, domain, label}

## Агенты (.opencode/agents/)
| Агент | Назначение |
|-------|-----------|
| collector-dev | разработка модуля сбора |
| reviewer | ревью |
| build (primary) | sonnet-4-6, temp 0.1, steps 30, task allow |
| plan (primary) | sonnet-4-6, temp 0.1, steps 20, edit/bash deny |

## Команды
— нет —

## Плагины (.opencode/plugins/)
env-guard.js · notify.js

## Конфиг (opencode.json)
edit: allow · bash: whitelist (git/ls/cat/pytest/python) · push и rm = ask · webfetch allow · lsp on

## Docs
docs/contracts.md (контракты модулей) · docs/decisions.md · docs/progress.md · docs/topvisor-api.md

## Состояние методов
| Метод | Статус |
|-------|--------|
| [[closed-loop]] | ❌ |
| [[verifier-pattern]] | ❌ |

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
