#!/usr/bin/env python3
"""
Navision 24/7 Daemon - Kører for evigt
========================================
Dette script kører i baggrunden og scraper Navision data 24/7/365

Installation:
1. Kopier til /workspace/navision-db/scripts/
2. Kør: python3 daemon-247.py &
3. Eller som systemd service

Kører scraper hver 6. time automatisk.
"""

import subprocess
import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
SCRAPER_DIR = Path(__file__).parent.resolve()
LOG_FILE = SCRAPER_DIR / 'logs' / 'daemon.log'
SLEEP_SECONDS = 60  # Kør hvert minut - MAKSIMAL FREKVENS!

def log(message):
    """Log message to file and stdout"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Append to log file
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def run_data_detective():
    """Run data detective auto-creative experiments"""
    log('🧪 Kører Data Detective eksperimenter...')
    
    try:
        result = subprocess.run(
            ['python3', str(SCRAPER_DIR / 'data-detective-auto.py')],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(SCRAPER_DIR)
        )
        
        if result.returncode == 0:
            log('✅ Data Detective eksperiment completed')
            if result.stdout:
                log('Output: ' + result.stdout[:500])
            return True
        else:
            log(f'❌ Data Detective failed: {result.stderr[:200]}')
            return False
    except Exception as e:
        log(f'❌ Data Detective error: {e}')
        return False

def run_scraper():
    """Run the scraper and return success status"""
    log('🕷️  Kører scraper...')
    
    try:
        result = subprocess.run(
            ['python3', str(SCRAPER_DIR / 'scraper.py'), '--auto'],
            capture_output=True,
            text=True,
            timeout=300,  # 5 min timeout
            cwd=str(SCRAPER_DIR)
        )
        
        if result.returncode == 0:
            log('✅ Scraper completed successfully')
            if result.stdout:
                # Log first 1000 chars of output
                log('Output: ' + result.stdout[:1000])
                
                # Check if companies were inserted
                if 'inserted' in result.stdout.lower():
                    # Run auto-notify
                    try:
                        subprocess.run(['bash', str(SCRIPT_DIR / 'auto-notify.sh')], timeout=10, capture_output=True)
                    except:
                        pass
            return True
        else:
            log(f'❌ Scraper failed with code {result.returncode}')
            if result.stderr:
                log('Error: ' + result.stderr[:500])
            return False
            
    except subprocess.TimeoutExpired:
        log('❌ Scraper timed out (5 min)')
        return False
    except Exception as e:
        log(f'❌ Scraper error: {e}')
        return False

def main():
    """Main daemon loop"""
    log('=' * 60)
    log('🚀 NAVISION 24/7 DAEMON STARTER')
    log(f'📁 Directory: {SCRAPER_DIR}')
    log(f'⏰ Interval: {SLEEP_SECONDS} sekunder (KØRER KONSTANT!)')
    log(f'📝 Log file: {LOG_FILE}')
    log('=' * 60)
    
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    run_count = 0
    error_count = 0
    
    while True:
        try:
            run_count += 1
            log(f'\n📊 Run #{run_count} - {datetime.now().isoformat()}')
            
            # Run scraper
            success = run_scraper()
            
            if success:
                error_count = 0  # Reset error count
            else:
                error_count += 1
                log(f'⚠️  Error count: {error_count}')
                
                # If 3 consecutive errors, wait longer
                if error_count >= 3:
                    log('⚠️  3 consecutive errors - waiting 12 hours')
                    time.sleep(43200)  # 12 hours
                    error_count = 0
            
            # Sleep until next run
            log(f'😴 Venter {SLEEP_SECONDS} sekunder...')
            time.sleep(SLEEP_SECONDS)
            
        except KeyboardInterrupt:
            log('\n⚠️  KeyboardInterrupt received - stopping daemon')
            sys.exit(0)
        except Exception as e:
            log(f'❌ Unexpected error: {e}')
            log('😴 Venter 1 time og prøver igen...')
            time.sleep(3600)

if __name__ == '__main__':
    main()
