#!/usr/bin/env bash
# Test planifié — « Bonjour Thierry » (crontab Linux / launchd macOS).
# Sur macOS, préférer launchd (voir LAUNCHD.txt) si cron n’écrit pas dans Documents.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$ROOT/logs"
LOG="${ROOT}/logs/hello_cron.log"
ERR="${ROOT}/logs/hello_cron.err"
exec 2>>"$ERR"

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') — Bonjour Thierry" >>"$LOG"
