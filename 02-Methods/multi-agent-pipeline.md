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

Это паттерн, реализованный в [[dotfiles]] v2 — эталонная реализация.

## Архитектура

### Роли агентов

| Роль | Mode | Назначение |
|------|------|-----------|
| **sysop** | primary | Инспектор (read-only аудит системы) |
| **planner** | primary | Архитектор (ADR, планы, дизайн решений) |
| **builder** | primary | Строитель (конфиги, скрипты, модули) |
| **reviewer** | subagent | Верификатор (PASS/FAIL, безопасность) |
| **domain-dev** | subagent | Доменный специалист (qtile-dev, bash-dev, util-dev...) |

### Пайплайны

```
/sysaudit    → sysop (автономный аудит)
/script      → planner → bash-dev → reviewer
/qtile       → planner → qtile-dev → reviewer
/util        → planner → util-dev → reviewer
/prompt      → builder → docs/cheatsheets/
/notify      → util-dev → reviewer
/macro       → util-dev → reviewer
/plugin      → builder → reviewer
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

### Конфигурация (opencode.json)

```json
{
  "default_agent": "planner",
  "model": "opencode/deepseek-v4-flash-free",
  "agent": {
    "planner": { "mode": "primary", "permission": { "edit": "deny", "task": { "*": "allow" } } },
    "builder": { "mode": "primary", "permission": { "edit": "allow", "task": { "reviewer": "allow" } } },
    "reviewer": { "mode": "subagent", "permission": { "edit": "deny" } },
    "domain-dev": { "mode": "subagent", "permission": { "edit": "allow" } }
  }
}
```

## Как применить к новому проекту

### Шаг 1: Аудит
Определи домены проекта. Для dotfiles: qtile, bash, утилиты. Для другого проекта могут быть: frontend, backend, infra, tests...

### Шаг 2: Роли
Создай primary-агентов (planner, builder) и subagent по доменам.

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
| Аспект | dotfiles (эталон) | SERP Factory (products) |
|--------|------------------|------------------------|
| Цель | Управление конфигами | Производство deployable-продуктов |
| Роли | sysop + planner + builder | architect + builder + infra + ux |
| Subagent | domain-dev (qtile, bash, util) | ux-dev, infra-dev, collector-dev, labeler-dev |
| Команды | 8 пайплайнов | `/interface`, `/container`, `/deploy`, `/pipeline` |
| После деплоя | — | Глубокая модернизация каждого куска |

### Когда применять
- Core-функционал продукта готов (data pipeline написан)
- Нужно: UI + Docker-сборка + деплой
- Дедлайн горит (first approximation)
- После деплоя — полный multi-agent-pipeline

### Внедрён в
- [[dotfiles]] ✅ — эталонная реализация v2
- [[SERPlux]] 🟡 — первый продукт SERP Factory (first approximation, дедлайн сегодня)

## Связанные
- Reference: [[agents]], [[commands]], [[permissions]]
- Зависит от: [[distill-pattern]] (пайплайны = дистиллированные команды)
- Питает: [[closed-loop]] (reviewer = verify-фаза), [[verifier-pattern]] (PASS/FAIL)
- Внедрён в: [[dotfiles]] ✅ (эталонная реализация v2)
