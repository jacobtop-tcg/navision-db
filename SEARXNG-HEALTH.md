# SearXNG Health & Rate Limit Protection

## Overview

The Navision scraper now includes automatic SearXNG health monitoring to detect and handle rate limiting gracefully.

## How It Works

### 1. Health Check (Before Each Scrape)

Before running any scraper, the system checks SearXNG health:

```bash
python3 scripts/searxng_health.py --check
```

**Checks performed:**
- HTTP response status (detects 429 Too Many Requests)
- Engine availability (how many search engines are working)
- Response content (detects "rate limit", "captcha", "blocked" keywords)
- Response time (timeout detection)

### 2. Exponential Backoff

When rate limiting is detected:

| Occurrence | Wait Time |
|------------|-----------|
| 1st        | 1 minute  |
| 2nd        | 5 minutes |
| 3rd        | 15 minutes|
| 4th+       | 1 hour    |

### 3. Auto-Skip Scrapers

If SearXNG is rate limited, the scraper automatically:
- Logs the skip reason
- Waits for backoff period
- Retries on next daemon run (every 60 seconds)

## Commands

### Check Health
```bash
# Quick check
python3 scripts/searxng_health.py --check

# Detailed JSON output
python3 scripts/searxng_health.py --check --json

# Status without checking
python3 scripts/searxng_health.py --status
```

### Quick Status Script
```bash
bash scripts/searxng-status.sh
```

### Reset Health State
```bash
# Clear rate limit history
python3 scripts/searxng_health.py --reset
```

### Restart SearXNG
```bash
# Restart with fresh session
bash scripts/restart-searxng.sh
```

## State File

Health state is persisted to:
```
navision-db/state/searxng_health.json
```

This survives session resets and daemon restarts.

## Daemon Integration

The daemon (`daemon-247.py`) calls the scraper every 60 seconds. The scraper now:
1. Checks SearXNG health first
2. Skips if rate limited
3. Proceeds if healthy

**No manual intervention needed!**

## Monitoring

### Check Current Status
```bash
# Is daemon running?
ps aux | grep daemon-247 | grep -v grep

# Is SearXNG healthy?
python3 scripts/searxng_health.py --check

# View health history
cat state/searxng_health.json | python3 -m json.tool
```

### Logs
```bash
# Daemon logs
tail -f logs/daemon.out

# Health check history
cat state/searxng_health.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"{h['timestamp']}: {h['status']}\") for h in d.get('history',[])[-10:]]"
```

## Troubleshooting

### "SearXNG is NOT AVAILABLE - Reason: backoff"
Wait for the backoff period to expire. Check `available_at` timestamp.

### "SearXNG is NOT AVAILABLE - Reason: error"
Check if SearXNG is running:
```bash
curl http://127.0.0.1:8080
```

If not responding, restart:
```bash
bash scripts/restart-searxng.sh
```

### "Only X/Y engines working"
Some search engines get rate limited faster than others. This is normal. The scraper proceeds if >30% of engines are working.

### Persistent Rate Limiting
If SearXNG stays rate limited for hours:
1. Restart SearXNG: `bash scripts/restart-searxng.sh`
2. Wait 10 minutes
3. Check health again

## Best Practices

1. **Don't manually restart SearXNG too often** - let the backoff work
2. **Check health before debugging** - most issues are rate limiting
3. **Monitor engine status** - some engines (Brave, DuckDuckGo) rate limit faster
4. **Use restart script** - it clears cookies and cache for fresh session

---

*Last updated: 2026-03-20*
