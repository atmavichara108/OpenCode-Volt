# Decision Queue Log

Append-only log of decision cards. Readable projection from `06-Specs/Vault/decision-queue/`.

> **Future:** `~/.local/state/opencode/decision-queue/` — XDG-compliant user state path. Not yet active; blocked by external_directory permissions.

---

## 2026-09-05 12:00 — Permission audit: git push

- **Status:** pending
- **Risk:** high
- **Context:** Global config had `git push*` = allow
- **Options:**
  - A: Change to ask (recommended)
  - B: Keep allow
  - C: Change to deny
- **Recommendation:** A
- **Reason:** Push is destructive, should require confirmation
- **Resolution:** —

---

## 2026-09-05 12:05 — Verifier mutation: systemctl restart

- **Status:** pending
- **Risk:** critical
- **Context:** Verifier had `systemctl --user restart/start/stop` = allow
- **Options:**
  - A: Remove mutation commands (recommended)
  - B: Keep as-is
- **Recommendation:** A
- **Reason:** Verifier should be read-only validation, not mutation
- **Resolution:** —

---

## 2026-09-05 12:10 — Meta agent creation

- **Status:** pending
- **Risk:** medium
- **Context:** No explicit meta agent for agent infrastructure editing
- **Options:**
  - A: Create meta agent with scoped edit/bash (recommended)
  - B: Use builder for meta tasks
- **Recommendation:** A
- **Reason:** Clear separation: meta for infra, builder for app code
- **Resolution:** —

---

## 2026-09-05 12:15 — Decision queue storage location

- **Status:** pending
- **Risk:** low
- **Context:** Where to store decision queue cards
- **Options:**
  - A: `~/.local/state/opencode/decision-queue/` (XDG, blocked by permissions)
  - B: `OpenCode-Vault/06-Specs/Vault/decision-queue/` (recommended, current)
  - C: `~/.config/opencode/decision-queue/`
- **Recommendation:** B
- **Reason:** Vault path works without permission changes; XDG path is future goal
- **Resolution:** —

---
