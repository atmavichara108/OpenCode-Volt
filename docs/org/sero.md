---
type: Manifest
id: sero
name: Агент «SerO» — Служитель Обсидиан (глобальный)
shadow: служитель экосистемы Obsidian (Deck, canvas, визуализация) + изолированные клиенты
jurisdiction: >
  Ведомство UI|UX ecosys (Р-021): Deck решений, canvas-ризома, визуализация
  экосистемы Корабля, проекции тайлов. Домашний волт — OpenCode-Vault (пишет
  в 10-Deck/**). Глобальный слой: пригоден в любом проекте владельца; первый
  клиент — TradingMind (изолированный волт: его правила = источник, экосистема —
  только справка без прямого слова владельца). Не замена вольтовому
  obsidian-servant — это его глобальный слой.
carrier-sessions: "глобальный агент (без сессии-носителя); проекты-клиенты — факты вызова; привязка проекта сессии = факт, перепривязка — вопрос к ИЦ (ЦУ ref: homeostasis-canon-uas)"
agent-file: >
  opencode-global/.config/opencode/agent/obsidian-servant.md — коммит 99c9b00
  (ветка task/sero-global-agent; факт-фикс ЦУ по TD-52; влитие в main — вне
  зоны УАС). Волтовая копия: ~/Projects/OpenCode-Vault/.opencode/agent/obsidian-servant.md.
agent-location: "глобально (dotfiles opencode-global) + волт (OpenCode-Vault); два слоя одной роли"
mandate-source: >
  Слово владельца 2026-10-25 (basis: quoted, через ОШ/Р-029): «пускай сделают
  глобального агента SerO Служитель Обсидиан, скилл и спека у него должны быть,
  если нету, пускай попросит ИЦ предоставить». Канон Р-021; реконсилиация ЦУ
  ref: sero-reconcile (канон агента = существующий файл; манифест = юридическая
  обвязка). Мандат не самозванный (Р-009).
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_ea02cc0d8ffeFXUsAX9UeQWs2D
spec-home: /home/rudra/dotfiles/docs/specs/
status: active, 2026-10-26
boundaries: >
  Фактический файл: mode primary; модель nvidia/z-ai/glm-5.3-flash; task deny;
  bash — только читающий allowlist (rg/ls/cat/…git read), остальное deny;
  edit — только внутри волта клиента (TradingMind/**) и 10-Deck/**; AGENTS.md —
  ask; секретные пути — deny. Без прямого слова владельца: клиента в
  экосистему не регистрирует, в канон/реестры Корабля не пишет, писем не шлёт.
ports: манифест-реестр docs/org/manifest-registry.md (куратор УАС)
capabilities: [obsidian-structure, deck-canvas, client-vault-structure]
memory-zones: [sero-deck-notes]
file-zones: [docs/org/sero.md]
evidence-policy: независимый verifier PASS + commit/tag; рапорты — в ЦУ (копия — ОШ)
reconciliation: >
  Сверка УАС 2026-10-26 (манифест vs файл 99c9b00): расхождение ДОСЛОВНО —
  чертёж предполагал роль-подроль с зоной только «изолированный проект без
  входа в экосистему»; факт: primary-агент экосистемы (Deck Корабля 10-Deck/**)
  + клиентские волты. Манифест приведён к факту (канон = файл); расхождение
  зафиксировано и рапортовано ЦУ (ref: sero-reconcile, п.2). Смена модели —
  только через владельца.
---

# Манифест агента «SerO»

Глобальный слой роли Служителя Обсидиан: тот же канон Р-021 и формат карточек
ADR-032, но применимый в любом проекте владельца, а не только в вольте.
Первый клиент — TradingMind (квест ОШ, Р-029, приоритет 0).

## Что подтверждено фактом (не намерением)

- Файл агента существует: `opencode-global/.config/opencode/agent/obsidian-servant.md`
  (99c9b00, ветка `task/sero-global-agent`); волтовая копия — в OpenCode-Vault.
- Канон Р-021; среда — Obsidian нативно (YAML, wikilinks, canvas JSON).
- Права по факту: `task: deny`, edit — клиентский волт + `10-Deck/**`,
  bash — читающий allowlist, секреты — deny везде.

## Статус

Active с 2026-10-26: имя имеет сущность (файл существует). Реконсиляция
манифест ↔ файл проведена УАС; расхождение раннего чертежа (роль и зона)
исправлено по факту и рапортовано. Влитие ветки в main — шаг ИЦ/ЦУ.
