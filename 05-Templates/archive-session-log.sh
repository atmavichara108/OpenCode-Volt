#!/bin/bash
# Авто-архивация session-log: переносит логи старше 30 дней в archive/
# Вызов: bash 05-Templates/archive-session-log.sh
# Можно добавить в crontab: 0 0 1 * * bash /path/to/05-Templates/archive-session-log.sh

ARCHIVE_DIR="04-Memory/archive"
SESSION_LOG_DIR="04-Memory/session-log"

mkdir -p "$ARCHIVE_DIR"

for f in "$SESSION_LOG_DIR"/*.md; do
  [ -f "$f" ] || continue
  filename=$(basename "$f")
  date_part=${filename%.md}  # YYYY-MM-DD
  if [[ "$date_part" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
    if [ "$(uname)" = "Linux" ]; then
      file_ts=$(date -d "$date_part" +%s 2>/dev/null)
    else
      file_ts=$(date -j -f "%Y-%m-%d" "$date_part" +%s 2>/dev/null)
    fi
    now_ts=$(date +%s)
    days_old=$(( (now_ts - file_ts) / 86400 ))
    if [ "$days_old" -gt 30 ]; then
      mv "$f" "$ARCHIVE_DIR/"
      echo "📦 Архивирован: $filename ($days_old дней)"
    fi
  fi
done

echo "✅ Архивация завершена"
