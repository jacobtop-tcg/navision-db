#!/usr/bin/env python3
"""
CLEANUP FAKE COMPANIES v1
Fjerner ikke-virksomheder fra databasen:
- Generiske spam-navne (Country + Type + Number mønstre)
- Microsoft Partners (sælger NAV, bruger det ikke)
- Artikel titler, case studies, dokumentation
- Person-navne, job titler
- For korte/ulæselige navne
"""

import sqlite3
import re
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'

# Mønstre der IKKE er virksomheder
FAKE_PATTERNS = [
    # Generiske spam: "US Tech 123", "DK Inc 456", "DE GmbH 789"
    r'^[A-Z]{2}\s+(Tech|Inc|Ltd|GmbH|A/S|ApS|Solutions|Systems|Consulting|Group|Software|Services)\s+\d+$',
    
    # TheirStack generiske: "IT Services Consulting Germany 2"
    r'^(IT|HR|Tech|Software|Consulting|Services|Solutions|Systems)\s+(Services|Consulting|Solutions|Systems|Group)\s+[A-Z]{2,}\s*\d*$',
    
    # Microsoft Partners (de sælger, er ikke kunder)
    r'^DynamicsNAV\s+Partner',
    r'^Dynamics\s+NAV\s+Partner',
    r'^Microsoft\s+Dynamics\s+Partner',
    r'^NAV\s+Partner',
    r'^Gold\s+Partner',
    r'^Registered\s+Partner',
    
    # Artikel titler / dokumentation
    r'^(Guide|Guía|Guida|Guide to|How to|What is|Definition of)',
    r'^.*\s+-\s+Case\s*Study',
    r'^.*\s+-\s+Definition',
    r'^.*\s+-\s+Migration',
    r'^.*\s+-\s+Tarifs',
    r'^.*\s+for\s+20\d{2}$',
    
    # Websider / blogs
    r'^Home\s*[-:]',
    r'^Blog\s*[-:]',
    r'^Navision\s+Planet',
    r'^Navision\s+World',
    r'^Navision\s+Hub',
    
    # Job titler / personer
    r'^Dynamics\s+NAV\s+(Consultant|Developer|Manager|Director|Architect)',
    r'^NAV\s+(Consultant|Developer|Manager)',
    r'^ERP\s+(Consultant|Manager|Specialist)',
    
    # Ulæseligt / for kort
    r'^[A-Z]{1,3}$',  # For kort
    r'^\d+$',  # Kun tal
    
    # Specifikke kendte ikke-virksomheder
    r'^Best\s+\d',  # "Best 10..."
    r'^Top\s+\d',   # "Top 10..."
    r'^Login\s+',
    r'^Sign\s+In',
    r'^Speedtest',
    r'^Yahoo\s+Search',
]

# Compile regex for performance
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in FAKE_PATTERNS]

def is_fake_company(name: str) -> bool:
    """Tjekker om navn matcher fake mønstre"""
    for pattern in COMPILED_PATTERNS:
        if pattern.match(name):
            return True
    return False

def cleanup_database(dry_run: bool = True, verbose: bool = True):
    """Fjerner fake virksomheder fra databasen"""
    
    if not DB_PATH.exists():
        print(f"❌ Database ikke fundet: {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Hent alle companies
    cursor.execute('SELECT id, company_name, country, source FROM companies')
    companies = cursor.fetchall()
    
    total = len(companies)
    fake_count = 0
    fake_companies = []
    
    print(f"🔍 Analyserer {total:,} virksomheder...")
    print()
    
    for company_id, name, country, source in companies:
        if is_fake_company(name):
            fake_count += 1
            fake_companies.append((company_id, name, country, source))
            
            if verbose and len(fake_companies) <= 50:
                print(f"❌ {name} ({country}) - Source: {source}")
    
    print()
    print(f"=== RESULTAT ===")
    print(f"📊 Total: {total:,}")
    print(f"❌ Fake/Ikke-virksomheder: {fake_count:,} ({fake_count/total*100:.1f}%)")
    print(f"✅ Rigtige virksomheder: {total - fake_count:,}")
    print()
    
    if fake_count > 0:
        if dry_run:
            print("🟡 DRY RUN - ingen ændringer lavet")
            print()
            print("Kør med --execute for at slette:")
            print(f"  python3 {sys.argv[0]} --execute")
        else:
            print("🗑️  Sletter fake virksomheder...")
            for company_id, name, country, source in fake_companies:
                cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
            
            conn.commit()
            print(f"✅ Slettede {fake_count:,} virksomheder!")
            
            # Opdater metadata
            cursor.execute('SELECT COUNT(*) FROM companies')
            new_total = cursor.fetchone()[0]
            print(f"📊 Ny total: {new_total:,} virksomheder")
    
    # Vis statistik over hvad der blev fjernet
    if fake_companies:
        print()
        print("=== TOP FJERNET MØNSTRE ===")
        pattern_counts = {}
        for _, name, _, source in fake_companies:
            for i, pattern in enumerate(FAKE_PATTERNS):
                if re.match(pattern, name, re.IGNORECASE):
                    key = pattern[:50]
                    pattern_counts[key] = pattern_counts.get(key, 0) + 1
                    break
        
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {count:,}x - {pattern}...")
    
    conn.close()
    return fake_count

if __name__ == '__main__':
    dry_run = '--execute' not in sys.argv
    verbose = '--quiet' not in sys.argv
    
    cleanup_database(dry_run=dry_run, verbose=verbose)
