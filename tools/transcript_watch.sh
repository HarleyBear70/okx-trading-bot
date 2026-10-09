#!/bin/bash
# Runs on Jeff's Linux (cron, every 10 min): answers "transcript: <youtube url>" comments on GitHub issues.
# YouTube blocks GitHub's servers, but not this machine.
export PATH="$HOME/.local/bin:/usr/bin:/bin"
cd "$HOME/okx-trading-bot" || exit 1
SEEN="$HOME/.transcript_seen"; touch "$SEEN"
gh api "repos/HarleyBear70/okx-trading-bot/issues/comments?sort=created&direction=desc&per_page=30" \
  --jq '.[] | select(.body | startswith("transcript:")) | "\(.id) \(.issue_url | split("/") | last) \(.body)"' 2>/dev/null |
while read -r id issue rest; do
  grep -qx "$id" "$SEEN" && continue
  echo "$id" >> "$SEEN"
  url=$(echo "$rest" | grep -oE 'https?://[^ ]+' | head -1)
  out=$(python3 tools/yt_transcript.py "$url" research/transcripts 2>&1 | tail -1)
  if [ -f "$out" ]; then
    git pull -q --rebase --autostash; git add "$out"; git commit -q -m "transcript: $url"; git push -q
    gh issue comment "$issue" --body "Transcript saved (from Jeff's Linux): https://github.com/HarleyBear70/okx-trading-bot/blob/main/${out// /%20}"
  else
    gh issue comment "$issue" --body "Linux transcript fetch failed for $url: $out"
  fi
done
