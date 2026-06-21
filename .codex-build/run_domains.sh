#!/usr/bin/env bash
# Pooled Codex driver: run every domain prompt (except the piloted error-handling)
# as a gpt-5.5 high-effort sub-agent, MAXJOBS at a time. Each writes its own log.
set -u
ROOT="$HOME/Desktop/Rustacean"
cd "$ROOT" || exit 1
MAXJOBS="${1:-5}"

run_one() {
  local slug="$1"
  codex exec --skip-git-repo-check --ephemeral -C "$ROOT" \
    -m gpt-5.5 -c model_reasoning_effort="high" --dangerously-bypass-approvals-and-sandbox \
    "$(cat ".codex-build/prompts/$slug.txt")" > ".codex-build/logs/$slug.log" 2>&1
  echo "DONE $slug (exit $?)"
}

start=$(date +%s 2>/dev/null || echo 0)
for f in .codex-build/prompts/*.txt; do
  slug="$(basename "$f" .txt)"
  [ "$slug" = "error-handling" ] && continue
  while [ "$(jobs -r | wc -l)" -ge "$MAXJOBS" ]; do sleep 3; done
  echo ">> launching $slug"
  run_one "$slug" &
done
wait
echo "=== ALL DOMAINS DONE ==="
