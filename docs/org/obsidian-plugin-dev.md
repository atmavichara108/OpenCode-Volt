---
type: Manifest
id: obsidian-plugin-dev
name: Агент «obsidian-plugin-dev» — разработчик плагинов Обсидиан
shadow: исполнитель плагинов (TypeScript) для Служителя Обсидиан
jurisdiction: >
  Разработка и переписывание плагинов Obsidian (TypeScript) для ведомства
  UI|UX ecosys (Р-021). Пишет в песочнице волтов: зоны правки —
  ~/Projects/OpenCode-Vault/.obsidian/plugins/** и
  ~/Projects/OpenCode-Vault-plugins-sandbox/**; всё остальное (dotfiles,
  dv-hub, tools, ~/.config) — read-only. Код приложений проектов не трогает.
carrier-sessions: "субагент без собственной сессии-носителя; вызывается Служителем Обсидиан (primary волта) через task(agent=\"obsidian-plugin-dev\")"
agent-file: dotfiles/.opencode/agent/obsidian-plugin-dev.md — main, зоны подтянуты 6adbd34 (первичная сверка c2849fd; уточнение по запросу УАС — сверено 2026-10-27 по origin/main)
agent-location: dotfiles (проектный слой)
mandate-source: >
  Слово владельца 2026-10-25 через Служителя + мандат ЦУ
  obsidian-plugin-agent-20261025 (Р-016: решение по агентной инфраструктуре —
  ИЦ; манифест — зона УАС, Р-004/Р-014). Мандат не самозванный (Р-009).
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_ea02cc0d8ffeFXUsAX9UeQWs2D
spec-home: /home/rudra/dotfiles/docs/specs/obsidian-plugin-dev-agent.md
status: active, 2026-10-27 (вердикт УАС без оговорки — после сверки 6adbd34)
boundaries: >
  ФАКТ по файлу (сверено 2026-10-27 по origin/main, 6adbd34): mode subagent;
  модель-пин amd-radeon/DeepSeek-V4.1-Flash = util-dev; task deny; edit
  "*": deny + allow только по двум зонам (.obsidian/plugins/**,
  плагины-песочница), **/AGENTS.md — ask; external_directory scoped (зоны +
  волт на чтение + dotfiles + .config/opencode + /tmp/opencode), секреты deny;
  опасные команды deny-list. Оговорка первого вердикта (edit/external_directory
  глобальны, зона текстом) СНЯТА: ИЦ подтянул права машиной по запросу УАС —
  обещание реквизитов и факт сошлись.
ports: манифест-реестр docs/org/manifest-registry.md (куратор УАС)
capabilities: [obsidian-plugin-typescript, sandbox-build]
memory-zones: [plugin-dev-sandbox-notes]
file-zones: [docs/org/obsidian-plugin-dev.md]
evidence-policy: независимый verifier PASS + commit/tag; приёмка исполнения по протоколу рубки (P-4)
---

# Манифест агента «obsidian-plugin-dev»

Субагент-исполнитель для плагинов Obsidian в ведомстве Служителя Обсидиан.
Вызывающий — Служитель (primary волта); сам не оркеструет. Создан по
реквизитам ИЦ (ref: obsidian-plugin-agent-20261025).

## Вердикт УАС (2026-10-27)

**active по факту**: файл агента в main (c2849fd, merge a658005) — имя имеет
сущность, канон соблюдён. Ключевые права проверены и совпадают (subagent,
модель-пин, task deny, секреты, опасные команды).

**Оговорка зафиксирована**: машинные границы шире обещанных реквизитов —
`edit: allow` и `external_directory: "*"` глобально, зона только в тексте
промпта. Запрос к ИЦ на подтяжку прав до scoped-зон отправлен; расхождение
рапортовано ЦУ (не молчаливая приёмка). До подтяжки: граница = дисциплина
текста + deny-list, любой выход из зоны фиксируется как инцидент.
