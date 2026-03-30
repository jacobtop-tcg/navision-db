#!/bin/bash
# Quick SearXNG status check

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

echo "═══ SearXNG Health Status ═══"
python3 scripts/searxng_health.py --check

echo ""
echo "═══ Details ═══"
python3 scripts/searxng_health.py --status --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Status: {d.get('status', 'unknown')}\")
print(f\"Last check: {d.get('last_check', 'never')}\")
print(f\"Errors: {d.get('consecutive_errors', 0)}\")
if d.get('in_backoff'):
    print(f\"⏸️  In backoff: {d.get('wait_minutes', 0)} min remaining\")
if d.get('rate_limited_since'):
    print(f\"🚫 Rate limited since: {d.get('rate_limited_since')}\")
"
