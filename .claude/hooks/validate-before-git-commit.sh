#!/usr/bin/env bash
# Avant `git commit` (PreToolUse) : même barrière que le skill plugin-lint pour les checks automatiques.
# Sortie 2 = bloque l'appel Bash (doc Claude Code hooks).

set -euo pipefail

INPUT=$(cat)
CMD=$(
  echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', '') or '')
except Exception:
    print('')
" 2>/dev/null || true
)

case "$CMD" in
  *"git commit"*) ;;
  *) exit 0 ;;
esac

ROOT="${CLAUDE_PROJECT_DIR:-.}"
cd "$ROOT" || exit 2

exec python3 "$ROOT/plugins/tooling/skills/plugin-lint/scripts/plugin-lint-check.py"
