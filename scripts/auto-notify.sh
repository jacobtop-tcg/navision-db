#!/bin/bash
# Auto-notify script - sender update når nye virksomheder findes

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

# Get current count
CURRENT=$(python3 -c "import sqlite3; conn = sqlite3.connect('database/navision-global.db'); print(conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]); conn.close()")

# Read last count from state
if [ -f "state/last_count.txt" ]; then
    LAST=$(cat state/last_count.txt)
else
    LAST=0
fi

# Check if we found new companies
if [ "$CURRENT" -gt "$LAST" ]; then
    DIFF=$((CURRENT - LAST))
    echo "🎉 NYE FUND: +$DIFF virksomheder (Total: $CURRENT)"
    
    # Save new count
    echo "$CURRENT" > state/last_count.txt
    
    # Log with timestamp
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] +$DIFF companies (Total: $CURRENT)" >> state/found_log.txt
fi

echo "$CURRENT"
