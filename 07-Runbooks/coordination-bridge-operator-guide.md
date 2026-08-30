---
type: Runbook
title: Coordination Bridge — руководство оператора
description: Пользовательский справочник по командам и ролям единого Git-backed bridge protocol.
tags: [runbooks, coordination, bridge, operator]
---
# Coordination Bridge — руководство оператора

> **FROZEN BY USER (2026-08-30):** Coordination Bridge не является обязательным
> workflow и не вызывается. Этот документ сохраняет historical frozen artifact;
> обычная AndroidOS работа идёт local-first без копипаста отчётов.

## Текущий пользовательский workflow

1. Открыть нужный репозиторий. Для AndroidOS: `cd AndroidOS; opencode`.
2. В AndroidOS прочитать `AGENTS.md`, затем выполнить
   `/android-plan <intent>` или отправить обычный свободный запрос.
3. Дождаться read-only status и plan, дать явное approval, затем выполнять
   только согласованный implementation slice.
4. Для отдельной потребности в host audit открыть dotfiles и выполнить
   `/sysaudit <intent>`; bridge не вызывается.
5. Для контекста использовать Vault `/ask`. Не копировать reports, handoff или
   prompts между чатами; Vault не является обязательным транспортом.

## Модель

Исторически Coordination Bridge был единым Git-backed протоколом AndroidOS для координации
AndroidOS, Vault и dotfiles. Простыми словами, это общая тетрадь Markdown в
Git с task envelope, handoff, evidence и decisions, где видна история и
provenance. Это не агент, сервис, MCP и не runtime-зависимость телефона.

Канон: `/home/rudra/Projects/AndroidOS/coordination/bridge/`, если путь доступен.
Git-backed mirror/clone может быть рабочим зеркалом, если он явно задан, но
второй source of truth создавать нельзя. Strategy остаётся в Vault, host facts
в dotfiles; bridge хранит ссылки и operational metadata, а не копии.

## Историческая reference (заморожено)

| Команда | Где доступна | Когда применять | Результат |
|---|---|---|---|
| `/bridge [intent]` | Историческая команда, frozen | Не применять | Не вызывать |
| `/android-plan [intent]` | Только AndroidOS: `.opencode/command/android-plan.md` | Текущий local-first путь планирования AndroidOS | AndroidOS plan и следующий scoped шаг; bridge не требуется |
| `/sysaudit [intent]` | Только dotfiles: `.opencode/command/sysaudit.md` | Read-only аудит host, packages, drift и Stow | Отчёт sysop; system changes не выполняются |
| `/review [scope]` | Только если определена проектом; в проверенных AndroidOS/dotfiles command dirs не обнаружена | Отдельное quality review перед verifier | Findings и reviewer verdict; acceptance не выносит |
| `/loop [goal]` | dotfiles `.opencode/command/loop.md` и глобально после Stow | Closed loop для реализации, только когда в текущем repo есть подходящий builder/verifier route | Ограниченный цикл build → verify → fix, hard stop после 5 циклов |
| `/commit [scope]` | Vault: `.opencode/command/commit.md`; проектная команда не является глобальной | Только после review, verifier, scope check и явного approval | Один scoped commit; push отдельно и только по approval |

Упоминания `/bridge`, bridge path и старого cross-repo protocol ниже сохранены
только как historical reference. Не вызывать bridge и не активировать T-108/T-109.

## Граница пользователя (текущая)

Пользователь формулирует intent в свободной форме и даёт approval. Пользователь
не переносит reports, handoff или prompts между чатами и не обязан записывать их
в Vault для обычной AndroidOS работы.

## Что делать мне

1. Открыть OpenCode в нужном репозитории.
2. В AndroidOS вызвать `/android-plan [intent]` или сделать свободный запрос.
3. Проверить read-only status, plan и `git diff`, затем явно одобрить изменения.
4. В dotfiles вызывать только `/sysaudit [intent]` при отдельной необходимости.
5. Использовать Vault `/ask` для контекста, без копипаста отчётов.

Не записывайте в bridge secrets, credentials, profile copies, raw audio или
live DB payloads. Handoff, evidence и historical decisions изменяются
append-only; cross-repo refs используют полный SHA из 40 hex-символов.

## Historical status

- **T-109:** FROZEN BY USER. Не закрывать, не активировать и не создавать PASS.
- **T-108:** FROZEN BY USER. Не продолжать permission/root experiments.
- **T-110:** FROZEN/DEFERRED BY USER. MCP не создавать.
- **AndroidOS:** следующий шаг независим от bridge: `/android-plan [PA/MVP intent]`.

## Не делать

- Не копировать bridge и не создавать второй canonical store.
- Не считать старый bridge workflow обязательным для проектной работы.
- Не редактировать активный task чужим owner без handoff.
- Не принимать branch, короткий SHA или uncommitted state за provenance.
- Не смешивать репозитории в один commit и не push без approval.
