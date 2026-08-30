---
type: Policy
status: approved
date: 2026-08-29
---
# Specs Location Policy

1. Для всех проектов, кроме утверждённого исключения SERPlux, центральный Vault
   — source of truth для execution specs:
   `/home/rudra/Projects/OpenCode-Vault/06-Specs/<project>/`.
2. Approved exception: для SERPlux canonical execution specs находятся только в
   `/home/rudra/Projects/serp/docs/specs/`. Этот локальный каталог и локальная
   команда `/spec` authoritative; старые Vault-файлы SERPlux — historical,
   non-authoritative archive и не могут быть источником инструкций.
3. Канонический путь детерминирован; новые execution specs не размещаются в
   случайных project `docs/` и не копируются между репозиториями.
4. Локальный pointer разрешён для discoverability, но не авторитетен и не
    содержит вторую версию инструкций.
5. `/spec` — protocol entrypoint: читает локальные `AGENTS.md`/`README.md`, затем
   canonical spec. Для SERPlux читает только `docs/specs/`; к Vault не обращается.
   Для остальных проектов читает canonical Vault spec; без selector показывает
   доступные specs; при недоступном обязательном источнике возвращает `BLOCKED`
   и не делает fallback.
6. Локальная `/spec` может существовать для совместимости только как wrapper с
    тем же canonical precedence. Legacy generation должен иметь отдельное имя.
7. Spec — execution instructions, не evidence of execution. Approval, commit/tag
   и verifier gates внутри spec остаются authoritative.
