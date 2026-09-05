#!/usr/bin/env bash
# Permission smoke test: representative safe commands for each role
# Run manually to verify permissions work as expected
# No mutation, no network, no dangerous operations
#
# Usage: bash 06-Specs/Vault/permission-smoke-test.sh
# (Executable bit pending manual chmod +x; chmod denied in Vault project config)

set -euo pipefail

echo "=== Permission Smoke Test ==="
echo "Date: $(date -Iseconds)"
echo ""

# Researcher: read-only git + filesystem
echo "--- Researcher (read-only) ---"
echo "✓ git status"
git status --short 2>&1 || echo "  (not a git repo or error)"
echo "✓ git log"
git log --oneline -3 2>&1 || echo "  (error)"
echo "✓ git diff"
git diff --stat 2>&1 || echo "  (error)"
echo "✓ ls"
ls -la .opencode/ 2>&1 || echo "  (error)"
echo "✓ grep"
grep -r "description" .opencode/agent/ 2>&1 || echo "  (error)"
echo ""

# Reviewer: read-only + validation
echo "--- Reviewer (read-only + validation) ---"
echo "✓ python3 -m json.tool (validate JSON)"
python3 -m json.tool < /home/rudra/dotfiles/opencode.json > /dev/null 2>&1 && echo "  JSON valid" || echo "  JSON invalid"
echo "✓ git blame"
git blame -L 1,5 .opencode/agent/librarian.md 2>&1 || echo "  (error)"
echo ""

# Verifier: read-only + validation commands
echo "--- Verifier (read-only + validation) ---"
echo "✓ git rev-parse"
git rev-parse --short HEAD 2>&1 || echo "  (error)"
echo "✓ git ls-files"
git ls-files .opencode/ 2>&1 || echo "  (error)"
echo "✓ stat"
stat -c '%A %n' .opencode/agent/librarian.md 2>&1 || echo "  (error)"
echo "✓ file"
file .opencode/agent/librarian.md 2>&1 || echo "  (error)"
echo ""

# Meta: scoped edit + git ask
echo "--- Meta (scoped edit + git ask) ---"
echo "✓ git branch"
git branch --show-current 2>&1 || echo "  (error)"
echo "✓ git remote -v"
git remote -v 2>&1 || echo "  (error)"
echo "✓ git describe"
git describe --tags --always 2>&1 || echo "  (error)"
echo ""

# Dangerous commands (should be denied/ask)
echo "--- Dangerous (should be denied/ask) ---"
echo "✗ git push --force (DENY)"
echo "✗ git reset --hard (DENY)"
echo "✗ git clean -fd (DENY)"
echo "✗ rm -rf (DENY)"
echo "✗ sudo (DENY)"
echo "✗ systemctl start/stop/restart (DENY for verifier/researcher/reviewer)"
echo ""

echo "=== Smoke test complete ==="
echo "Manual verification: run these commands in OpenCode TUI and check permission prompts"
