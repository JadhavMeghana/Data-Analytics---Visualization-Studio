#!/bin/bash

# Cron Job Setup Helper Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CRON_JOB="0 2 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/run_pipeline.sh >> $PROJECT_ROOT/logs/cron.log 2>&1"

echo "Adding cron job for daily execution at 2 AM..."
echo "Cron job: $CRON_JOB"
echo ""
echo "To add this cron job, run:"
echo "crontab -e"
echo ""
echo "Then add this line:"
echo "$CRON_JOB"

