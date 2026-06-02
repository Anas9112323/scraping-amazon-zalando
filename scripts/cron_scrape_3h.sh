#!/usr/bin/env bash
# Point d'entrée prévu pour crontab à 3h du mat (scraping complet, sortie dans logs/cron_3h.log).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p "$ROOT/logs"

PY="${ROOT}/.venv/bin/python"
RUN="${ROOT}/run.py"
LOG="${ROOT}/logs/cron_3h.log"

if [[ ! -x "$PY" ]]; then
  echo "Erreur: Python venv introuvable ou non exécutable: $PY" >&2
  exit 1
fi

exec >>"$LOG" 2>&1

echo ""
echo "================================================================================"
echo "CRON scrape 3h | début $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC | host $(hostname -s 2>/dev/null || echo '?')"
echo "================================================================================"

"$PY" "$RUN" --append
code=$?

echo "================================================================================"
echo "CRON scrape 3h | fin $(date -u '+%Y-%m-%dT%H:%M:%SZ') UTC | exit ${code}"
echo "================================================================================"

exit "${code}"
