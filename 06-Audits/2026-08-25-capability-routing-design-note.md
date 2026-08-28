---
type: Design Note
date: 2026-08-25
status: design-only
tags: [capability-routing, orchestration, design]
source: "[[02-Methods/capability-routing]]"
---
# Capability-routing design note (2026-08-25)

> Это design evidence, а не подтверждение runtime-внедрения. Наблюдения ниже
> отражают текущий planning decision и не являются stable facts об OpenCode.

## Решение по sequence

Не поднимать global roles одним батчем. Базовая последовательность:

1. `researcher` — получить воспроизводимое evidence.
2. `reviewer` — проверить качество evidence и самого routing contract.
3. `sysop` — проверить глобальную инфраструктурную применимость и границы.
4. Orchestration integration — только после первых трёх gate, подключить
   route selection/dispatch к orchestration surface.

`guardian` и `prompt-engineer`/`task-compiler` остаются следующими слоями после
базового routing. `verifier` сохраняет acceptance-роль и не становится
заменой reviewer. Порядок является предложенным rollout sequence, не заявлением
о том, что global agents уже существуют.

## Kernel и extensions

Решение: строить **global role kernel + local extensions**. Kernel содержит
минимальные role/capability contracts, named dispatch, risk/mutability gates и
fallback policy. Local extension добавляет project-specific tools, language
runtime и acceptance checks. Global role не заменяет project acceptance и не
может объявить проект принятым вместо его verifier/DoD.

`librarian` остаётся coordinator: читает контекст, выбирает маршрут, вызывает
именованную роль и обновляет vault-документацию в разрешённом scope; сам не
редактирует код проектов или agent runtime.

## T-092: future interface

`prompt-normalizer` и `task-compiler` описываются как будущий интерфейс, без
создания agent runtime:

`user request -> prompt-normalizer (goal/constraints/context/DoD/spec) ->
task-compiler (roster/capabilities/order/artifacts) -> route decision -> named
dispatch`.

До runtime-подъёма этот интерфейс только задаёт вход/выход design contract.
Он не разрешает скрытую автозагрузку, generic `general` fallback или изменение
текущей Luna + DeepSeek Go model policy.

## T-094: style-contract approval flow

`engineering-style-contract` пока не оформляется методом в `02-Methods/`.
Минимальный approval flow:

1. Draft общего короткого контракта и language profiles (TS/JS, Python, Shell,
   Config/docs), включая anti-shitcode rules.
2. `researcher` собирает evidence и edge cases, `reviewer` выдаёт findings.
3. Проверить routing table и deterministic checks на representative examples.
4. `sysop` проверяет глобальные/local boundaries и operational risk.
5. Approval gate: явное согласие ответственных reviewer/guardian; до этого
   T-094 не закрывать и в `02-Methods/` не переносить.
6. После approval отдельно решить runtime adoption и project acceptance.

Минимальная routing table/reference для будущего draft:

| Work shape | Capability | Named role | Check |
|---|---|---|---|
| language/style research | `read-research` | `researcher` | sourced evidence |
| contract quality review | `quality-review` | `reviewer` | findings, no acceptance claim |
| global config/runtime audit | `system-audit` | `sysop` | scope/risk report |
| project DoD | `acceptance-verification` | project `verifier` | PASS/FAIL |

Это reference sketch, не утверждённая runtime table и не новый Method.

`system-ops` — local high-risk extension, не global role kernel. Маршрут:
`sysop` (read-only audit) → `planner` (plan) → `system-ops` (apply) →
`verifier`/post-check. Actual root smoke pending.

## Acceptance / rollback gates

Design gate считается пройденным только после проверки wikilinks, согласования
named-agent roster и approval flow. Runtime gate потребует live dispatch,
project-level acceptance evidence и отдельный rollback rehearsal. При
неопределённом capability/agent маршрут должен остановиться как `UNROUTABLE`,
а не отклониться к generic `general`.

