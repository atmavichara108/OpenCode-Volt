---
name: spec-write-routing
description: Use when the user asks to write or create an execution spec for a named project; route the file to that project's spec-home, never to Vault docs/specs unless the project is vault.
---

# Spec Write Routing

When the user asks to write a spec for a project, treat the named project as the
destination, not merely as metadata.

1. Read `03-Projects/<project>.md` in the Vault and obtain its `spec-home`.
2. Write the spec directly into that project's `spec-home/` through the project
   agent or a named build subagent.
3. Use `kind: task` for one-off execution work and `kind: contract` for a
   durable protocol/schema/role contract. New task specs belong in the root of
   `spec-home`; completed task specs move to `spec-home/done/` only after
   independent verifier PASS plus commit/tag.
4. Never use Vault `docs/specs/` as a staging area for another project's spec.
   Vault `docs/specs/` is reserved for `project: vault`.
5. After writing, verify the absolute path is inside the requested project's
   `spec-home`; if not, stop with `BLOCKED` and do not leave a duplicate.

Required report: project, spec-home, absolute path written, kind, and blockers.
