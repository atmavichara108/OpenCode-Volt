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
agent-file: dotfiles/.opencode/agent/obsidian-plugin-dev.md — ветка task/next-20261026-0015 (по реквизитам ИЦ, 2026-10-26)
agent-location: dotfiles (проектный слой) + ожидается глобальный срез по решению владельца
mandate-source: >
  Слово владельца 2026-10-25 через Служителя + мандат ЦУ
  obsidian-plugin-agent-20261025 (Р-016: решение по агентной инфраструктуре —
  ИЦ; манифест — зона УАС, Р-004/Р-014). Мандат не самозванный (Р-009).
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_ea02cc0d8ffeFXUsAX9UeQWs2D
spec-home: /home/rudra/dotfiles/docs/specs/obsidian-plugin-dev-agent.md
status: proposed, 2026-10-26
boundaries: >
  По реквизитам ИЦ: не читает, не печатает, не коммитит секреты; не ставит
  системные пакеты; не публикует в npm; не оркеструет (task deny);
  опасные команды — deny-list в файле агента. Сам не вызывает агентов.
  Модель-пин зеркалит util-dev (amd-radeon/DeepSeek-V4.1-Flash); смена —
  только через владельца. Disciplina proposed→active: активен после
  существования файла агента + вердикта УАС (имя без сущности = корень
  dvhub-inbound-20261024).
ports: манифест-реестр docs/org/manifest-registry.md (куратор УАС)
capabilities: [obsidian-plugin-typescript, sandbox-build]
memory-zones: [plugin-dev-sandbox-notes]
file-zones: [docs/org/obsidian-plugin-dev.md]
evidence-policy: независимый verifier PASS + commit/tag; приёмка исполнения по протоколу рубки (P-4)
---

# Манифест агента «obsidian-plugin-dev»

Субагент-исполнитель для плагинов Obsidian в ведомстве Служителя Обсидиан.
Вызывающий — Служитель (primary волта); сам не оркеструет. Зоны правки
ограничены песочницами; всё остальное — только чтение.

Создан по реквизитам ИЦ (ref: obsidian-plugin-agent-20261025, письмо
2026-10-26). Статус proposed: файл агента на ветке task/next-20261026-0015,
в main не влит; вердикт УАС → active после подтверждения файла.
