---
type: project
repo: /home/rudra/Projects/serp
kind: коммерция
stack: Python 3.11+ / requests / gspread / FastAPI / DeepSeek / SQLite
---
# SERPlux

Сбор позиций Google через topvisor Snapshots API, классификация URL (DeepSeek / Zen), выгрузка в Google Sheets.

**Окружение:** Python venv. Секреты в `.env` (см. `.env.example`).
**Запуск:** `python main.py`
**CI / проверка:** `python -m pytest -q` [проверить: тестов мало, pytest разрешён]
**Провайдер:** OpenCode Zen (primary) + DeepSeek (labeler)
**Особенность:** webhook.py пуст — заготовка на будущее.

## Архитектура (пайплайн)
config → collector (topvisor) → storage (кэш) → labeler (классификация) → exporter (Sheets)

| Модуль | Роль |
|--------|------|
| topvisor.py | run_check / poll_status / get_snapshot → list[Row] |
| collector.py | collect(config) → list[Row] |
| labeler.py | label(rows, mode) → +label; кэш или LLM (DeepSeek) |
| storage.py | save / get_cached_label / get_history (SQLite) |
| exporter.py | export(rows) → Google Sheets |
| reporter.py | отчётность |
| config.py | конфиг из управляющего Google Sheet |
| webhook.py | FastAPI endpoint (пусто, план) |

Row = {date, searcher, query, geo, position, url, domain, label}

## Агенты (.opencode/agents/ + opencode.json)
| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| build | primary | opencode/claude-sonnet-4-6 | разработка, temp 0.1, steps 30, task allow |
| plan | primary | opencode/claude-sonnet-4-6 | планирование, temp 0.1, steps 20, edit/bash deny |
| collector-dev | subagent | opencode/claude-sonnet-4-6 | разработка модуля сбора (topvisor.py, collector.py) |
| reviewer | subagent | opencode/gpt-5.3-codex | ревью кода на соответствие контрактам |

> build и plan на одной модели — [[model-routing]] не разведён (🟡: только reviewer на другой модели).

## Команды
— нет —

## Плагины (.opencode/plugins/)
env-guard.js · notify.js

## Конфиг (opencode.json)
edit: allow · bash: whitelist (git/ls/cat/pytest/python) · push и rm = ask · webfetch allow · lsp on

## Состояние методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | нет команды /loop, нет автономной петли |
| [[verifier-pattern]] | ❌ | reviewer не выносит PASS/FAIL вердикт, только список замечаний |
| [[context-as-docs]] | 🟡 | docs/contracts.md + docs/decisions.md есть, но не формализованы как spec-driven |
| [[distill-pattern]] | ❌ | команд в .opencode/commands/ нет |
| [[memory-management]] | ❌ | плагинов компакции/flush нет |
| [[model-routing]] | 🟡 | build/plan/collector-dev на Sonnet 4.6, reviewer на GPT-5.3 — частичное разведение |

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-29: обновлён стек (DeepSeek labeler, Zen primary), добавлены статусы всех методов
- 2026-06-30: ревью — модели агентов добавлены (включая gpt-5.3-codex для reviewer), model-routing 🟡, стек исправлен (DeepSeek вместо google-generativeai), labeler описание актуализировано
