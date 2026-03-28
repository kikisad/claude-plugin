#!/bin/bash
# Usage: bash init-eval.sh <eval-dir-path>
# Creates the eval directory and an empty runs.jsonl.

DIR="$1"

if [ -z "$DIR" ]; then
  echo "ERROR: eval directory path required" >&2
  exit 1
fi

mkdir -p "$DIR"
touch "$DIR/runs.jsonl"
echo "Initialized $DIR"
