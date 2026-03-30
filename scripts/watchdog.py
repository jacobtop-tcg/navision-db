#!/usr/bin/env python3
"""
Navision System Watchdog - Auto-Recovery
=========================================
Kører hvert 5. minut og tjekker at systemet er sundt.
Genstarter automatisk hvis noget er crashet.

Installation (cron):
*/5 * * * * cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db && python3 scripts/watchdog.py >> logs/watchdog.log 2>&1
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE = SCRIPT_DIR.parent
LOG_FILE = SCRIPT_DIR / 'logs' / 'watchdog.log'
STATE_DIR = SCRIPT_DIR.parent / 'state'
PID_FILE = SCRIPT_DIR / 'logs' / 'daemon.pid'

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def check_process(name: str, pattern: str) -> bool:
    """Check if a process is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', pattern],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            log(f"✅ {name}: Running (PID: {', '.join(pids[:3])})")
            return True
        else:
            log(f"❌ {name}: NOT RUNNING")
            return False
    except Exception as e:
        log(f"⚠️  {name}: Check failed - {e}")
        return False

def check_searxng() -> bool:
    """Check if SearXNG is healthy"""
    try:
        import requests
        resp = requests.get('http://127.0.0.1:8080', timeout=10)
        if resp.status_code == 200:
            log(f"✅ SearXNG: Healthy (HTTP {resp.status_code})")
            return True
        else:
            log(f"❌ SearXNG: Unhealthy (HTTP {resp.status_code})")
            return False
    except Exception as e:
        log(f"❌ SearXNG: Unreachable - {e}")
        return False

def check_database_growth() -> bool:
    """Check if database is growing (not stuck)"""
    try:
        # Read last status
        status_file = WORKSPACE / 'navision-db' / 'state' / 'last_status.txt'
        if not status_file.exists():
            log("⚠️  Database growth: No baseline yet")
            return True
        
        with open(status_file) as f:
            last_count = int(f.read().strip())
        
        # Get current count
        result = subprocess.run(
            ['python3', str(SCRIPT_DIR / 'scraper.py'), '--status'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        for line in result.stdout.split('\n'):
            if 'Total companies:' in line:
                current_count = int(line.split(':')[1].strip())
                break
        else:
            log("⚠️  Database growth: Could not parse status")
            return True
        
        # Save current for next check
        with open(status_file, 'w') as f:
            f.write(str(current_count))
        
        if current_count >= last_count:
            log(f"✅ Database growth: OK ({last_count} → {current_count})")
            return True
        else:
            log(f"⚠️  Database growth: SHRINKING? ({last_count} → {current_count})")
            return True  # Don't restart, just warn
            
    except Exception as e:
        log(f"⚠️  Database growth: Check failed - {e}")
        return True  # Don't restart on check failure

def restart_daemon():
    """Restart the daemon"""
    log("🔄 Restarting daemon...")
    
    # Kill existing daemon
    subprocess.run(['pkill', '-f', 'daemon-247.py'], capture_output=True)
    
    # Start new daemon
    nohup_cmd = f"cd {WORKSPACE / 'navision-db'} && nohup python3 scripts/daemon-247.py > logs/daemon.out 2>&1 &"
    subprocess.run(nohup_cmd, shell=True)
    
    log("✅ Daemon restarted")

def restart_searxng():
    """Restart SearXNG"""
    log("🔄 Restarting SearXNG...")
    
    # Kill existing
    subprocess.run(['pkill', '-f', 'searxng-run'], capture_output=True)
    
    # Start new
    searxng_dir = Path.home() / '.local' / 'searxng'
    if searxng_dir.exists():
        env = {
            'SEARXNG_SETTINGS_PATH': str(searxng_dir / 'settings.yml'),
            'SEARXNG_LIMITER': 'false',
        }
        subprocess.run(
            ['searxng-run'],
            cwd=str(searxng_dir),
            env={**subprocess.os.environ, **env},
            start_new_session=True
        )
    
    log("✅ SearXNG restarted")

def main():
    log("=" * 60)
    log("WATCHDOG CHECK START")
    
    issues = []
    
    # Check SearXNG
    if not check_searxng():
        issues.append('searxng')
    
    # Check daemon
    if not check_process('Daemon', 'daemon-247.py'):
        issues.append('daemon')
    
    # Check scraper (should be running or recently completed)
    if not check_process('Scraper', 'scraper.py --auto'):
        log("ℹ️  Scraper: Not currently running (may be between cycles)")
    
    # Check database growth
    if not check_database_growth():
        issues.append('database_stuck')
    
    # Auto-recover
    if 'searxng' in issues:
        log("⚠️  SearXNG is down - attempting restart...")
        restart_searxng()
    
    if 'daemon' in issues:
        log("⚠️  Daemon is down - attempting restart...")
        restart_daemon()
    
    if 'database_stuck' in issues:
        log("⚠️  Database not growing - may be stuck")
        # Don't auto-restart, just alert
    
    # Summary
    if not issues:
        log("✅ ALL SYSTEMS HEALTHY")
    else:
        log(f"⚠️  ISSUES FOUND: {', '.join(issues)}")
        log("🔧 AUTO-RECOVERY INITIATED")
    
    log("WATCHDOG CHECK END")
    log("=" * 60)

if __name__ == '__main__':
    main()
