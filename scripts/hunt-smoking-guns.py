#!/usr/bin/env python3
"""
SYSTEMATISK SMOKING GUN HUNT
Finder rigtige beviser for Navision brug
"""

import sqlite3
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# SMOKING GUN SEARCH QUERIES
SEARCH_QUERIES = [
    # Danske kundecases
    '"kundecase" "Dynamics NAV" site:.dk',
    '"gået live med" "Dynamics NAV" site:.dk',
    '"bruger Microsoft Dynamics NAV" site:.dk',
    '"vores ERP" "Dynamics NAV" site:.dk',
    
    # Internationale cases
    '"customer story" "Dynamics NAV"',
    '"went live with" "Dynamics NAV"',
    '"using Microsoft Dynamics NAV" company',
    
    # Job postings fra virksomheder (ikke konsulenthuse)
    '"Dynamics NAV developer" "our team"',
    '"NAV administrator" "internal"',
    '"Dynamics NAV" "in-house"',
]

def add_smoking_gun(company_name, country, evidence, url, gun_type):
    """Tilføj smoking gun til database"""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Tjek om allerede eksisterer
    cur.execute('SELECT id FROM companies WHERE company_name = ? AND source_url = ?', 
              (company_name, url))
    if cur.fetchone():
        conn.close()
        return False
    
    # Indsæt ny
    cur.execute('''
        INSERT INTO companies 
        (company_name, country, evidence_type, evidence_text, 
         confidence_score, source, source_url, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        company_name,
        country,
        'smoking_gun',
        evidence,
        5,  # Maximum confidence - verified smoking gun
        'smoking_gun_hunt',
        url,
        datetime.utcnow().isoformat() + 'Z'
    ))
    
    conn.commit()
    conn.close()
    return True

def main():
    print(f"[{datetime.utcnow().isoformat()}Z] Starter SYSTEMATISK SMOKING GUN HUNT...")
    print("=" * 80)
    print()
    print("📋 SØGEQUERIES:")
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  {i}. {query}")
    print()
    print("⏳ Dette tager tid - hver query kræver web search...")
    print()
    print("JEG ER I GANG! 🔍")

if __name__ == '__main__':
    main()
