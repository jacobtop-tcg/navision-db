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

def export_verified():
    """Eksporter kun verified data (høj kvalitet med evidence)"""
    import sqlite3
    import json
    
    db_path = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
    verified_json = SCRIPT_DIR.parent / 'web-export' / 'companies-verified.json'
    verified_meta = SCRIPT_DIR.parent / 'web-export' / 'metadata-verified.json'
    
    try:
        log("Starting verified export...")
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Kun højkvalitets data med evidence
        query = '''
        SELECT * FROM companies 
        WHERE confidence_score >= 4 
          AND evidence_text IS NOT NULL 
          AND evidence_text != ''
          AND source_url IS NOT NULL 
          AND source_url != ''
        ORDER BY confidence_score DESC, discovered_at DESC
        '''
        
        companies = [dict(row) for row in conn.execute(query)]
        conn.close()
        
        # Gem verified
        with open(verified_json, 'w') as f:
            json.dump(companies, f, indent=2)
        
        # Metadata
        from datetime import datetime
        meta = {
            'total_companies': len(companies),
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'quality_criteria': {
                'evidence_required': True,
                'source_url_required': True,
                'min_confidence': 4,
                'noise_filtered': True
            }
        }
        
        with open(verified_meta, 'w') as f:
            json.dump(meta, f, indent=2)
        
        log(f"Verified export: {len(companies)} virksomheder")
        return len(companies)
    except Exception as e:
        log(f"Verified export error: {e}")
        return 0

def git_commit_push():
    """Commit og push ændringer til GitHub"""
    import subprocess
    from datetime import datetime
    
    navision_dir = SCRIPT_DIR.parent
    
    try:
        # Tjek om der er ændringer
        status = subprocess.run(
            ['git', 'status', '--porcelain', 'web-export/'],
            capture_output=True,
            text=True,
            cwd=str(navision_dir)
        )
        
        if not status.stdout.strip():
            log("Git: Ingen ændringer at committe")
            return False
        
        # Git add
        subprocess.run(['git', 'add', 'web-export/'], cwd=str(navision_dir), capture_output=True)
        
        # Git commit
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        commit_msg = f"Auto-update: {timestamp}"
        commit_result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True,
            text=True,
            cwd=str(navision_dir)
        )
        
        if commit_result.returncode != 0:
            log(f"Git commit failed: {commit_result.stderr}")
            return False
        
        log(f"Git: Committet - {commit_msg}")
        
        # Git push
        push_result = subprocess.run(
            ['git', 'push'],
            capture_output=True,
            text=True,
            cwd=str(navision_dir),
            timeout=30
        )
        
        if push_result.returncode != 0:
            log(f"Git push failed: {push_result.stderr}")
            return False
        
        log("Git: Pushed til GitHub ✅")
        return True
        
    except subprocess.TimeoutExpired:
        log("Git push timeout")
        return False
    except Exception as e:
        log(f"Git error: {e}")
        return False

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
            # Kør også verified export
            export_verified()
            # Auto commit og push til GitHub
            git_commit_push()
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
