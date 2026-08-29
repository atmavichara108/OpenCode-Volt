---
type: Runbook Changelog
title: Vibecoding Runbook Changelog
description: Краткая append-only история подтверждённых изменений operational practice.
tags: [runbooks, changelog]
---
# Vibecoding Runbook Changelog

## Purpose

Коротко фиксирует подтверждённые shifts практики в operational layer. Это не
аудит, не план и не журнал всех сессий.

## Format rule

Append-only: одна запись на подтверждённый shift, дата, краткое изменение и
основание. Старые записи не переписываются; proposals и `[проверить]` не входят.

## Entries

### 2026-08-29 — Global Coordination Bridge command

- Добавлена глобальная `/bridge` как protocol entrypoint в текущем репозитории;
  команда использует canonical AndroidOS bridge, named-role gate и `UNROUTABLE`
  без общего fallback.
- Source: `~/dotfiles/opencode-global/.config/opencode/command/bridge.md`;
  после GNU Stow — `~/.config/opencode/command/bridge.md`.

### 2026-08-29 — User-facing Coordination Bridge protocol shift

- Coordination Bridge закреплён как единый canonical Git-backed file protocol,
  а не отдельный bridge-agent; будущие facade/command и MCP optional и не
  являются source of truth.
- Добавлен пользовательский guide для Max Rudra: intent/scope/owner/DoD,
  handoff, evidence, named gates, full SHA и commit approval.
- Basis: [[07-Runbooks/coordination-bridge-operator-guide]],
  `repo=AndroidOS; commit=planned; path=coordination/bridge/README.md`.

### 2026-08-17 — Volt as coordination node

- Volt moved from command-center framing toward a coordination node above the
  vibecoding layer.
- Basis: [[04-Memory/session-log/2026-08-04]].

### 2026-08-17 — Execution sequence fixed

- Sequence: kernel → SERPlux → dotfiles/global hardening → dv-hub.
- Basis: [[06-Audits/2026-08-03-execution-sequence-note]].

### 2026-08-17 — Contracts replace loose agent descriptions

- Ecosystem planning uses contracts instead of loose agent descriptions.
- Basis: [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]].

### 2026-08-17 — Runbook layer separated

- Runbook layer introduced as separate operational truth.
- Basis: [[04-Memory/session-log/2026-08-04]].

### 2026-08-29 — Named reviewer smoke gate

- После изменения agent/config требуется restart; named route сначала проходит
  controlled smoke. Reviewer даёт quality verdict, verifier отдельно даёт
  acceptance; отсутствие named route означает `UNROUTABLE`.
- Basis: [[04-Memory/route-log/2026-08-29-reviewer-smoke]],
  [[04-Memory/facts]].

### 2026-08-29 — Correction smoke protocol

- Primary role переключается через Tab или настроенный `switch_agent` keybind;
  subagent вызывается через `@mention` или `task`.
- Пользователь задаёт intent естественным языком и не обязан писать
  технический prompt или acceptance marker. Evidence/verdict проверяет
  независимый verifier по session/runtime artifacts, а не самодекларация агента.
- `/agents` не зафиксирован как универсальный способ переключения agent role:
  это может быть пользовательская команда model selection; реализацию не
  предполагать без подтверждения.
- Ошибочная `/agent`-инструкция исправлена; текущий sysop live smoke не
  состоялся из-за неправильного dispatch-инструкта, поэтому marker не является
  evidence и `sysop smoke PASS` не объявляется.
- Source: https://opencode.ai/docs/agents/

### 2026-08-29 — Sysop primary smoke gate

- Exact global primary `system-audit -> sysop` получил scoped
  `runtime-smoke-confirmed`: read-only runtime trace, без general fallback;
  это не orchestration/general rollout, а `system-ops` apply остаётся отдельным.
- Acceptance подтверждён independent verifier; self-declared marker не является
  evidence.
- Basis: [[04-Memory/route-log/2026-08-29-sysop-smoke]], [[04-Memory/facts]],
  [[01-Reference/capability-routing]].

### 2026-08-29 — Orchestration smoke gate

- Подтверждён exact Vault workflow: librarian route selection → named
  researcher → reviewer → verifier; sequential, read-only, без `general`
  fallback и self-marker evidence. Automatic runtime router не внедрён.
- Basis: [[04-Memory/route-log/2026-08-29-orchestration-smoke]],
  [[06-Specs/Vault/control-plane-smoke]].
