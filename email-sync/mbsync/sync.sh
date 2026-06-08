#!/usr/bin/env bash
# Run the two-way mirror once. Safe to schedule (cron/launchd/systemd timer).
# A lock prevents overlapping runs; output is appended to a rotating-ish log.
set -euo pipefail

LOG="${HOME}/Mail/sync.log"
LOCK="${HOME}/Mail/.sync.lock"
mkdir -p "${HOME}/Mail"

# flock avoids two syncs stomping on each other if a run runs long.
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -Is) another sync is already running; skipping." >>"$LOG"
  exit 0
fi

echo "$(date -Is) === sync start ===" >>"$LOG"
# 'mirror' is the Group defined in ~/.mbsyncrc (both channels).
if mbsync -V mirror >>"$LOG" 2>&1; then
  echo "$(date -Is) === sync ok ===" >>"$LOG"
else
  rc=$?
  echo "$(date -Is) === sync FAILED (exit $rc) ===" >>"$LOG"
  exit $rc
fi
