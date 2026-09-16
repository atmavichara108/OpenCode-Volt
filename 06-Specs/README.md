---
type: Protocol
title: Canonical Execution Specs
status: approved
---

# Canonical Execution Specs

## Правило владения (одно, без исключений)

> **Execution spec живёт в репозитории того агента, который его исполняет.**

- Spec, который исполняет **локальный агент проекта** в своём репозитории, —
  живёт в этом репозитории: `<repo>/docs/specs/<spec>.md`.
- Spec, который исполняется **из Vault** (агентами Vault / Pip-Boy или для
  самого Vault), — живёт здесь: `06-Specs/<project>/<spec>.md`.
- Vault **не хранит** execution-спеки чужих проектов «на будущее» и не требует
  от проектов держать pointer-копии своих спеков. Единственный кросс-репо
  указатель — поле `spec-home` в карточке проекта.

## Layout

```text
# локальная спека проекта (исполняет агент проекта)
/home/rudra/<repo>/docs/specs/<name>.md

# спека, исполняемая из Vault (агент Vault / Pip-Boy)
/home/rudra/Projects/OpenCode-Vault/06-Specs/<project>/<spec>.md
```

`<project>` — canonical project key (`dv-hub`, `ChaT`, `AndroidOS`, `dotfiles`,
`vault`, …). Имя spec — lowercase kebab-case, с версией или task id при
необходимости.

## Как Vault ссылается на перенесённую спеку

1. Карточка проекта (`03-Projects/<project>.md`) держит поле `spec-home` —
   абсолютный путь к spec-каталогу проекта. Это единственный указатель, который
   нужно поддерживать при переезде catalog.
2. Ссылки на конкретную спеку — **plain-путь** (не Vault-викилинка), потому что
   Vault-викилинки не резолвятся за пределы репозитория:
   `` `~/dotfiles/docs/specs/coordination-bridge-freeze.md` ``.

## Ownership and lifecycle

- Vault librarian владеет конвенцией размещения, naming и protocol metadata.
- Проектный агент — единственный владелец своих локальных спеков: пишет и
  правит их **в своём репозитории**, не в Vault.
- Vault-агент (librarian / Pip-Boy) правит только `06-Specs/Vault/` и те
  `06-Specs/<project>/` спеки, что исполняются из Vault.
- Переезд спеки: физически переносится файл + обновляется `spec-home` и
  plain-ссылки. Старая копия в Vault удаляется, томбстоун не оставляется
  (двойная копия — источник путаницы).

## SERPlux (исключение)

SERPlux authoritative specs живут только в `/home/rudra/Projects/serp/docs/specs/`
и читаются локальным `/spec`. Vault-артефакты `06-Specs/SERPlux/` — архивная
история, не execution source of truth.

## Migration (2026-09-16)

Перенесены из Vault в локальные репозитории:

| Spec | Было | Стало |
|------|------|-------|
| coordination-bridge-freeze | 06-Specs/dotfiles/ | ~/dotfiles/docs/specs/ |
| linaliapi-provider-canon | 06-Specs/dotfiles/ | ~/dotfiles/docs/specs/ |
| promo-provider-probe-balance-hook | 06-Specs/dotfiles/ | ~/dotfiles/docs/specs/ |
| pipboy-hotkey | 06-Specs/dotfiles/ | ~/dotfiles/docs/specs/ |
| androidos-return-to-implementation | 06-Specs/AndroidOS/ | ~/Projects/AndroidOS/docs/ |
| dv-hub execution specs (4 + index) | 06-Specs/dv-hub/ | ~/Projects/dv-hub/docs/specs/ |