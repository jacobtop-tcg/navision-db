#!/bin/bash
# Navision Global Database Scraper - Cron Job Script
# ==================================================
# This script is designed to be run via cron every 6 hours
# It handles errors gracefully and logs all output

# Configuration
WORKSPACE="/mnt/data/openclaw/workspace/.openclaw/workspace"
SCRAPER_DIR="$WORKSPACE/navision-db"
LOG_DIR="$SCRAPER_DIR/logs"
LOG_FILE="$LOG_DIR/scraper-$(date +%Y-%m-%d).log"
ERROR_LOG="$LOG_DIR/scraper-errors.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Change to scraper directory
cd "$SCRAPER_DIR"

# Log start
echo "======================================" >> "$LOG_FILE"
echo "Starting scraper at $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Run the scraper
python3 scripts/scraper.py --auto >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Log completion
if [ $EXIT_CODE -eq 0 ]; then
    echo "Scraper completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Scraper failed with exit code $EXIT_CODE at $(date)" >> "$ERROR_LOG"
    echo "Check $LOG_FILE for details" >> "$ERROR_LOG"
fi

echo "" >> "$LOG_FILE"

# Exit with same code as scraper
exit $EXIT_CODE
