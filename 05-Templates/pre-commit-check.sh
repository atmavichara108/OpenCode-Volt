#!/bin/bash
# Pre-commit hook: git-гигиена параллельной работы + пустые файлы + битые викилинки.
# Установка: ln -sf ../../05-Templates/pre-commit-check.sh .git/hooks/pre-commit
#
# Гейты (по порядку):
#   1. Блок коммита напрямую на main/master (кроме merge и явного ALLOW_MAIN=1).
#      Не даёт агентам оставлять работу кучей в канонической ветке — коммиты
#      должны идти в task/feat-ветку, а в main попадать только через merge/release.
#   2. Блок merge-conflict-маркеров (<<<<<<< / ======= / >>>>>>>) в staged-файлах.
#   3. Блок пустых .md-файлов в контент-директориях.
#   4. Блок битых [[wikilink]].
#
# Переменные окружения:
#   ALLOW_MAIN=1 — разрешить коммит прямо в main (release-флоу, осознанный шаг).

set -u

# --- Общие утилиты -----------------------------------------------------------

die() {
  echo "❌ $*" >&2
  exit 1
}

git_branch() {
  git symbolic-ref --short -q HEAD 2>/dev/null || echo "(detached)"
}

is_merge() {
  git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1
}

staged_files() {
  # Относительные пути staged-файлов (A/M/C/D), по одному на строку.
  git diff --cached --name-only --diff-filter=ACMR
}

# --- Гейт 1: не коммитить напрямую в main/master -----------------------------

echo "🔍 Pre-commit check: ветка..."

branch="$(git_branch)"
case "$branch" in
  main|master)
    if [ "${ALLOW_MAIN:-0}" = "1" ]; then
      echo "ℹ️  Коммит в $branch разрешён явно (ALLOW_MAIN=1)."
    elif is_merge; then
      echo "ℹ️  Коммит в $branch — это merge (MERGE_HEAD), пропускаю." 
    else
      die "запрещён прямой коммит в '$branch'. Создай task-ветку (git switch -c task/<slug>) и коммить туда; в main — только через merge. Форс-обход: ALLOW_MAIN=1."
    fi
    ;;
  *)
    echo "✅ Ветка '$branch' — не main/master, ок."
    ;;
esac

# --- Гейт 2: конфликт-маркеры в staged-файлах ---------------------------------

echo "🔍 Pre-commit check: merge-conflict маркеры..."

bad_markers=false
while IFS= read -r f; do
  [ -z "$f" ] && continue
  cache="$f"
  if git show ":$cache" 2>/dev/null | grep -Eq '^(<{7}[[:space:]]|>{7}[[:space:]]|={7}$)'; then
    echo "❌ Конфликт-маркеры в staged-файле: $f"
    bad_markers=true
  fi
done < <(staged_files)
if $bad_markers; then
  die "Найден незавершённый merge-conflict. Разреши конфликт и пере-stage файлы."
fi
echo "✅ Конфликт-маркеров нет"

# --- Гейт 3: пустые .md-файлы ------------------------------------------------

echo "🔍 Pre-commit check: пустые файлы..."

EMPTY_FILES=$(find 02-Methods 05-Templates -name "*.md" -empty 2>/dev/null)
if [ -n "$EMPTY_FILES" ]; then
  echo "❌ Найдены пустые файлы:"
  echo "$EMPTY_FILES"
  exit 1
fi
echo "✅ Пустых файлов нет"

# --- Гейт 4: битые [[wikilink]] ----------------------------------------------

echo "🔍 Pre-commit check: битые [[wikilink]]..."

while read -r target; do
  [[ "$target" == "..." ]] && continue
  [[ "$target" == *"#"* ]] && continue  # anchor-ссылка
  target="${target%\\}"                 # отрезать \ перед | в таблицах
  found=false
  for ext in "" ".md" ".json" ".jsonc" ".js" ".sh"; do
    [ -f "$target$ext" ] && { found=true; break; }
  done
  if ! $found; then
    for dir in "" "01-Reference/" "02-Methods/" "03-Projects/" "04-Memory/" ".opencode/agent/" ".opencode/command/"; do
      for ext in "" ".md" ".json" ".jsonc" ".sh"; do
        [ -f "${dir}${target}${ext}" ] && { found=true; break 2; }
      done
    done
  fi
  if ! $found; then
    echo "❌ Битый викилинк: [[$target]]"
    exit 1
  fi
done < <(rg -o '\[\[([^\]|]+)' --type md --no-filename --no-line-number 2>/dev/null | sed 's/\[\[//' | sort -u)

echo "✅ Все викилинки валидны"
echo "🎉 Все pre-commit гейты пройдены"
exit 0