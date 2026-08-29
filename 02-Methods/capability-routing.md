---
type: method
status: stable
tags: [method, routing, capabilities]
---
# Capability Routing

> Design contract. Этот документ фиксирует язык и правила принятия routing
> decisions; он не утверждает runtime-внедрение и не создаёт агентов.

## Scope и определения

- **Role** — именованная ответственность агента в pipeline: например,
  `researcher`, `reviewer`, `sysop`, `verifier` или `librarian`.
- **Capability** — проверяемая способность, необходимая для шага: например,
  `read-research`, `quality-review`, `system-audit`, `acceptance-verification`
  или `vault-coordination`.
- **Route** — явное решение `task -> capability -> named role/agent` с
  границами, риском, артефактом и acceptance criteria.
- **Global kernel** — общий минимальный role/capability contract для всех
  проектов. Он задаёт интерфейс, границы и названия, но не заменяет локальную
  acceptance surface.
- **Local extension** — project-local роль, capability или проверка, которая
  добавляет проектную специфику, не меняя смысл global kernel молча.
- **Override** — явное, scoped и объяснимое изменение default route; override
  не должен скрыто превращаться в generic dispatch.

## Три слоя

| Слой | Содержание | Вопрос |
|---|---|---|
| **A: engineering conventions** | качество, структура, style contract и anti-shitcode ограничения | как должен быть сделан результат? |
| **B: language/runtime** | язык, framework, runtime, tooling и локальные технические ограничения | чем и в каком окружении это делать? |
| **C: routing policy** | capability, role, порядок шагов, риск, reviewer/verifier и fallback | кто и в какой последовательности делает/проверяет? |

Слой A не выбирает агента, B не выдаёт acceptance, а C не подменяет
проектные engineering conventions. Будущий `engineering-style-contract`
потребует отдельного approval gate и пока не является методом этого раздела.

## Route decision schema

Каждое решение должно быть представимо такой записью (формат концептуальный):

```yaml
task: "краткое действие"
scope: vault | global | project:<name>
capability: <registered-capability>
role: <named-role>
agent: <explicit-agent-name>
layers:
  engineering: <A constraints>
  language_runtime: <B constraints>
  routing: <C constraints>
inputs: [<artifacts or paths>]
outputs: [<named artifacts>]
risk: read-only | low | medium | high
mutability: read-only | docs-only | project-edit | infra-edit
review: none | reviewer
acceptance: none | project-verifier | named-acceptance-gate
fallback: <named fallback or UNROUTABLE>
override: null | {reason: <text>, approver: <role>}
```

Незаполненные `capability`, `role`, `agent`, `risk`, `mutability` и
`acceptance` не являются разрешением на dispatch: решение должно стать
`UNROUTABLE`.

## Capability registry

Это начальный design registry, а не утверждение, что перечисленные агенты уже
подняты глобально.

| Capability | Canonical role | Default scope | Expected artifact |
|---|---|---|---|
| `vault-coordination` | `librarian` | global/vault | vault plan, links, memory update |
| `read-research` | `researcher` | global + local extension | sourced research/evidence |
| `quality-review` | `reviewer` | global + local extension | findings and review verdict |
| `system-audit` | `sysop` | global + local extension | infrastructure audit |
| `meta-infrastructure` | `meta` | global | infrastructure changes/audit |
| `acceptance-verification` | `verifier` | project-local or explicitly named global | PASS/FAIL against project DoD |
| `prompt-normalization` | `prompt-engineer` | future global | normalized task spec |
| `task-compilation` | `task-compiler` | future global | compiled route/pipeline |

Registry entries require a named role, scope, input/output contract and known
acceptance boundary before runtime registration. A project may add a local
capability, but must state its relationship to the canonical one. Runtime
availability still requires live dispatch evidence, project acceptance evidence
and a separate verification gate; registry presence alone is not evidence.

## Dispatch и fallback

Dispatch is explicit and named: call the selected `agent` by its canonical name
and record the capability and route decision. `general` is not a silent router
and is not a valid substitute for a missing named agent.

Fallback order:

1. Use a compatible, explicitly registered local extension.
2. Use a compatible global role only when its scope and acceptance contract fit.
3. Apply an approved, documented override.
4. Otherwise stop with **`UNROUTABLE`**, report the missing capability/agent and
   ask for a routing decision. Do not improvise a generic dispatch.

`UNROUTABLE` is a safe outcome, not a failure to be hidden. Read-only research
may stop without a verifier only when the decision schema declares
`acceptance: none`; mutable or acceptance-bearing work may not.

## Capability routing != model routing

Capability-routing answers **who should perform which responsibility** and what
checks/boundaries apply. Model-routing answers **which model serves an already
selected role**. They remain orthogonal: changing a model does not change the
capability, authority, or acceptance contract. The current Luna + DeepSeek Go
model policy remains unchanged by this design contract.

## Boundaries, risk и approval

- `read-only` work may inspect and produce evidence, but cannot mutate project
  or global state.
- `docs-only` work may edit the explicitly scoped vault documentation only.
- `project-edit` and `infra-edit` require the relevant project/global role,
  declared paths, and an acceptance path.
- Medium/high-risk or irreversible operations require an explicit override with
  an approver and a rollback plan.
- `reviewer` evaluates engineering quality and contract adherence; `verifier`
  evaluates acceptance/DoD. **Reviewer != verifier.** Neither role silently
  inherits the other's verdict.
- `librarian` remains the coordinator: it selects/records routes and delegates;
  it does not edit project code or global agent runtime itself.

## Acceptance и rollback

Capability-routing design is accepted only when the registry, named dispatch,
fallback/`UNROUTABLE`, scope boundaries, reviewer/verifier split and at least
one representative route are approved as documents. Runtime adoption additionally
requires live dispatch evidence, project acceptance evidence and a separate
verification gate; this method does not claim those exist.

Rollback means removing or disabling the affected route/extension and returning
to the last approved named route. It must not silently broaden permissions or
replace a missing route with `general`. Any live adoption must preserve a
before/after record and a reversible change boundary.

## Связанные документы

- [[02-Methods/model-routing]] — orthogonal model selection policy.
- [[02-Methods/multi-agent-pipeline]] — pipeline composition.
- [[02-Methods/verifier-pattern]] — acceptance role boundary.
- [[06-Audits/2026-08-25-capability-routing-design-note]] — current design evidence.
- [[TASKS]] — T-077, T-092, T-093, T-094.
