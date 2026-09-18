---
type: Method
status: stable
tags: [method, architecture, multi-agent]
---
# Multi-Agent Pipeline

## Проблема
Один агент на все задачи = нет разделения ролей, нет проверки качества, нет специализации. Ручное управление конфигами/скриптами/автоматизацией — каждый раз новый промпт, нет воспроизводимости.

## Решение
Мульти-агентная архитектура с пайплайнами: специализированные агенты связаны в цепочки задач, каждая с проверкой качества. Память и UX-профиль делают агентов осознанными — они знают для кого работают.

С 2026-09-17 эталон перешёл на модель **один primary + плоская иерархия субагентов** (ADR-010): primary сам анализирует/проектирует/пишет и по необходимости `task`-ает субагентов; субагенты не оркестрируют друг друга.

Это паттерн, реализованный в [[dotfiles]] v3 — эталонная реализация.

## Архитектура

### Роли агентов (v3 — один primary)

| Роль | Mode | Назначение |
|------|------|-----------|
| **sysop** | primary | Оператор-оркестратор: анализ, проектирование, код, делегирование субагентам |
| **planner** | subagent | Стратег/ADR (проектирование, код не пишет) |
| **builder** | subagent | Строитель конфигов/скриптов по спеку |
| **reviewer** | subagent | Read-only ревью (PASS/FAIL, безопасность) |
| **verifier** | subagent | Верификатор применимости (синтаксис, dry-run) |
| **domain-dev** | subagent | Доменный специалист (qtile-dev, bash-dev, util-dev, stow-ops...) |
| **system-audit** | subagent (global) | Read-only аудит системы/экосистемы |
| **system-ops** | subagent (global) | High-risk apply planning (approval-gated) |

### Пайплайны (sysop — точка входа каждой команды)

```
/sysaudit    → sysop → system-audit (read-only аудит)
/script      → sysop → bash-dev → reviewer
/qtile       → sysop → qtile-dev → reviewer
/util        → sysop → util-dev → reviewer
/prompt      → sysop → docs/cheatsheets/
/notify      → sysop → util-dev → reviewer
/macro       → sysop → util-dev → reviewer
/plugin      → sysop → builder → reviewer
/loop        → sysop → verifier (closed-loop build→verify→fix)
```

### Память

```
.opencode/memory/
├── user-profile.md    ← кто пользователь, UX-предпочтения, anti-goals
└── decisions.md       ← реестр ADR (архитектурные решения)
```

**user-profile.md** — ключевой файл. Все агенты читают его перед работой. Содержит:
- Кто пользователь, как работает
- Стек инструментов
- Что ценит (визуально, функционально)
- Anti-goals (чего НЕ хочет)
- Контекст системы (OS, DE, paths)

### Конфигурация (v3 — `.md`-канон)

Канон агента — `.md`-файл в `.opencode/agent/` (или глобальном
`~/.config/opencode/agent/`), frontmatter задаёт description/mode/model/permission:

```json
{
  "default_agent": "sysop",
  "model": "opencode/deepseek-v4-flash-free"
}
```

`opencode.json` больше не дублирует agent-блоки ядра: primary и субагенты
определены `.md`-frontmatter'ом (`sysop.md`, `planner.md`, `builder.md`,
`verifier.md`, domain-dev'ы).

## Как применить к новому проекту

### Шаг 1: Аудит
Определи домены проекта. Для dotfiles: qtile, bash, утилиты. Для другого проекта могут быть: frontend, backend, infra, tests...

### Шаг 2: Роли
Создай primary-агента (один, оркестратор) и субагентов по доменам и по
каноническим ролям (planner/builder/verifier/domain-dev/reviewer).

### Шаг 3: Пайплайны
Для каждого типа задачи создай команду-пайплайн в `.opencode/command/`.

### Шаг 4: Память
Создай `.opencode/memory/user-profile.md` и `.opencode/memory/decisions.md`.

### Шаг 5: Безопасность
- reviewer: `edit: deny`, только PASS/FAIL
- domain-dev: ограниченный bash whitelist
- Никаких секретов в репо

## Когда применять
- Проект с несколькими доменами (конфиги, скрипты, код, инфра)
- Задачи повторяются ≥3 раз
- Нужна проверка качества (reviewer)
- Нужна специализация (domain-dev)

## Когда НЕ применять
- Простой проект с одним типом задач
- Нет повторяющихся паттернов
- Один агент справляется

## Variant: Software Factory (SERP Factory)

Для продуктов, где ядро готово, а нужна обёртка (UI + Docker + Deploy), применяется
**Factory variant** — облегчённая версия multi-agent-pipeline с фокусом на сборку продукта.

### Отличия от эталона (dotfiles)
| Аспект | dotfiles (эталон v3) | SERP Factory (products) |
|--------|------------------|------------------------|
| Цель | Управление конфигами | Производство deployable-продуктов |
| Роли | sysop (primary) + planner/builder/domain-dev/reviewer | build + plan + domain-dev |
| Subagent | domain-dev (qtile, bash, util, stow-ops) + planner/builder | ui-dev, infra-dev, collector-dev, reviewer |
| Команды | 9 пайплайнов | `/interface`, `/container`, `/deploy` |
| После деплоя | — | Глубокая модернизация каждого куска |

### Когда применять
- Core-функционал продукта готов (data pipeline написан)
- Нужно: UI + Docker-сборка + деплой
- Дедлайн горит (first approximation)
- После деплоя — полный multi-agent-pipeline

### Внедрён в
- [[dotfiles]] ✅ — эталонная реализация v3 (один primary + субагенты, 2026-09-17)
- [[SERPlux]] ✅ — первый продукт SERP Factory (6 агентов, 3 команды)
- [[dv-hub]] ❌ — 5 агентов, но без пайплайнов-команд
- [[vault]] ✅ — 1 агент (librarian) = чистый «один primary» паттерн

## Связанные
- Reference: [[agents]], [[commands]], [[permissions]]
- Зависит от: [[distill-pattern]] (пайплайны = дистиллированные команды)
- Питает: [[closed-loop]] (reviewer = verify-фаза), [[verifier-pattern]] (PASS/FAIL)
- Внедрён в: [[dotfiles]] ✅ (эталонная реализация v2)
