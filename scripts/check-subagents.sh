#!/bin/bash
# Subagent Health Check for Navision System
# Run this as part of system monitoring

WORKSPACE="/mnt/data/openclaw/workspace/.openclaw/workspace"
LOG="$WORKSPACE/navision-db/logs/subagent-health.log"

log() {
    echo "[$(date -Iseconds)] $1" >> "$LOG"
}

cd "$WORKSPACE"

# Check if detective subagent should be running
# For now, just log status - actual spawning done by main agent

log "=== Subagent Health Check ==="

# Check for active subagents via OpenClaw CLI if available
if command -v openclaw &> /dev/null; then
    openclaw subagents list >> "$LOG" 2>&1
else
    log "OpenClaw CLI not available - cannot check subagents"
fi

# Check if detective agent files exist
if [ -f "agents/navision-detective/SOUL.md" ]; then
    log "✅ Detective agent config exists"
else
    log "❌ Detective agent config MISSING"
fi

if [ -f "agents/navision-detective/AGENTS.md" ]; then
    log "✅ Detective agent instructions exist"
else
    log "❌ Detective agent instructions MISSING"
fi

log "=== Check Complete ==="
