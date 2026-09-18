---
type: Protocol
title: Canonical Execution Specs
status: approved
timestamp: 2026-09-18
---

# Canonical Execution Specs

## Одно правило (без исключений)

> **Execution spec живёт в репозитории того агента, который его исполняет.**

- Spec, который исполняет **локальный агент проекта** в своём репозитории, —
  живёт в этом репозитории: `<repo>/docs/specs/<spec>.md`.
- Spec, который исполняется **из Vault** (агентом Vault / Pip-Boy / для самого
  Vault), — живёт здесь: `docs/specs/<spec>.md` этого репозитория.
- Vault **не хранит** execution-спеки чужих проектов «на будущее» и не требует
  от проектов держать pointer-копии своих спеков. Единственный кросс-репо
  указатель — поле `spec-home` в карточке проекта (`03-Projects/<project>.md`).

## Layout

```text
# локальная спека проекта (исполняет агент проекта)
/home/rudra/<repo>/docs/specs/<name>.md

# спека, исполняемая из Vault (агент Vault / Pip-Boy)
/home/rudra/Projects/OpenCode-Vault/docs/specs/<name>.md

# runtime-состояние волта (НЕ спеки): decision queue, kanban storage
/home/rudra/Projects/OpenCode-Vault/control-plane/
```

`<project>` — canonical project key (`dv-hub`, `ChaT`, `AndroidOS`, `dotfiles`,
`SERPlux`, `vault`, …). Имя spec — lowercase kebab-case, с версией или task id
при необходимости.

## `spec-home` — единственный указатель

1. Карточка проекта (`03-Projects/<project>.md`) держит поле `spec-home` —
   абсолютный путь к `docs/specs/` этого проекта.
2. Протокол `/spec` резолвит spec **только внутри `spec-home`**. Для Vault
   `spec-home` указывает на его собственный `docs/specs/`.
3. Локальный `docs/specs/README.md` в проекте — index/указатель на его спеки.
   Второй копии инструкций в Vault не существует; Vault-викилинки и plain-пути
   на проектную спеку ведут напрямую в `<repo>/docs/specs/`.

```text
SERPlux    /home/rudra/Projects/serp/docs/specs/
dotfiles   /home/rudra/dotfiles/docs/specs/
dv-hub     /home/rudra/Projects/dv-hub/docs/specs/
AndroidOS  /home/rudra/Projects/AndroidOS/docs/specs/
ChaT       /home/rudra/Projects/ChaT/docs/specs/
vault      /home/rudra/Projects/OpenCode-Vault/docs/specs/
```

## Ownership and lifecycle

- Vault librarian владеет конвенцией размещения, naming и protocol metadata.
- Проектный агент — единственный владелец своих локальных спеков: пишет и
  правит их **в своём репозитории**, не в Vault.
- Vault-агент (librarian / Pip-Boy) правит только `docs/specs/` и `control-plane/`
  этого Vault.
- Переезд спеки: физически переносится файл + обновляется `spec-home` и
  plain-ссылки. Старая копия в Vault удаляется, томбстоун не оставляется
  (двойная копия — источник путаницы).

## Как Vault ссылается на проектную спеку

Ссылки на конкретную спеку — **plain-путь** (не Vault-викилинка), потому что
Vault-викилинки не резолвятся за пределы репозитория:

`` `~/dotfiles/docs/specs/coordination-bridge-freeze.md` ``

## Migration log (2026-09-18)

Унифицирована репо-локальная модель. Каталог `06-Specs/` упразднён:

- спеки Vault → `docs/specs/` (этот Vault);
- decision-queue и прочее runtime-состояние → `control-plane/`;
- архивный `06-Specs/SERPlux/` удалён (наследники — в `~/Projects/serp/docs/specs/`);
- AndroidOS спеку перенесена в `docs/specs/`, `spec-home` обновлён;
- SERPlux/ChaT/vault получили `spec-home`; ChaT — пустой `docs/specs/README.md`.