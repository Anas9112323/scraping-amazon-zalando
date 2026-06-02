#!/usr/bin/env bash
# Tâche quotidienne : Docker session_2 puis notification Slack si OK (voir .env.example).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

mkdir -p "$ROOT/logs"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

LOG="${ROOT}/logs/cron_session2.log"
exec >>"$LOG" 2>&1

echo ""
echo "================================================================================"
echo "Session_2 planifié | début $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC | host $(hostname -s 2>/dev/null || echo '?')"
echo "================================================================================"

if ! command -v docker >/dev/null 2>&1; then
  echo "Erreur: docker introuvable (PATH). Lance Docker Desktop." >&2
  exit 1
fi

docker compose run --rm app
code=$?

echo "================================================================================"
echo "Session_2 planifié | fin $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC | exit docker=${code}"
echo "================================================================================"

if [[ "$code" -eq 0 && -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  msg="Session 2 OK — $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC ($(hostname -s 2>/dev/null || echo host))"
  payload=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$msg")
  if curl -sS -X POST -H 'Content-type: application/json' \
    --data "$payload" \
    --max-time 30 \
    "$SLACK_WEBHOOK_URL"; then
    echo "Slack : notification envoyée."
  else
    echo "Slack : échec envoi (curl)." >&2
  fi
elif [[ "$code" -eq 0 ]]; then
  echo "Slack : ignoré (définir SLACK_WEBHOOK_URL dans session_2/.env)."
fi

exit "$code"
