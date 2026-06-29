#!/bin/bash
# Pre-commit hook: проверяет пустые файлы и битые викилинки
# Установка: ln -sf ../../05-Templates/pre-commit-check.sh .git/hooks/pre-commit

echo "🔍 Pre-commit check: пустые файлы..."

EMPTY_FILES=$(find 02-Methods 05-Templates -name "*.md" -empty 2>/dev/null)
if [ -n "$EMPTY_FILES" ]; then
  echo "❌ Найдены пустые файлы:"
  echo "$EMPTY_FILES"
  exit 1
fi

echo "✅ Пустых файлов нет"

echo "🔍 Pre-commit check: битые [[wikilink]]..."

while read -r target; do
  [[ "$target" == "..." ]] && continue
  [[ "$target" == *"#"* ]] && continue  # anchor-ссылка
  found=false
  for ext in "" ".md" ".json" ".jsonc" ".js"; do
    [ -f "$target$ext" ] && { found=true; break; }
  done
  if ! $found; then
    for dir in "" "01-Reference/" "02-Methods/" "03-Projects/" "04-Memory/" ".opencode/agent/" ".opencode/command/"; do
      for ext in "" ".md" ".json" ".jsonc"; do
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
exit 0
