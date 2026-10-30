#!/bin/bash
# B11 v3 apply: repo name + staging conf source
set -uo pipefail
repo="$1"; confsrc="$2"
STAGE=/home/rudra/Projects/OpenCode-Vault/.b11-staging
cd "/home/rudra/Projects/$repo" || { echo "BLOCKED: no repo"; exit 9; }

cur=$(git branch --show-current)
if [ "$cur" != task/git-freed-b11 ]; then
  git switch task/git-freed-b11 || { echo "BLOCKED: switch failed"; exit 9; }
fi

git status --porcelain > "/tmp/opencode/b11v3-$repo-before.txt"

# 2. hook v3 (install, exec bit) + symlink self-heal
install -m 755 "$STAGE/pre-commit" githooks/pre-commit || { echo "BLOCKED: install hook"; exit 9; }
[ -L .git/hooks/pre-commit ] || ln -sf ../../githooks/pre-commit .git/hooks/pre-commit

# 3. conf
install -m 644 "$confsrc" githooks/garbage-guard.conf || { echo "BLOCKED: install conf"; exit 9; }

echo "--- worktree sha256 ---"
sha256sum githooks/pre-commit githooks/garbage-guard.conf

# 4. amend
git add githooks/pre-commit githooks/garbage-guard.conf || { echo "BLOCKED: add"; exit 9; }
git commit --amend -m "chore(hygiene): pre-commit v3 — гейт decode-мусора с per-repo исключениями (vendor/build)" --quiet || { echo "BLOCKED: amend"; exit 9; }

echo "--- verify ---"
echo "AMEND_SHA=$(git rev-parse HEAD)"
echo "--- show --stat ---"
git show --stat --oneline HEAD | cat
nfiles=$(git show --name-only --format= HEAD | grep -c .)
echo "NFILES=$nfiles"
echo "--- ls-tree ---"
git ls-tree HEAD -- githooks/
echo "HOOK_SHA=$(git show HEAD:githooks/pre-commit | sha256sum | cut -d' ' -f1)"
echo "CONF_SHA=$(git show HEAD:githooks/garbage-guard.conf | sha256sum | cut -d' ' -f1)"

# 6. acceptance (direct hook run, never committed)
echo "--- acceptance ---"
echo 'чистый русский текст' > .b11v3-ok.md
git add .b11v3-ok.md
bash .git/hooks/pre-commit > "/tmp/opencode/b11v3-$repo-ok.out" 2>&1; rc_ok=$?
echo "RC_CLEAN=$rc_ok"; tail -2 "/tmp/opencode/b11v3-$repo-ok.out"

printf 'текст \xe4\xb8\xad мусор\n' > .b11v3-bad.md
git add .b11v3-bad.md
bash .git/hooks/pre-commit > "/tmp/opencode/b11v3-$repo-bad.out" 2>&1; rc_bad=$?
echo "RC_BAD=$rc_bad"; grep -n 'decode-мусор' "/tmp/opencode/b11v3-$repo-bad.out" || echo "NO_DECODE_MSG"

# cleanup test artifacts only
git reset --quiet
rm -f .b11v3-ok.md .b11v3-bad.md
git status --porcelain > "/tmp/opencode/b11v3-$repo-after.txt"
if diff -q "/tmp/opencode/b11v3-$repo-before.txt" "/tmp/opencode/b11v3-$repo-after.txt" > /dev/null; then
  echo "DIFF_BEFORE_AFTER=equal"
else
  echo "DIFF_BEFORE_AFTER=DIFFERENT"
  diff "/tmp/opencode/b11v3-$repo-before.txt" "/tmp/opencode/b11v3-$repo-after.txt" || true
fi
exit 0
