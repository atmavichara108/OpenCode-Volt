---
type: research
title: Институт — хвост vault-upgrade-research-2026-08-02: сверка и вердикт
status: draft
timestamp: 2026-10-13
project: OpenCode-Vault / dotfiles
source: "мандат Rudra 2026-10-13: «Нереализованный хвост 99-Inbox/vault-upgrade-research-2026-08-02 - исследовать и передать в лабораторию»"
related:
  - 99-Inbox/vault-upgrade-research-2026-08-02.md
  - 06-Audits/2026-10-13-ship-research-registry.md
  - 06-Audits/2026-10-07-lab-queue.md
---

# Хвост vault-upgrade-research-2026-08-02 — сверка 2026-10-13

Исходный документ (99-Inbox) предлагал P0: Mem0, sqlite-vec, Custom Tool
token-budget + audit-log; P1: LiteLLM, Langfuse, repo-map; Watch: Graphiti,
Letta. Сверка с текущим состоянием экосистемы:

## Закрыто с 2026-08-02 (не хвост)

- **A1 telemetry — РЕАЛИЗОВАНО:** token-budget (record/report) и audit-log
  работают как живые инструменты сессий (использованы Институтом 2026-10-13).
- **Context capsule {path, sha256, role} — РЕАЛИЗОВАНО** протоколом handoff
  (path + hash + summary) в peer/handoff-канонах.
- **Spend tracking — УШЛО в другой путь:** не LiteLLM, а шлюз-направление New
  API/AnyModel (спека newapi-gateway-layer) + control-plane/model-catalog +
  model-watch (T-178). Роль закрыта иначе.
- **Mem0 — ОТБОЙ:** ниша закрыта собственной горячей памятью (И-10/И-11:
  журнал+индекс+CLI) по self-host принципу; внешний memory-слой избыточен.
- **Probe «потерянных журналов research:2026-10-04» — ЗАКРЫТ:** это
  provenance-ID узлов idea-graph (jev-classifier-audit, evolution-applications,
  graph-technologies); файлов-первоисточников не существовало, дистиллят живёт
  в узлах tech-* (nodes.jsonl:83–89). Восстанавливать нечего.

## Осталось нереализованным (хвост)

- **Semantic-retrieval** (главный хвост): facts.md/session-log читаются
  целиком при старте сессии; нет индекса «мы это уже разбирали» — дубли
  исследований.
- **Repo-map (tree-sitter)** — не реализовано; зона проектов SERPlux/dv-hub,
  не Институт (в реестр как проектный кандидат).
- Langfuse/LiteLLM как таковые — сняты (роль закрыта шлюзом).

## Вердикт и передача

Годно к передаче в Ability Lab: **L9 — локальный семантический индекс**
(sqlite-vec + локальные эмбеддинги через sqlite-lembed/.gguf или Qwen, без
внешних API) над 04-Memory/facts + session-log + 99-Inbox; прямое продолжение
горячей памяти (И-10/И-11) — её векторное крыло. Запись внесена в lab-queue.
Критерий passing — в строке L9.
