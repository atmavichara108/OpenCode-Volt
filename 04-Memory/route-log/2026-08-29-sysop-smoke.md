---
type: Route Log
title: Sysop primary smoke
date: 2026-08-29
status: ROUTED
tags: [routing, sysop, smoke, verifier]
---
# Sysop Primary Smoke

- **route_id:** `system-audit->sysop:global-primary-smoke:2026-08-29`
- **status:** `ROUTED`
- **capability:** `system-audit`
- **role/agent:** `sysop`
- **scope:** `global`
- **risk/mutability:** `read-only`
- **review:** `reviewer`
- **acceptance:** `verifier`
- **runtime_dispatch:** `true` only for exact smoke
- **evidence:** sysop session `ses_fb7542676ffejYn26lfi5Ep0Pf`; verifier task
  `ses_fb1b20cf1ffeqHsO7geJ1UBKf2`
- **reason:** Независимый verifier PASS по runtime trace подтвердил, что
  session переключена на `agent=sysop`, `mode=primary`, с model provider
  `opencode-go/deepseek-v4-flash`. Выполнены read-only audit commands;
  `edit`, `task` и mutating `bash` отсутствовали; `stow -n` был simulation;
  general fallback не наблюдался. Self-declared marker не использовался как
  proof.

Boundary: это scoped primary smoke, не orchestration/general rollout. `sysop`
не используется как task subagent. `system-ops` apply остаётся отдельным
local extension и не входит в acceptance этого route.
