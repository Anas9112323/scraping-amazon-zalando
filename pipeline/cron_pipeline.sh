#!/usr/bin/env bash
# Cron job quotidien : lance le pipeline de scraping marques FR.
# Ajoute au crontab avec :
#   crontab -e
#   0 8 * * * /Users/Anas/Documents/cours-scraping-pipeline/pipeline/cron_pipeline.sh
#
# Ou via launchd (macOS) — voir LAUNCHD_SETUP en bas du fichier.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  source "$ROOT/.env"
  set +a
fi

mkdir -p "$ROOT/logs"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Developer/CommandLineTools/usr/bin:$PATH"

LOG="${ROOT}/logs/cron_$(date +%Y%m%d).log"
exec >>"$LOG" 2>&1

echo ""
echo "================================================================================"
echo "Pipeline scraping | début $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC"
echo "================================================================================"

python3 "$ROOT/run_batch.py"
code=$?

if [[ "$code" -eq 0 ]]; then
  echo "Export Excel..."
  python3 "$ROOT/export_excel.py" || echo "Excel: export failed (non-blocking)"
fi

echo "================================================================================"
echo "Pipeline scraping | fin $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC | exit=${code}"
echo "================================================================================"

if [[ "$code" -eq 0 && -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  msg="Pipeline scraping OK — $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC"
  payload=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$msg")
  curl -sS -X POST -H 'Content-type: application/json' \
    --data "$payload" --max-time 30 \
    "$SLACK_WEBHOOK_URL" || echo "Slack: échec envoi"
fi

exit "$code"

# ============================================================================
# LAUNCHD_SETUP (macOS — alternative à crontab)
# ============================================================================
# Crée le fichier ~/Library/LaunchAgents/com.scraping.pipeline.plist :
#
# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#   <key>Label</key>
#   <string>com.scraping.pipeline</string>
#   <key>ProgramArguments</key>
#   <array>
#     <string>/Users/Anas/Documents/cours-scraping-pipeline/pipeline/cron_pipeline.sh</string>
#   </array>
#   <key>StartCalendarInterval</key>
#   <dict>
#     <key>Hour</key>
#     <integer>8</integer>
#     <key>Minute</key>
#     <integer>0</integer>
#   </dict>
#   <key>StandardOutPath</key>
#   <string>/Users/Anas/Documents/cours-scraping-pipeline/pipeline/logs/launchd.log</string>
#   <key>StandardErrorPath</key>
#   <string>/Users/Anas/Documents/cours-scraping-pipeline/pipeline/logs/launchd_err.log</string>
# </dict>
# </plist>
#
# Puis :
#   launchctl load ~/Library/LaunchAgents/com.scraping.pipeline.plist
