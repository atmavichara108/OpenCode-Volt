---
type: Specification
title: Scope, worktree и commit isolation для агентных сессий
description: Жёсткое ограничение scope, физическая изоляция worktree и staged-scope защита от самовольных действий агентов.
timestamp: 2026-09-25
kind: task
tags: [agents, safety, scope, worktree, git, orchestration]
---

# Scope, worktree и commit isolation

## Проблема

Самовольные действия моделей не являются нормой. Сейчас scope в основном
передаётся текстом prompt-а, а permission означает общую способность агента,
но не точный manifest текущей задачи. `steps` ограничивает длину, но не
правильность действий. Pre-commit уже блокирует прямой commit в `main`, но не
проверяет ожидаемую ветку, approved scope, staged-файлы и смену ветки.

Общий рабочий каталог также не даёт физической изоляции: отдельная ветка на
сессию не равна отдельному worktree. В результате агент может увидеть или
затронуть контекст другой сессии, а branch preflight может устареть между
проверкой и commit.

## Инцидент как evidence

- Коммит `516d54e` с model-bench правками оказался в
  `task/lit-project-bootstrap`, хотя рабочим scope считалась
  `task/tails-2026-09-19`.
- Verifier расширил acceptance scope на локальный
  `OpenCode-Vault/opencode.json`, хотя файл не входил в согласованный manifest.
  Изменение не было принято и файл не был затронут.
- Зациклившийся verifier ранее показал второй класс риска: permission-gap плюс
  невыполнимый prompt может сжечь кредиты без жёсткого шага/FAIL guard.

## Цель

Агент не может молча:

1. выйти за approved file/directory manifest;
2. сменить ветку или worktree текущей сессии;
3. включить внешний файл в acceptance scope;
4. закоммитить staged-файл вне manifest;
5. продолжить при отсутствии route, scope, permission или acceptance boundary.

## P0 — обязательный протокол уже сейчас

Перед каждой mutable delegation librarian фиксирует:

- intent;
- project/repository и абсолютный root;
- ожидаемую ветку и session/worktree id;
- approved file/directory manifest;
- запрещённые файлы/директории;
- mutability и risk;
- reviewer route;
- verifier acceptance boundary;
- evidence и stop conditions.

Перед commit/push обязательно повторно проверить:

- `git branch --show-current` совпадает с ожидаемой веткой;
- `git status --short` и staged-файлы;
- каждый staged path входит в approved manifest;
- не было `git checkout`/`git switch`;
- reviewer verdict предшествует verifier acceptance;
- неожиданный файл означает STOP, а не автоматическое расширение scope.

## P1 — физическая изоляция

Каждая сессия работает в отдельном worktree:

```text
worktrees/
  task-tails-2026-09-19/
  task-lit-project-bootstrap/
  task-other/
```

Агенту запрещены смена ветки и worktree внутри сессии. Нельзя считать одну
общую рабочую директорию изолированной только потому, что сессии используют
разные branch names.

## P2 — staged-scope guard

Commit guard проверяет:

```text
approved scope = {files...}
staged files ⊆ approved scope
current branch == approved branch
```

При нарушении commit блокируется независимо от решения модели. Существующая
проверка `main/master` недостаточна: она не заменяет staged-scope guard.

## P3 — runtime scope guard

Исследовать реальную поддержку runtime/plugin API. Если API позволяет,
реализовать tool-level guard:

- edit/write вне manifest → deny;
- `git checkout`/`git switch` → deny;
- commit/push без explicit approval → deny;
- чтение секретных файлов → deny;
- выход за approved project root → deny.

Если runtime не предоставляет manifest-aware hook, не считать маркер в prompt-е
за guard. Использовать физический worktree, wrapper-команды и pre-commit
проверки; отсутствие механизма фиксировать как BLOCKED, а не маскировать.

## Acceptance criteria

- (a) Две параллельные сессии получают разные worktree и не меняют друг другу
  `HEAD`, рабочие файлы или staged state.
- (b) Попытка сменить branch/worktree из агентной сессии блокируется и оставляет
  evidence.
- (c) Commit со staged path вне approved manifest блокируется.
- (d) Acceptance verifier помечает внешний файл `OUT_OF_SCOPE`, а не расширяет
  scope и не превращает внешний файл в FAIL текущей задачи.
- (e) Reviewer quality verdict идёт до verifier acceptance; отсутствие route,
  scope или acceptance boundary даёт `UNROUTABLE`/`BLOCKED`.
- (f) Тесты fixture-based, без сети, без секретов и без мутации application
  code.
- (g) Rollback описан и проверен для каждого изменяемого guard/worktree.

## Ownership и порядок

- `meta`: agent infrastructure, runtime/tool permissions и guard implementation;
- `reviewer`: read-only quality review;
- `verifier`: independent acceptance;
- librarian: route decision, manifest, handoff и evidence record;
- project build-agent: application code не входит в эту задачу.

Порядок: P0 protocol → P1 worktree isolation → P2 staged-scope guard → P3
runtime guard. Каждый этап отдельная mutable delegation с отдельным review и
verifier acceptance. При scope gap — STOP.

## Статус

`planned`. Эта спека фиксирует обязательный план и acceptance boundary; она не
утверждает, что guards уже реализованы.
