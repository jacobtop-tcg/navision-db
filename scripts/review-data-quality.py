#!/usr/bin/env python3
"""
KRITISK DATA REVIEW
Gennemgår hvad vi faktisk har og vurderer kvalitet
"""

import sqlite3
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

def review():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    print("=" * 80)
    print("🔍 KRITISK DATA REVIEW")
    print("=" * 80)
    print()
    
    # Total
    cur.execute('SELECT COUNT(*) FROM companies WHERE confidence_score >= 4')
    total = cur.fetchone()[0]
    print(f"Total med høj kvalitet (4-5★): {total:,}")
    print()
    
    # Fordeling på kilder
    print("📊 FORDELING PÅ KILDER:")
    cur.execute('''
        SELECT source, COUNT(*) as count 
        FROM companies 
        WHERE confidence_score >= 4
        GROUP BY source 
        ORDER BY count DESC
    ''')
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,}")
    print()
    
    # Tjek for konsulenthuse (dårligt)
    print("⚠️  TVIVLSOMT - KONSELLENTHUSE/PARTNERE:")
    consultant_patterns = [
        '%consult%', '%partner%', '%implement%', '%reseller%', '%advisor%'
    ]
    
    for pattern in consultant_patterns:
        cur.execute('''
            SELECT COUNT(*) FROM companies 
            WHERE (company_name LIKE ? OR evidence_text LIKE ?)
            AND confidence_score >= 4
        ''', (pattern, pattern))
        count = cur.fetchone()[0]
        if count > 0:
            print(f"   '{pattern}': {count:,}")
    print()
    
    # Eksempler på tvivlsomme
    print("❌ EKSEMPLER PÅ TVIVLSOMME:")
    cur.execute('''
        SELECT company_name, country, evidence_text, source_url
        FROM companies
        WHERE (
            company_name LIKE '%consult%' 
            OR company_name LIKE '%partner%'
            OR evidence_text LIKE '%consultant%'
            OR evidence_text LIKE '%partner%'
        )
        AND confidence_score >= 4
        LIMIT 10
    ''')
    for row in cur.fetchall():
        print(f"   • {row[0]} ({row[1]})")
        print(f"     Evidence: {row[2][:100]}...")
        print(f"     URL: {row[3]}")
        print()
    
    # TheirStack (burde være godt)
    print("✅ THEIRSTACK (teknologi scan - burde være SOLIDT):")
    cur.execute('''
        SELECT COUNT(*) FROM companies 
        WHERE source = 'TheirStack' 
        AND confidence_score >= 4
    ''')
    theirstack = cur.fetchone()[0]
    print(f"   TheirStack: {theirstack:,}")
    print()
    
    # Case studies (kan være både godt og skidt)
    print("⚠️  CASE STUDIES (skal gennemgås manuelt):")
    cur.execute('''
        SELECT COUNT(*) FROM companies 
        WHERE evidence_text LIKE '%case study%'
        AND confidence_score >= 4
    ''')
    cases = cur.fetchone()[0]
    print(f"   Case studies: {cases:,}")
    print()
    
    conn.close()
    
    print("=" * 80)
    print("💡 ANBEFALING:")
    print("=" * 80)
    print()
    print("BEHOLD:")
    print("   ✅ TheirStack (teknologi scan - faktisk bevis)")
    print("   ✅ Konkrete case studies OM kunder (ikke AF konsulenthuse)")
    print("   ✅ Job postings HOS slutbrugere (ikke konsulenthuse)")
    print()
    print("FJERN:")
    print("   ❌ Konsulenthuse/partnere (sælger Navision, bruger det ikke)")
    print("   ❌ LinkedIn search results (ikke konkrete beviser)")
    print("   ❌ Job aggregators (Indeed, SimplyHired, etc.)")
    print()
    print("MANUEL REVIEW:")
    print("   ⚠️  Gennemgå største virksomheder én efter én")

if __name__ == '__main__':
    review()
