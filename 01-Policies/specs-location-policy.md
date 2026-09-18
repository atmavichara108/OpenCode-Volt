---
type: Policy
status: approved
date: 2026-09-18
---
# Specs Location Policy

1. Каждая execution spec живёт в репозитории того агента, который её исполняет:
   `<repo>/docs/specs/<spec>.md`. Для Vault-агентов — `docs/specs/` этого Vault.
   Исключений нет.
2. Vault не хранит execution-спеки чужих проектов. Единственный кросс-репо
   указатель — поле `spec-home` в карточке проекта (`03-Projects/<project>.md`).
3. Канонический путь детерминирован; новые execution specs не размещаются в
   случайных project `docs/` и не копируются между репозиториями.
4. `/spec` — protocol entrypoint: определяет `spec-home` текущего проекта (из
   карточки или локальных `AGENTS.md`/`README.md`), читает локальные context
   files, затем canonical spec только внутри `spec-home`. Без selector показывает
   доступные specs; при недоступном обязательном источнике возвращает `BLOCKED`
   и не делает fallback. Vault в резолвинг чужих проектов не участвует.
5. Spec — execution instructions, не evidence of execution. Approval, commit/tag
   и verifier gates внутри spec остаются authoritative.

См. протокол: [[docs/specs/README]].