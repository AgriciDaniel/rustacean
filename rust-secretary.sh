#!/usr/bin/env bash
# Rust Secretary launcher — your dedicated Rust agent, grounded in this brain.
# Usage:
#   ./rust-secretary.sh "your task or question"
#   EFFORT=xhigh ./rust-secretary.sh "do a deep review of wiki/concepts/Ownership.md"
# Codex auto-loads AGENTS.md from this folder.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
EFFORT="${EFFORT:-high}"
TASK="${*:?usage: ./rust-secretary.sh \"task\"}"
exec codex exec --skip-git-repo-check --ephemeral -C "$ROOT" \
  -m gpt-5.5 -c model_reasoning_effort="$EFFORT" --dangerously-bypass-approvals-and-sandbox \
  "$TASK"
