#!/bin/bash
# Usage: bash get-context.sh <path-to-runs.jsonl>
# Returns a JSON object with all context needed for skill-score forks.

RUNS="$1"

if [ ! -f "$RUNS" ] || [ ! -s "$RUNS" ]; then
  echo '{"segment":1,"last_score":null,"mode":"qualite","ignored_changes":[],"efficience_backlog":[]}'
  exit 0
fi

CURRENT_SEG=$(jq -s 'if length == 0 then 1 else .[-1].segment // 1 end' "$RUNS")

LAST_SCORE=$(jq -s --argjson seg "$CURRENT_SEG" \
  '[.[] | select(.segment == $seg)] | .[-1] | {quality: .scores.quality, quality_max: .scores.quality_max, decision: .decision}' \
  "$RUNS")

IS_EFFICIENCE=$(jq -s --argjson seg "$CURRENT_SEG" \
  '[.[] | select(.segment == $seg)] | .[-2:] | map(select(.scores.quality == .scores.quality_max)) | length == 2' \
  "$RUNS")

IGNORED=$(jq -s --argjson seg "$CURRENT_SEG" \
  '[.[] | select(.segment == $seg and .decision == "ignored") | .change | select(. != null)]' \
  "$RUNS")

BACKLOG=$(jq -s '[.[] | .piste_efficience | select(. != null)] | unique' "$RUNS")

CONSECUTIVE=$(jq -s --argjson seg "$CURRENT_SEG" '
  [.[] | select(.segment == $seg)] | reverse |
  reduce .[] as $r (
    {"count": 0, "done": false};
    if .done then .
    elif $r.decision != "applied" then .count += 1
    else .done = true
    end
  ) | .count' "$RUNS")

ALL_AT_MAX=$(jq -s --argjson seg "$CURRENT_SEG" --argjson n "$CONSECUTIVE" '
  if ($n | tonumber) == 0 then false
  else
    [.[] | select(.segment == $seg)] | .[-($n | tonumber):] |
    map(select(.scores.quality != null and .scores.quality == .scores.quality_max)) |
    length == ($n | tonumber)
  end' "$RUNS")

if [ "$IS_EFFICIENCE" = "true" ]; then
  MODE="efficience"
else
  MODE="qualite"
fi

jq -n \
  --argjson seg "$CURRENT_SEG" \
  --argjson last "$LAST_SCORE" \
  --arg mode "$MODE" \
  --argjson ignored "$IGNORED" \
  --argjson backlog "$BACKLOG" \
  --argjson consecutive "$CONSECUTIVE" \
  --argjson all_at_max "$ALL_AT_MAX" \
  '{segment: $seg, last_score: $last, mode: $mode, ignored_changes: $ignored, efficience_backlog: $backlog, stagnation: {consecutive_no_improvement: $consecutive, all_at_quality_max: $all_at_max}}'
