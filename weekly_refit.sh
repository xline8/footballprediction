#!/usr/bin/env bash
# weekly_refit.sh — Full model refit / re-training.
#
# Triggers the end-to-end pipeline (data, walk-forward fits, meta model,
# upcoming predictions). Run weekly to keep team-rating decay and model
# parameters fresh.
#
# Suggested cron (Monday 04:00 WIB = 21:00 UTC Sunday):
#   0 21 * * 0 cd /path/to/football-data && ./weekly_refit.sh >> logs/weekly_refit.log 2>&1

set -euo pipefail
cd "$(dirname "$0")"

echo "[weekly_refit] $(date -Iseconds) start"
python pipeline_orchestrator.py --run-all
echo "[weekly_refit] $(date -Iseconds) done"
