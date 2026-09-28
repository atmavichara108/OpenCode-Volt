#!/bin/bash
# ensure-provider-packages — сверка npm-пакетов провайдеров с диском.
# Кредо: программа вместо токенов. Запуск: bash tools/agent-ops/ensure-provider-packages.sh [--install]
# Без --install только отчёт (exit 1 если чего-то нет). С --install — bun add недостающего.
# Проверяет оба живых конфига: TUI (симлинк в dotfiles-канон) и M Code.
set -uo pipefail

CONFIGS=(
    "$HOME/.config/opencode/opencode.jsonc"
    "$HOME/.local/share/m-code-data/config/opencode.jsonc"
)
MOD_BASE="$HOME/.config/opencode/node_modules"
missing=0

for cfg in "${CONFIGS[@]}"; do
    [[ -f "$cfg" ]] || { echo "SKIP (нет файла): $cfg"; continue; }
    while IFS= read -r pkg; do
        name="${pkg#@ai-sdk/}"
        # openai-compatible встроен в opencode v2 — проверять нечего
        [[ "$pkg" == "@ai-sdk/openai-compatible" ]] && continue
        if [[ -d "$MOD_BASE/$pkg" || -d "$MOD_BASE/@ai-sdk/$name" ]]; then
            echo "OK   $pkg ($cfg)"
        else
            echo "MISS $pkg ($cfg)"
            missing=1
            if [[ "${1:-}" == "--install" ]]; then
                (cd "$HOME/.config/opencode" && bun add "$pkg") && echo "INSTALLED $pkg"
            fi
        fi
    done < <(grep -oE '"(npm|package)"[[:space:]]*:[[:space:]]*"[^"]+"' "$cfg" | grep -oE '"[^"]+"$' | tr -d '"' | sed 's/^aisdk://' | sort -u)
done

if [[ "$missing" -eq 1 && "${1:-}" != "--install" ]]; then
    echo "---"
    echo "Есть недостающие пакеты. Починить: bash tools/agent-ops/ensure-provider-packages.sh --install"
    exit 1
fi
