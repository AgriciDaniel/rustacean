#!/usr/bin/env bash
# Run a specific set of prompt files (by basename, no .txt) as Codex gpt-5.5 high agents, pooled.
# Usage: run_set.sh MAXJOBS slug1 slug2 ...
set -u
ROOT="$HOME/Desktop/Rustacean"; cd "$ROOT" || exit 1
MAXJOBS="$1"; shift
run_one(){ local s="$1"
  codex exec --skip-git-repo-check --ephemeral -C "$ROOT" \
    -m gpt-5.5 -c model_reasoning_effort="high" --dangerously-bypass-approvals-and-sandbox \
    "$(cat ".codex-build/prompts/$s.txt")" > ".codex-build/logs/$s.log" 2>&1
  echo "DONE $s (exit $?)"; }
for s in "$@"; do
  while [ "$(jobs -r | wc -l)" -ge "$MAXJOBS" ]; do sleep 3; done
  echo ">> $s"; run_one "$s" &
done
wait; echo "=== SET DONE ==="
