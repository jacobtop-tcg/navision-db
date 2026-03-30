#!/bin/bash
# Auto-restart script for Navision scraper system
# Run this via cron every 5 minutes to ensure system stays up

WORKSPACE="/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db"
LOG="$WORKSPACE/logs/auto-restart.log"

log() {
    echo "[$(date -Iseconds)] $1" >> "$LOG"
}

cd "$WORKSPACE"

# Check SearXNG
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080 | grep -q "200"; then
    log "⚠️ SearXNG not responding - restarting..."
    pkill -f searxng-run 2>/dev/null
    sleep 2
    export SEARXNG_SETTINGS_PATH=/mnt/data/openclaw/workspace/.local/searxng/settings.yml
    export SEARXNG_LIMITER=false
    export SEARXNG_PUBLIC_INSTANCE=false
    export SEARXNG_BOT_DETECTION=false
    cd /mnt/data/openclaw/workspace/.local/searxng
    nohup searxng-run > searxng.log 2>&1 &
    log "✅ SearXNG restarted"
    sleep 10
fi

# Check daemon
if ! pgrep -f "daemon-247.py" > /dev/null; then
    log "⚠️ Daemon not running - restarting..."
    cd "$WORKSPACE"
    nohup python3 scripts/daemon-247.py > logs/daemon.out 2>&1 &
    log "✅ Daemon restarted"
fi

# Check scraper (spawned by daemon)
if ! pgrep -f "scraper.py --auto" > /dev/null; then
    log "⚠️ Scraper not running - daemon should restart it"
fi

log "✓ System health check complete"
