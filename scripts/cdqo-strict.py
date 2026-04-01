#!/usr/bin/env python3
"""
CDQO - Chief Data Quality Officer (STRICT MODE)
Fjerner Business Central og kun behold ægte NAV/on-premise virksomheder
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
LOG_PATH = Path(__file__).parent.parent / 'logs' / 'cdqo-strict.log'

# NAV-indikatorer (on-premise, ægte NAV)
NAV_INDICATORS = [
    'navision',
    'dynamics nav',
    'nav 2013', 'nav 2015', 'nav 2016', 'nav 2017', 'nav 2018',
    'microsoft dynamics nav',
    'c/al',  # NAV programmeringssprog
    'navision statistical',
]

# BC-indikatorer (Business Central = CLOUD, ikke on-premise NAV)
BC_INDICATORS = [
    'business central',
    'dynamics 365 business central',
    'dynamics 365 bc',
    'bc 2019', 'bc 2020', 'bc 2021', 'bc 2022', 'bc 2023', 'bc 2024',
    'al language',  # BC programmeringssprog (ikke C/AL)
    'cloud erp',
    'saas erp',
]

def log(message):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def classify_company(evidence_text, company_name, source_url):
    """
    Klassificer om virksomhed er NAV, BC, eller UKLART
    Returnerer: 'NAV', 'BC', 'UNKNOWN'
    """
    text = str(evidence_text or '').lower()
    name = str(company_name or '').lower()
    url = str(source_url or '').lower()
    
    # Tjek for BC først (hvis BC nævnes, er det IKKE NAV)
    for indicator in BC_INDICATORS:
        if indicator in text or indicator in name or indicator in url:
            return 'BC'
    
    # Tjek for NAV
    for indicator in NAV_INDICATORS:
        if indicator in text or indicator in name or indicator in url:
            return 'NAV'
    
    # Hvis ingen indikatorer, er det uklart
    return 'UNKNOWN'

def main():
    log("=" * 60)
    log("CDQO STRICT MODE - NAV vs BC Audit")
    log("=" * 60)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Få alle virksomheder med confidence >= 4
    query = '''
    SELECT id, company_name, country, confidence_score, evidence_text, source_url
    FROM companies
    WHERE confidence_score >= 4
    '''
    
    rows = conn.execute(query).fetchall()
    
    nav_companies = []
    bc_companies = []
    unknown_companies = []
    
    for row in rows:
        classification = classify_company(row['evidence_text'], row['company_name'], row['source_url'])
        
        if classification == 'NAV':
            nav_companies.append(row)
        elif classification == 'BC':
            bc_companies.append(row)
        else:
            unknown_companies.append(row)
    
    log(f"\n=== RESULTATER ===")
    log(f"Total analyseret: {len(rows)}")
    log(f"✅ Ægte NAV: {len(nav_companies)} ({len(nav_companies)/len(rows)*100:.1f}%)")
    log(f"❌ Business Central: {len(bc_companies)} ({len(bc_companies)/len(rows)*100:.1f}%)")
    log(f"❓ Uklart: {len(unknown_companies)} ({len(unknown_companies)/len(rows)*100:.1f}%)")
    
    # Vis BC virksomheder der skal fjernes
    if bc_companies:
        log(f"\n=== BC VIRKSOMHEDER (SKAL FJERNES) ===")
        for company in bc_companies[:20]:  # Vis første 20
            log(f"  ❌ {company['company_name']} ({company['country']})")
    
    # Gem resultater
    results = {
        'total': len(rows),
        'nav': len(nav_companies),
        'bc': len(bc_companies),
        'unknown': len(unknown_companies),
        'nav_percentage': len(nav_companies)/len(rows)*100 if rows else 0
    }
    
    log(f"\n=== KVALITETSMÅL ===")
    log(f"Nuværende NAV%: {results['nav_percentage']:.1f}%")
    log(f"Mål: >95% ægte NAV")
    
    if results['nav_percentage'] < 95:
        log(f"⚠️  KVALITET FOR LAV! {len(bc_companies)} BC virksomheder skal fjernes.")
    
    conn.close()
    
    return results

if __name__ == '__main__':
    main()
