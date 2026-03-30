#!/usr/bin/env python3
"""
Auto-Export Daemon
Kører export scriptet hvert 5. minut automatisk
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
EXPORT_SCRIPT = SCRIPT_DIR / 'export-for-web.py'
LOG_FILE = SCRIPT_DIR.parent / 'logs' / 'auto-export-daemon.log'
STATE_FILE = SCRIPT_DIR.parent / 'state' / 'last-export.txt'

def log(message):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def export_data():
    """Kør export scriptet"""
    try:
        log("Starting export...")
        result = subprocess.run(
            ['python3', str(EXPORT_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log(f"Export successful! Output:\n{result.stdout}")
            # Gem timestamp
            with open(STATE_FILE, 'w') as f:
                f.write(datetime.utcnow().isoformat() + 'Z')
        else:
            log(f"Export failed: {result.stderr}")
    except Exception as e:
        log(f"Export error: {e}")

def main():
    log("Auto-export daemon started")
    log(f"Will run every 300 seconds (5 minutes)")
    
    # Første run
    export_data()
    
    # Kør i loop
    while True:
        time.sleep(300)  # 5 minutter
        export_data()

if __name__ == '__main__':
    main()
