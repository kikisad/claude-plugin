#!/bin/bash
# Usage: bash append-run.sh <path-to-runs.jsonl> '<json-object>'
# Validates JSON then appends as a single compact line.

RUNS="$1"
JSON="$2"

if [ -z "$JSON" ]; then
  echo "ERROR: JSON argument is empty" >&2
  exit 1
fi

echo "$JSON" | jq empty 2>/dev/null
if [ $? -ne 0 ]; then
  echo "ERROR: Invalid JSON — not appended" >&2
  exit 1
fi

echo "$JSON" | jq -c '.' >> "$RUNS"
echo "Appended run to $RUNS"
