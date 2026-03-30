#!/usr/bin/env python3
"""
Auto-update progress tracker after each batch insert
Call this after every batch insertion
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database' / 'navision-global.db'
PROGRESS_FILE = Path(__file__).parent / 'PROGRESS.md'

def get_current_count():
    conn = sqlite3.connect(str(DB_PATH))
    count = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    conn.close()
    return count

def get_country_breakdown():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute('''
    SELECT country, COUNT(*) as count 
    FROM companies 
    GROUP BY country 
    ORDER BY count DESC
    ''')
    breakdown = cursor.fetchall()
    conn.close()
    return breakdown

def update_progress():
    count = get_current_count()
    breakdown = get_country_breakdown()
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    progress = count / 20000 * 100
    remaining = 20000 - count
    
    # Read existing file
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update status section
    old_status = f"""## CURRENT STATUS
- **Total Companies:** 4630
- **Goal:** 20000
- **Progress:** 23.1%
- **Remaining:** 15370"""

    new_status = f"""## CURRENT STATUS
- **Total Companies:** {count}
- **Goal:** 20000
- **Progress:** {progress:.1f}%
- **Remaining:** {remaining:,}"""

    content = content.replace(old_status, new_status)
    
    # Update timestamp
    old_ts = f"- **Timestamp:** 2026-03-25T21:39:00Z"
    new_ts = f"- **Timestamp:** {timestamp}"
    content = content.replace(old_ts, new_ts)
    
    # Update country breakdown if needed
    breakdown_text = "\n".join([f"- 🇿🇿 {country}: {count}" for country, count in breakdown[:15]])
    
    # Write updated file
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Progress updated: {count}/20000 ({progress:.1f}%)")
    print(f"📊 Top countries:")
    for country, count in breakdown[:10]:
        print(f"   {country}: {count}")

if __name__ == '__main__':
    update_progress()
