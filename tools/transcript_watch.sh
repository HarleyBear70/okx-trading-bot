#!/bin/bash
# Runs on Jeff's Linux (cron, every 10 min): answers "transcript: <youtube url>" comments on GitHub issues.
# YouTube blocks GitHub's servers, but not this machine.
# Oct 14 2026: transcripts are saved on Jeff's computer only (Claude Files), never pushed: the repo is public and
# they are other people's words.
export PATH="$HOME/.local/bin:/usr/bin:/bin"
cd "$HOME/okx-trading-bot" || exit 1
SEEN="$HOME/.transcript_seen"; touch "$SEEN"
gh api "repos/HarleyBear70/okx-trading-bot/issues/comments?sort=created&direction=desc&per_page=30" \
  --jq '.[] | select(.user.login == "HarleyBear70" and (.body | startswith("transcript:"))) | "\(.id) \(.issue_url | split("/") | last) \(.body)"' 2>/dev/null |
while read -r id issue rest; do
  grep -qx "$id" "$SEEN" && continue
  echo "$id" >> "$SEEN"
  url=$(echo "$rest" | grep -oE 'https?://[^ ]+' | head -1)
  out=$(python3 tools/yt_transcript.py "$url" "$HOME/Claude Files/From Claude/4 - Rules, guides, notes/transcripts" 2>&1 | tail -1)
  if [ -f "$out" ]; then
    gh issue comment "$issue" --body "Transcript saved on Jeff's computer (not on GitHub): $(basename "$out"). Terminal Claude can read it."
  else
    gh issue comment "$issue" --body "Linux transcript fetch failed for $url: $out"
  fi
done
