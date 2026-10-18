---
type: incident-record
date: 2026-10-09
status: documented; runtime commit gate not implemented
---

# Incident record: permissions, gate ordering, and branch provenance

## 1. Sibling-worktree permission mismatch

- **Симптом:** нужные Vault/dotfiles sibling worktrees изначально расходились с эффективным permission allowlist.
- **Repro/evidence:** в этом ходе задано, что mismatch был устранён точечным allowlist-изменением в `cac2a00`; оба текущих task worktree созданы отдельно от fetched `origin/main` (Vault `cac2a00`, dotfiles `fcabb01`).
- **Причина:** метод/allowlist не совпадали по разрешённым roots.
- **Урок:** перед созданием worktree сверять точный абсолютный путь с эффективным allowlist.
- **Исправление:** точечный permission fix в `cac2a00`; дальнейшая работа выполняется только под разрешёнными roots.
- **Статус:** исправлено для этих roots; это не утверждение о runtime-gate.

## 2. Проверки выполнены после review/verifier

- **Симптом:** полный pre-commit/garbage-guard был запущен после reviewer/verifier и нашёл старую mixed-script typo, что запустило новый цикл.
- **Repro/evidence:** последовательность и результат указаны в подтверждённом handoff для этой работы; отдельный лог запуска в этом record не заявляется.
- **Причина:** deterministic gate не был поставлен перед review/verification.
- **Урок:** сначала завершить edit/staging и все применимые детерминированные проверки; затем reviewer → verifier на одном hash staged diff.
- **Исправление:** порядок документирован в global meta instructions, Vault AGENTS и `02-Methods/team-director.md`; любая мутация требует повторения полного цикла на новом hash.
- **Статус:** процесс документирован; runtime commit gate не реализован.

## 3. Task branch с чужим ancestry

- **Симптом:** первая task branch была ответвлена от чужого checkout `c0b99a6` с посторонними commits.
- **Repro/evidence:** подтверждённый handoff фиксирует исходный commit и наличие посторонних commits; они не были запушены, патч изолировали от свежего `origin/main`.
- **Причина:** ветка создавалась от текущего checkout/HEAD, а не от явно обновлённого canonical base.
- **Урок:** `fetch` и явно указывать `origin/main` при создании новой task branch/worktree.
- **Исправление:** текущие task worktrees созданы отдельно от `origin/main`; пример в `02-Methods/git-worktree-isolation.md` теперь явно указывает base.
- **Статус:** патч изолирован, посторонние commits не запушены; исправление метода описано.

## Runtime gate — отдельный scope

Есть договорённость спроектировать runtime commit gate, но сначала требуется определить
trusted machine-verifiable evidence path и уточнить risk-tier policy. Код/hook не
внедрялся; утверждать, что такой gate уже работает, нельзя.
