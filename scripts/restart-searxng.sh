#!/bin/bash
# Restart SearXNG with fresh session

echo "🔄 Restarting SearXNG..."

cd /mnt/data/openclaw/workspace/.openclaw/workspace

# Stop existing
pkill -f "searxng" 2>/dev/null
sleep 2

# Clear cookies/cache
rm -rf .local/searxng/instances/* 2>/dev/null
rm -rf .local/searxng/.searxng-cookie* 2>/dev/null

# Start fresh
cd .local/searxng
./start-searxng.sh &

sleep 5

# Test
curl -s "http://127.0.0.1:8080/search?q=test&format=json" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    engines = d.get('unresponsive_engines', [])
    working = len([e for e in engines if not e]) if isinstance(engines, list) else 0
    print(f'✅ SearXNG restarted')
    print(f'   Unresponsive engines: {len(engines)}')
except:
    print('❌ SearXNG not responding')
"

# Reset health state
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db
python3 scripts/searxng_health.py --reset

echo "Done!"
