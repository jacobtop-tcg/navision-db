#!/usr/bin/env python3
"""
CDQO - Chief Data Quality Officer (PRODUKTION)
Fjerner Business Central og kun behold ægte NAV/on-premise virksomheder

Kriterier for ÆGTE NAV:
✅ Nævner "Navision", "Dynamics NAV", "NAV 2013/2015/2016/2017/2018"
✅ Nævner C/AL (NAV programmeringssprog)
✅ Nævner on-premise, lokal installation
✅ Jobopslag der søger "NAV udvikler", "Navision konsulent"

Kriterier for BUSINESS CENTRAL (SKAL FJERNES):
❌ Nævner "Business Central", "Dynamics 365 BC"
❌ Nævner AL language (BC programmeringssprog)
❌ Nævner cloud, SaaS, online
❌ BC 2019, 2020, 2021, 2022, 2023, 2024

Kriterier for UKLART (SKAL REVIEWES):
❓ Ingen specifikke nævnelser af hverken NAV eller BC
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
LOG_PATH = Path(__file__).parent.parent / 'logs' / 'cdqo-production.log'
BACKUP_PATH = Path(__file__).parent.parent / 'database' / 'navision-global-backup.db'

# NAV-indikatorer (on-premise, ægte NAV) - CASE INSENSITIVE
NAV_PATTERNS = [
    'navision',
    'dynamics nav',
    'microsoft dynamics nav',
    'nav 2013', 'nav 2015', 'nav 2016', 'nav 2017', 'nav 2018',
    'navision 2013', 'navision 2015', 'navision 2016', 'navision 2017', 'navision 2018',
    'c/al',  # NAV programmeringssprog (IKKE AL som BC bruger)
    'nav udvikler', 'nav konsulent', 'nav developer',
    'navision udvikler', 'navision konsulent',
    'navision statistical',  # Dansk statsinstitution
    'nav/on-premise',
    # Tillægsløsninger til NAV
    'ns-webshop', 'ns-webtid', 'ns-edi', 'ns-produktion',
    'navision webshop', 'nav webshop',
    'c/odbc',  # NAV database access
    'navision sdk',
    # NAV-specifikke termer
    'nav back-office', 'nav backoffice',
    'nav kunde', 'navision kunde',
    'nav integration', 'navision integration',
    'nav rapport', 'nav rapportering',
    'nav server', 'navision server',
    'nav client', 'navision client',
]

# BC-indikatorer (Business Central = CLOUD, IKKE ægte NAV) - CASE INSENSITIVE
BC_PATTERNS = [
    'business central',
    'dynamics 365 business central',
    'dynamics 365 bc',
    'bc 2019', 'bc 2020', 'bc 2021', 'bc 2022', 'bc 2023', 'bc 2024',
    'al language',  # BC programmeringssprog
    'microsoft dynamics 365',
    'cloud erp',
    'saas erp',
    'dynamics 365 cloud',
    # BC-specifikke termer
    'bc online',
    'dynamics 365 finance',  # BC/Finance er cloud
    'dynamics 365 supply chain',  # Cloud
]

def log(message):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def classify_company(evidence_text, company_name, source_url, industry):
    """
    Klassificer om virksomhed er NAV, BC, eller UKLART
    Returnerer: 'NAV', 'BC', 'UNKNOWN'
    """
    text = str(evidence_text or '').lower()
    name = str(company_name or '').lower()
    url = str(source_url or '').lower()
    ind = str(industry or '').lower()
    
    combined = f"{text} {name} {url} {ind}"
    
    # Tjek for BC først (hvis BC nævnes, er det IKKE NAV)
    for pattern in BC_PATTERNS:
        if pattern in combined:
            return 'BC'
    
    # Tjek for NAV
    for pattern in NAV_PATTERNS:
        if pattern in combined:
            return 'NAV'
    
    # Hvis ingen indikatorer, er det uklart
    return 'UNKNOWN'

def create_backup():
    """Lav backup af database før cleanup"""
    import shutil
    if not BACKUP_PATH.exists():
        shutil.copy(str(DB_PATH), str(BACKUP_PATH))
        log(f"Backup created: {BACKUP_PATH}")

def main():
    log("=" * 80)
    log("CDQO PRODUCTION - NAV vs BC Cleanup")
    log("=" * 80)
    
    create_backup()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Få alle virksomheder
    query = 'SELECT id, company_name, country, confidence_score, evidence_text, source_url, industry FROM companies'
    rows = conn.execute(query).fetchall()
    
    nav_ids = []
    bc_ids = []
    unknown_ids = []
    
    nav_companies = []
    bc_companies = []
    unknown_companies = []
    
    for row in rows:
        classification = classify_company(
            row['evidence_text'], 
            row['company_name'], 
            row['source_url'],
            row['industry']
        )
        
        if classification == 'NAV':
            nav_ids.append(row['id'])
            nav_companies.append(row)
        elif classification == 'BC':
            bc_ids.append(row['id'])
            bc_companies.append(row)
        else:
            unknown_ids.append(row['id'])
            unknown_companies.append(row)
    
    total = len(rows)
    log(f"\n=== KLASSIFICERING AF {total} VIRKSOMHEDER ===")
    log(f"✅ Ægte NAV: {len(nav_companies)} ({len(nav_companies)/total*100:.1f}%)")
    log(f"❌ Business Central: {len(bc_companies)} ({len(bc_companies)/total*100:.1f}%)")
    log(f"❓ Uklart: {len(unknown_companies)} ({len(unknown_companies)/total*100:.1f}%)")
    
    # Vis eksempler på BC der skal fjernes
    if bc_companies:
        log(f"\n=== EKSEMPLER PÅ BC (SKAL FJERNES) ===")
        for company in bc_companies[:10]:
            log(f"  ❌ {company['company_name']} ({company['country']})")
            log(f"     Evidence: {company['evidence_text'][:100]}...")
    
    # Spørg om cleanup skal køres
    log(f"\n=== ANBEFALING ===")
    log(f"1. Fjern {len(bc_companies)} BC-virksomheder (ikke ægte NAV)")
    log(f"2. Behold {len(nav_companies)} ægte NAV-virksomheder")
    log(f"3. Review {len(unknown_companies)} uklare virksomheder manuelt")
    
    # Gem resultater som JSON for review
    results_file = Path(__file__).parent.parent / 'state' / 'cdqo-classification.json'
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'total': total,
        'nav_count': len(nav_companies),
        'bc_count': len(bc_companies),
        'unknown_count': len(unknown_companies),
        'nav_percentage': len(nav_companies)/total*100 if total else 0,
        'bc_ids': bc_ids,
        'nav_ids': nav_ids,
        'unknown_ids': unknown_ids,
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    log(f"\nResultater gemt: {results_file}")
    log(f"BC IDs til sletning: {len(bc_ids)}")
    
    conn.close()
    
    return results

if __name__ == '__main__':
    main()
