# B9-followup: evidence для verifier (raw command output)

## 1. is_common_field — шаблон и исключения
```
04-Memory/idea-graph/nodes.jsonl: True
04-Memory/idea-graph/edges.jsonl: True
04-Memory/idea-graph/protocol.jsonl: True
04-Memory/idea-graph/race-test/race-nodes.jsonl: True
04-Memory/idea-graph/generated/x.jsonl: True
04-Memory/idea-graph/archive/v1/nodes.jsonl: False
04-Memory/idea-graph/_archive/x.jsonl: False
03-Projects/foo.jsonl: False
```
Прод-поведение не регрессировало (3 корневых = True), sandbox/generated = True, архивы = False.

## 2. untracked-каталоги разворачиваются
`tools/git-agent/freed.py:56`: run(["git","status","--porcelain=v1","--untracked-files=all"])

## 3. freed.py check (rc=1, ловит и общий файл, и дубль id)
```
WARN: common-field:04-Memory/idea-graph/race-test/librarian-verify/concurrent.jsonl,04-Memory/idea-graph/race-test/librarian-verify/probe.jsonl; dup-id:04-Memory/idea-graph/race-test/librarian-verify/probe.jsonl:lv-a-001
rc=1
```

## 4. exit-коды
- lease-list rc=0; bogus cmd rc=64.
- check: 0 ok / 1 warn / 2 blocked (код: freed.py:205/212/227).
- Блок 2 = merge-state/main — код подтверждён, main не создавали.

## 5. PROD validate.mjs (без argv) — не регрессировал
```
nodes: 165   edges: 198   protocol: 3
by graph:  {"stream":92,"proto":21,"world":14,"organ":7,"mech":8,"tech":8,"quest":7,"event":8}
PASS   rc=0
```

## 6. SANDBOX validate.mjs
Дубль-набор (probe.jsonl, lv-a-001 дважды):
```
MODE: sandbox (.../librarian-verify/probe.jsonl) — прод-пороги не применяются
nodes: 2
ERRORS (1): ... :3 duplicate node id: lv-a-001
FAIL   rc=1
```
Чистый набор (cleancheck/clean.jsonl, 1 узел):
```
MODE: sandbox (.../race-test/cleancheck)
nodes: 1
PASS   rc=0
```

## 7. Спека консистентна коду
docs/specs/git-freed.md:71-72 — исключение `archive/` и `_archive/` (совпадает с freed.py:32 `COMMON_EXCLUDE_DIRS = ("_archive","archive")`).
S8.1 — приёмка: warning на дубль id и одновременную запись, exit-коды 0/1/2.

## 8. Прод-граф не тронут
`git status --porcelain=v1` по nodes/edges/protocol.jsonl — пусто.

## Сценарий гонки (кейс B, одновременная запись)
2 параллельных писателя, по 5 узлов в один свежий файл concurrent.jsonl:
итог 10 строк, unique 10, lost 0, dups NONE → freed.py даёт common-field WARN (rc=1).
