---
type: Protocol
title: Canonical Execution Specs
status: approved
---
# Canonical Execution Specs

`06-Specs/<project>/` — canonical source of truth для execution specs всех
проектов, кроме approved exception SERPlux. SERPlux authoritative specs живут
только в `/home/rudra/Projects/serp/docs/specs/` и читаются локальным `/spec`.

## Layout and naming

```text
06-Specs/<project>/
├── README.md                 # optional project index and local notes
└── <spec-name>.md            # one execution spec per deterministic name
```

`<project>` — canonical project key (`dv-hub`, `ChaT`, `AndroidOS` и другие,
кроме SERPlux),
а имя spec — lowercase kebab-case с версией или task id при необходимости.
Путь обязан быть детерминированным:
`/home/rudra/Projects/OpenCode-Vault/06-Specs/<project>/<spec>.md`.

## Ownership and lifecycle

- Vault librarian владеет canonical placement, naming и protocol metadata.
- Проектный агент читает spec до изменения кода или конфигурации.
- Для обычных проектов правки execution spec выполняются только в Vault;
  локальный pointer допускается лишь для discoverability и не является
  источником правды. Для SERPlux правки выполняются только в
  `serp/docs/specs/`; Vault-артефакты SERPlux архивны.
- Новый spec сначала проверяется на существующий canonical spec; дубликаты и
  случайные `docs/spec*` как альтернативный источник запрещены.
- Approval, commit, tag, verifier и иные gates из spec обязательны.
- Spec описывает инструкции и acceptance gates, но не доказывает выполнение,
  тесты, commit, tag или release readiness.

## `/spec` protocol

Запускай `/spec <project-or-spec-selector>` из любого repo. Команда сначала
читает локальные `AGENTS.md` и `README.md`, затем соответствующий canonical
spec. Для SERPlux selector разрешён только под `docs/specs/`; Vault и случайные
`docs/spec*` не используются. Для остальных проектов используется Vault.
Без selector команда показывает доступные specs или останавливается с
инструкцией. Источник не смешивается и не создаёт копии; при недоступности
обязательного источника результат — `BLOCKED` с точной причиной.

Локальный pointer может ссылаться на canonical path для discoverability, но не
должен содержать вторую версию execution instructions. Исключение SERPlux:
`docs/specs/` содержит authoritative instructions, а старые pointers остаются
только навигацией. Project-local `/spec` имеет precedence над global `/spec`.

## Spec versus other documents

- **Execution spec** — что и в каком порядке должен сделать агент, ограничения,
  gates и Definition of Done.
- **Audit** — датированный снимок находок и рисков, не инструкция к исполнению.
- **Policy** — обязательное правило governance, применяемое к нескольким работам.
- **Runbook** — повторяемая операционная процедура после принятия решений.

Audits, policies и runbooks не заменяют spec и не должны дублировать его как
конкурирующую версию.

## No-duplicate rule

Перед созданием spec проверь `06-Specs/<project>/`, историю и локальные
pointers. Если spec уже существует, обновляй canonical файл с сохранением его
идентичности или создай новую версию только при явном lifecycle decision.

## Archived SERPlux legacy artifacts

Следующие файлы сохранены в Vault для истории, но не являются execution source
of truth и не должны выбираться `/spec`:

- `06-Specs/SERPlux/spec-close-serplux-v1.0.md`
- `06-Specs/SERPlux/resolve-v1-tag-conflict.md`

Их authoritative successors находятся в
`/home/rudra/Projects/serp/docs/specs/`. При расхождении всегда действует
локальный SERPlux spec.
