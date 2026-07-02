---
type: method
status: stable
tags: [method]
---
# Verifier Pattern

## Проблема
Агент-исполнитель сам себе судья: он «считает» задачу выполненной, потому что заинтересован закончить. Без внешней проверки качество дрейфует, баги и дыры безопасности просачиваются (DryRun 2026: Claude-агент дотащил IDOR и незащищённый destructive-endpoint до финала именно из-за отсутствия независимой проверки).

## Решение
Отдельный агент-верификатор, который НИЧЕГО не правит, только выносит вердикт PASS/FAIL против Definition of Done. Это паттерн evaluator из multi-agent архитектур Anthropic. Разделение ролей критично: тот, кто пишет, не должен оценивать сам себя.

## Реализация в OpenCode
Глобальный subagent в `~/.config/opencode/agent/verifier.md` (один на все проекты):

```
---
description: Strict acceptance verifier. Checks work against DoD. Returns PASS/FAIL, never edits.
mode: subagent
model: opencode-go/glm-5.2
temperature: 0.1
permission:
  edit: deny
  webfetch: deny
  bash:
    "*": deny
    "git diff*": allow
    "git log*": allow
    "npm run ci": allow
    "npm test*": allow
    "python -m pytest*": allow
---
You are a strict acceptance verifier. You NEVER fix or edit anything.
For each acceptance criterion: PASS/FAIL with concrete evidence (file:line, test name, output).
End with exactly one line: `VERDICT: PASS` or `VERDICT: FAIL`.
Partial completion is FAIL. Never soften the verdict.
If FAIL: numbered list of minimal fixes for the build agent.
```

## Когда применять / когда НЕ применять
- Применять: задачи с проверяемым DoD (тесты, CI, чёткие критерии). Идеально для SERPlux (бинарные критерии пайплайна) и dv-hub (npm run ci).
- НЕ применять: чисто исследовательские задачи без критериев — там вердикт PASS/FAIL бессмысленен.

## Связанные
- Reference: [[agents]], [[permissions]]
- Используется в: [[closed-loop]] (verify-фаза)
- Модель: [[model-routing]] (почему именно sonnet, а не haiku)
- Внедрён в: [[SERPlux]] ✅, [[dv-hub]] ❌, [[vault]] ❌
