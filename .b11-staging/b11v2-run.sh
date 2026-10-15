#!/bin/bash
# B11-v2 apply+repro runner. usage: b11v2-run.sh <repo> [runbook|synthetic]
set -u
repo=$1
mermode=${2:-synthetic}
stage=/home/rudra/Projects/OpenCode-Vault/.b11-staging/pre-commit
cd "/home/rudra/Projects/$repo" || { echo "BLOCKED: no repo"; exit 9; }

br=$(git branch --show-current)
[ "$br" = "task/git-freed-b11" ] || { echo "BLOCKED: branch=$br"; exit 1; }

mkdir -p /tmp/opencode
git status --porcelain > "/tmp/opencode/b11v2-$repo-before.txt"

if [ -n "$(git diff --cached --name-only)" ]; then echo "BLOCKED: index not clean before apply"; exit 1; fi

install -m 755 "$stage" githooks/pre-commit || { echo "BLOCKED: install failed"; exit 1; }

git add githooks/pre-commit
staged=$(git diff --cached --name-only)
[ "$staged" = "githooks/pre-commit" ] || { echo "BLOCKED: unexpected staged set: $staged"; git reset -q; exit 1; }
git commit --amend -m "chore(hygiene): pre-commit контур Git Freed B11-v2 — known-FP fix: викилинк-гейт игнорирует fenced/inline code (mermaid)" > "/tmp/opencode/b11v2-$repo-amend.log" 2>&1
rc_amend=$?
[ $rc_amend -eq 0 ] || { echo "BLOCKED: amend rc=$rc_amend"; tail -5 "/tmp/opencode/b11v2-$repo-amend.log"; exit 1; }

sha_head=$(git rev-parse HEAD)
stat_files=$(git show --stat --format= HEAD | grep -c '|')
blob_mode=$(git ls-tree HEAD -- githooks/pre-commit | awk '{print $1}')
hook_sha=$(sha256sum <(git show HEAD:githooks/pre-commit) | cut -d' ' -f1)
wt_sha=$(sha256sum githooks/pre-commit | cut -d' ' -f1)
echo "AMEND $sha_head files=$stat_files mode=$blob_mode hooksha=${hook_sha:0:16} wt=${wt_sha:0:16}"

run_hook() { bash .git/hooks/pre-commit > "/tmp/opencode/b11v2-hook-$repo.log" 2>&1; echo $?; }

[ -z "$(git diff --cached --name-only)" ] || { echo "BLOCKED: staged before tests"; exit 1; }
rc_a=$(run_hook)

cleanup() { git reset -q HEAD -- "$1" 2>/dev/null; rm -f "$1"; }

: > .b11-test-empty.md; git add .b11-test-empty.md; rc_b=$(run_hook); cleanup .b11-test-empty.md

printf '<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> other\n' > .b11-test-conf.md; git add .b11-test-conf.md; rc_c=$(run_hook); cleanup .b11-test-conf.md

if [ "$mermode" = "runbook" ]; then
  # infra-runbook.md чистый (не в dirty) — `git add` чистого файла стейджит ноль, тест был бы
  # вакуальным. Стейджим байт-идентичную копию его контента из HEAD как новый .md —
  # гейт 3 реально видит mermaid-контент. Оригинал не трогаем.
  git show HEAD:docs/infra-runbook.md > .b11-test-runbook.md; git add .b11-test-runbook.md
  rc_d=$(run_hook); cleanup .b11-test-runbook.md
else
  printf '```mermaid\nflowchart LR\n  M --> Media[[media :9 UDP]]\n```\n' > .b11-test-mer.md
  git add .b11-test-mer.md; rc_d=$(run_hook); cleanup .b11-test-mer.md
fi

echo 'ссылка [[b11-нет-такой]]' > .b11-test-wl.md; git add .b11-test-wl.md; rc_e=$(run_hook); cleanup .b11-test-wl.md

leftover=$(git diff --cached --name-only)

git status --porcelain > "/tmp/opencode/b11v2-$repo-after.txt"
if diff -q "/tmp/opencode/b11v2-$repo-before.txt" "/tmp/opencode/b11v2-$repo-after.txt" >/dev/null; then snap="before==after OK"; else snap="DIFF!"; diff "/tmp/opencode/b11v2-$repo-before.txt" "/tmp/opencode/b11v2-$repo-after.txt"; fi

echo "RC clean=$rc_a empty=$rc_b conflict=$rc_c mermaid=$rc_d wikilink=$rc_e (expect 0 1 1 0 1)"
echo "LEFTOVER_STAGED=[${leftover:-none}] $snap"
