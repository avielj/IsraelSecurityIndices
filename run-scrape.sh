#!/bin/bash
# Israeli indices scraper — runs on the VPS because bizportal does not serve
# GitHub's US runners. Scrapes, commits data.json, pushes to GitHub; Pages then
# republishes and the iPhone (Scriptable) widget picks it up from raw.githubusercontent.
set -uo pipefail
REPO=/home/tv-linux/israel-indices-watch
LOG=/home/tv-linux/israel-indices-watch/scrape.log
cd "$REPO" || exit 1

git fetch -q origin main && git reset -q --hard origin/main   # CI may still hold the branch

if ! python3 scraper/fetch_indices.py >>"$LOG" 2>&1; then
  echo "[$(date -Is)] scraper failed, nothing committed" >>"$LOG"
  exit 1
fi

if git diff --quiet -- data.json; then
  echo "[$(date -Is)] no change" >>"$LOG"
  exit 0
fi

git add data.json
git commit -q -m "chore: update index data $(date -u +%Y-%m-%dT%H:%M:%SZ) [vps]"
if git push -q origin main 2>>"$LOG"; then
  echo "[$(date -Is)] pushed" >>"$LOG"
else
  echo "[$(date -Is)] PUSH FAILED" >>"$LOG"
  exit 1
fi
