---
description: Transfer read ledger and context between librarian and task-agent.
---
# Handoff Protocol

Передаёт read ledger и context между librarian и task-agent без дублирования полного содержимого файлов.

## Формат handoff ledger

```yaml
handoff:
  session_id: <timestamp>
  from: librarian
  to: <agent-name>
  scope: <vault|global|project:<name>>
  route: <capability-routing decision>
  
  read_ledger:
    - path: /absolute/path/to/file
      hash_or_mtime: <content-hash или mtime>
      purpose: <зачем читал>
      summary: <краткое содержание, не full text>
    
  context:
    intent: <что нужно сделать>
    constraints: <границы, запреты>
    acceptance: <критерии приёмки>
    
  files_to_edit:
    - path: /absolute/path
      action: <create|edit|delete>
      scope: <что менять>
      
  files_to_read:
    - path: /absolute/path
      reason: <почему нужно прочитать>
```

## Правила

1. **Не передавай full prompts** — только path + hash_or_mtime + summary
2. **Не передавай secrets** — никогда, даже в summary
3. **hash_or_mtime** — для проверки актуальности при повторном чтении
4. **Summary** — краткое содержание (3-5 строк), не копипаст содержимого
5. **Scope explicit** — vault/global/project:<name>, не размыто
6. **Acceptance criteria** — что считается выполненным

## Использование

Librarian формирует handoff ledger перед делегацией task-agent. Task-agent:
1. Читает handoff ledger
2. Проверяет read_ledger — если файл нужен и hash_or_mtime совпадает, использует summary
3. Если hash_or_mtime изменился — перечитывает файл
4. Выполняет scope из context
5. Возвращает evidence (не full diff)

## Пример

```yaml
handoff:
  session_id: 2026-09-05T16:30:00
  from: librarian
  to: meta
  scope: global
  route: capability=meta-infrastructure, role=meta, risk=medium
  
  read_ledger:
    - path: /home/rudra/dotfiles/opencode-global/.config/opencode/agent/meta.md
      hash_or_mtime: 2026-09-05T16:00:00
      purpose: canonical meta agent definition
      summary: "Meta agent: infra-edit only, no app code, read-once policy added"
    
  context:
    intent: "Add read-once policy to meta.md"
    constraints: "No app code, minimal changes, reversible"
    acceptance: "Policy section added, no syntax errors, git diff reviewed"
    
  files_to_edit:
    - path: /home/rudra/dotfiles/opencode-global/.config/opencode/agent/meta.md
      action: edit
      scope: "Add read-once policy section after main instructions"
```

## Связано

- Read-once policy: `.opencode/agent/librarian.md` (раздел "Read-once policy")
- Capability routing: `02-Methods/capability-routing.md`
- Route command: `.opencode/command/route.md`
