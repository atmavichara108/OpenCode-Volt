---
type: Execution Spec
title: <краткое название>
project: <project-key>
kind: task
status: proposed
owner: <agent>
date: YYYY-MM-DD
tags: [spec, <project>]
---

# <title>

## Назначение (kind)

- `kind: task` — одноразовая задача (feature / fix / возврат к реализации). После
  независимого verifier PASS + commit/tag переносится в `docs/specs/done/`.
- `kind: contract` — долгоживущий канонический контракт (schema / протокол /
  role-профили). **Никогда** не переносится в `done/`, остаётся в корне
  `spec-home/`. Отсутствие поля `kind` = `task`.

## Scope

Что входит и, отдельно, что НЕ входит в эту работу.

## Gates (обязательны)

- approval — explicit, до реализации;
- commit / tag — отдельные действия, не автоматические;
- verifier — независимая проверка по DoD. PASS ≠ production readiness.

## Closure

Только для `kind: task`: после независимого verifier PASS + commit/tag агент
физически переносит **этот файл** в `docs/specs/done/`. Перенос — lifecycle-шаг,
**не evidence**: факт выполнения доказывают git-история и отчёт verifier, а не
наличие файла в `done/`. `kind: contract` не переносится никогда.