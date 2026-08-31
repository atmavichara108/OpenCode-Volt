---
type: Execution Spec
title: Read-only MCP server — ecosystem state (contract, implementation BLOCKED)
status: blocked
date: 2026-08-31
owner: librarian
source_plan: "[[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]"
related: "[[06-Specs/Vault/ecosystem-registry]]"
tags: [spec, vault, mcp, read-only, blocked]
---
# Read-only MCP server — ecosystem state (2026-08-31)

> **Implementation status: BLOCKED.** Runtime НЕ реализован и НЕ
> заявляется. Этот документ — полный контракт/спека для будущего
> unblock. Preferred path до unblock — custom tool
> `.opencode/tools/ecosystem-snapshot.ts` (read-only local endpoint,
> без новых зависимостей; runtime loading `[проверить]`).

## 1. Решение и причины block

- **BLOCKED** (plan v2 §7). Причины:
  1. **MCP context overhead** — подтверждённый docs caveat
     (opencode.ai/docs/mcp-servers/, проверено 2026-08-31): MCP-инструменты
     добавляются в контекст; большой tool-surface легко превышает лимит.
     Для 3 инструментов overhead не оправдан, пока нет внешнего потребителя.
  2. **Dependency explosion risk** — MCP SDK (npm/python) — новая
     зависимость в экосистеме, не проходящая OSS-first gate без
     подтверждённой потребности.
  3. **Прецедент user-policy** — T-110 (AndroidOS MCP facade)
     frozen/deferred by user; MCP-инициативы требуют отдельного approval.
- **Unblock-условия (все три):**
  1. подтверждённая потребность **внешнего MCP-клиента** (не
     OpenCode-агента — агентам достаточно custom tool);
  2. оценка context overhead (число tools × schema size) зафиксирована
     и принята reviewer'ом;
  3. явный approval пользователя (отдельный proposal, не этот spec).

## 2. Контракт сервера (когда unblocked)

- **Имя (mcp-блок opencode.json):** `ecosystem-readonly`.
- **Transport:** `type: "local"`, stdio; `command: ["python3",
  "tools/mcp-readonly/server.py"]` (vault-scope); `enabled: true` только
  после unblock-approval; без `environment`-секретов (сервер не требует
  ключей).
- **Границы:** только vault-файлы (карточки, TASKS, route-log, registry,
  generated snapshot); read-only; no network; no root; no mutation.

## 3. Tools (ровно 3, минимальный surface)

| Tool | Args | Возвращает | Источник |
|------|------|-----------|----------|
| `ecosystem_state` | — | сводка: projects/tasks/route_log counts, drift_signals, input_digest, vault_head | generated/snapshot.json (или прямой пересчёт observer-логики) |
| `ecosystem_card` | `card_id: ECO-NNN` | одна карточка registry (поля card schema) | tools/ecosystem-map/registry.json |
| `ecosystem_kanban` | `layer?: L0..L4` | карточки, сгруппированные по lifecycle | tools/ecosystem-map/registry.json |

Запрещено в будущей реализации: tools с write-семантикой, tools,
открывающие произвольные пути (path traversal), tools с network-доступом.

## 4. Read-only гарантии (acceptance для будущей реализации)

- Код сервера не содержит `open(..., 'w'/'a')`, `os.remove`, `shutil`,
  сетевых импортов (`requests`, `urllib`, `socket`) — проверяется
  reviewer'ом детерминированно (grep-чеклист).
- Smoke: запуск сервера + вызов 3 tools через MCP-клиент; повторный
  вызов `ecosystem_state` на том же входе → идентичный вывод
  (детерминизм, как у observer).
- Verifier acceptance: PASS только по независимой проверке smoke; self-
  declared marker — не evidence.

## 5. Prefer custom tool (текущий путь)

- `.opencode/tools/ecosystem-snapshot.ts` — custom tool OpenCode
  (подтверждённая механика: docs/custom-tools/, проверено 2026-08-31):
  вызывает `python3 tools/ecosystem-map/observer.py --dry-run` через
  `Bun.$`, возвращает JSON. Без новых зависимостей, без secrets, без
  сети. Доступен агентам в vault-контуре.
- **Runtime loading в OpenCode не подтверждён** `[проверить]`: файл
  создан 2026-08-31; live smoke (видимость tool агенту + успешный
  вызов) — отдельный шаг, не заявлен как выполненный.

## 6. Rollback

- Spec-only: runtime нет — удалять нечего.
- После будущего unblock: удалить `mcp`-блок из opencode.json +
  `tools/mcp-readonly/`; canonical-данные не затронуты (registry/карточки
  остаются).