Rollback design: отключить конкретный route/extension, вернуть последнюю
одобренную named route, сохранить evidence и не расширять права молча.

## Symptoms to investigate before root cause

- **2026-08-25:** during acceptance verification, the global `researcher`
  verifier task was cancelled by the user after the model became stuck in an
  infinite loop.
- This is a symptom/incident observation; root cause is unknown.
- This observation is not evidence of a defect in `researcher`, `verifier`,
  the model, task runtime, or routing.
- Re-running through the same route is deferred until investigation.
- Investigation requires a reproduction boundary, logs/session evidence, a
  stop condition/timeout, and a safe rollback.

### Investigation status

**Observed evidence (read-only investigation):**

- The verifier session was aborted by the user.
- Forensic session totals: 191 parts, 73 tool calls, 40 assistant turns, and
  approximately 471 seconds (~7:51).
- Tool breakdown: 29 `bash` calls (20 completed, 9 permission errors), 28
  `read`, 8 `grep`, and 8 `glob` calls.
- The incident was not run through `/loop`.
- The task inside `verifier` was not invoked.
- No explicit prompt recursion was found in the available evidence.
- `/loop` was not detected; no consecutive identical tool calls occurred.
  There were two non-consecutive similar `git log` repetitions, but they used
  different paths.
- There was a 35-second pause between assistant turns. The final result was
  `MessageAbortedError: Aborted`.
- The pattern confirms prolonged continuation/recovery behavior, but does not
  prove an infinite loop or establish the root cause.

**Ruled out only:** explicit recursion is not evidenced. This does not rule
out other retry, routing, model, or runtime behavior.

**Working hypotheses, not findings:** tool/error retry; contradictory
acceptance requiring an absent symlink; missing verifier steps; model/runtime
behavior.

**Evidence gaps:** complete session/tool trace and error payloads; exact
acceptance inputs and expected symlink state; verifier task-dispatch evidence;
model/runtime configuration and retry semantics; an independent reproduction.
The symlink discrepancy is now precise: the top-level `~/.config/opencode`
path is a symlink to the global tree, while `agent/researcher.md` is a regular
file with the matching inode/hash; the earlier statement that the file itself
was a symlink was inaccurate.

**Safe experiment constraints:** one researcher probe only; 60-second wall
timeout; no verifier, `/loop`, or `task`; ask one read-only question; stop on
repeated intent, permission rejection, or no progress. At most one child is
allowed.

**Controlled probe feasibility (2026-08-25):** the planned CLI probe was not
completed. In OpenCode 1.18.5, `opencode run --agent researcher` targets the
primary agent and may fall back to `default`; it therefore does not guarantee
that the `researcher` subagent is started. A per-run prohibition of `task` is
not provided. Shell `timeout` limits only the CLI process and does not
guarantee abort of the server-side session. These constraints make the
proposed CLI path insufficient as a controlled probe boundary.

**Next experiment:** do not treat the CLI attempt as researcher-runtime
evidence and do not retry the same route. Define a dispatch surface that
proves the named subagent was selected, enforces the no-`task` boundary per
run, and has an explicit server-session abort/cleanup mechanism; then run one
read-only probe with the existing stop conditions. Until that boundary exists,
the probe remains pending and T-107 remains open.

Root cause remains unknown. This investigation is not evidence of a defect in
`researcher`, `verifier`, the model, runtime, or routing. The previous claim
that the symlink was correct did not match the forensic observation; record
this as a drift/incomplete-verification signal, not as the cause.

## Связанные задачи и evidence

- [[TASKS]]: T-077, T-092, T-093, T-094 остаются Active design substeps; T-108 открыт до live evidence.
- [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]] — исходный ecosystem plan.
- [[06-Audits/2026-08-03-execution-sequence-note]] — предыдущая sequence rationale.
- [[02-Methods/capability-routing]] — стабильный design contract.
