#!/usr/bin/env python3
"""
Check Navision DB threshold - send update every 50 new companies
"""

import json
from pathlib import Path
from datetime import datetime
import subprocess

SCRIPT_DIR = Path(__file__).parent.resolve()
STATE_FILE = SCRIPT_DIR.parent / 'state' / 'threshold-state.json'
DATABASE_DIR = SCRIPT_DIR.parent / 'database'

def get_company_count():
    """Count companies in database"""
    import sqlite3
    
    db_file = DATABASE_DIR / 'navision-global.db'
    if not db_file.exists():
        return 0
    
    try:
        conn = sqlite3.connect(str(db_file))
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM companies')
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"DB error: {e}")
        return 0

def load_state():
    """Load threshold state"""
    if not STATE_FILE.exists():
        return {
            "baseline_count": 0,
            "next_threshold": 50,
            "threshold_increment": 50,
            "last_notified": None,
            "created_at": datetime.now().isoformat()
        }
    
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    """Save threshold state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_notification(current_count, state):
    """Send notification via OpenClaw message"""
    baseline = state.get('baseline', state.get('baseline_count', 0))
    message = f"""📊 Navision DB Update:
- Nye virksomheder: +{current_count - baseline}
- Total: {current_count}
- Næste opdatering ved: {state['next_threshold'] + state['threshold_increment']}"""
    
    # Use OpenClaw message tool via subprocess
    # This assumes we're running in OpenClaw context
    print(f"NOTIFICATION: {message}")
    
    # Try to send via openclaw CLI if available
    try:
        subprocess.run(
            ['openclaw', 'send', '--target', 'telegram:458055659', '--message', message],
            capture_output=True,
            timeout=10
        )
    except Exception as e:
        print(f"Could not send via CLI: {e}")

def main():
    current_count = get_company_count()
    state = load_state()
    
    print(f"Current count: {current_count}")
    print(f"Next threshold: {state['next_threshold']}")
    
    if current_count >= state['next_threshold']:
        print(f"🎯 Threshold reached! Sending notification...")
        send_notification(current_count, state)
        
        # Update state
        state['baseline_count'] = current_count
        state['next_threshold'] = current_count + state['threshold_increment']
        state['last_notified'] = datetime.now().isoformat()
        save_state(state)
        
        print(f"✅ New threshold set: {state['next_threshold']}")
    else:
        remaining = state['next_threshold'] - current_count
        print(f"⏳ {remaining} more companies until next update")

if __name__ == '__main__':
    main()
