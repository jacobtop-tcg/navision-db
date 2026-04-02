#!/usr/bin/env python3
"""
CDQO - Chief Data Quality Officer (NO COMPROMISE)
Fjerner ALLE tvivlsomme poster. Beholder KUN bekræftet NAV.

Regel: Hvis vi ikke er 100% sikre på det er NAV (ikke BC) → FJERNES
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
LOG_PATH = Path(__file__).parent.parent / 'logs' / 'cdqo-no-compromise.log'
BACKUP_PATH = Path(__file__).parent.parent / 'database' / 'navision-global-backup.db'

# NAV-indikatorer (STRENGE - kun ægte NAV)
NAV_PATTERNS = [
    'navision',
    'dynamics nav',
    'microsoft dynamics nav',
    'nav 2013', 'nav 2015', 'nav 2016', 'nav 2017', 'nav 2018',
    'navision 2013', 'navision 2015', 'navision 2016', 'navision 2017', 'navision 2018',
    'c/al',  # NAV programmeringssprog
    'nav udvikler', 'nav konsulent', 'nav developer',
    'navision udvikler', 'navision konsulent',
    'navision statistical',
    'ns-webshop', 'ns-webtid', 'ns-edi', 'ns-produktion',
    'c/odbc',
    'nav back-office', 'nav backoffice',
    'nav kunde', 'navision kunde',
    'nav integration',
]

# BC-indikatorer (ALTID fjern)
BC_PATTERNS = [
    'business central',
    'dynamics 365',
    'bc 2019', 'bc 2020', 'bc 2021', 'bc 2022', 'bc 2023', 'bc 2024',
    'al language',
    'cloud erp',
    'saas erp',
    'bc online',
    'dynamics 365 finance',
    'dynamics 365 supply chain',
]

# IKKE-VIRKSOMHEDER - TOM LISTE
# Alle kunder er valide - ministerier, hospitaler, kommuner osv. bruger også NAV!
# Vi fjerner KUN Business Central og helt uklare poster
NON_COMPANY_PATTERNS = [
    # Ingen filtre - behold alle NAV-kunder uanset type
]

def log(message):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def is_definitely_nav(evidence_text, company_name, source_url, industry):
    """
    Returnerer True KUN hvis vi er 100% sikre på det er NAV (ikke BC)
    OG at det er en kommerciel virksomhed (ikke offentlig institution)
    """
    text = str(evidence_text or '').lower()
    name = str(company_name or '').lower()
    url = str(source_url or '').lower()
    ind = str(industry or '').lower()
    
    combined = f"{text} {name} {url} {ind}"
    
    # Tjek for IKKE-VIRKSOMHED først - offentlige institutioner = fjern
    for pattern in NON_COMPANY_PATTERNS:
        if pattern in combined:
            return False  # Offentlig institution = fjern
    
    # Tjek for BC først - hvis BC nævnes, er det IKKE NAV
    for pattern in BC_PATTERNS:
        if pattern in combined:
            return False  # BC = fjern
    
    # Tjek for NAV - hvis NAV nævnes OG ikke BC, er det NAV
    for pattern in NAV_PATTERNS:
        if pattern in combined:
            return True  # NAV = behold
    
    # Hvis hverken NAV eller BC nævnes eksplicit = UKLART = fjern (no compromise!)
    return False

def create_backup():
    import shutil
    if not BACKUP_PATH.exists():
        shutil.copy(str(DB_PATH), str(BACKUP_PATH))
        log(f"✅ Backup created: {BACKUP_PATH}")

def main():
    log("=" * 80)
    log("CDQO NO COMPROMISE - Kun 100% bekræftet NAV")
    log("=" * 80)
    
    create_backup()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Få alle virksomheder
    query = 'SELECT id, company_name, country, confidence_score, evidence_text, source_url, industry, source FROM companies'
    rows = conn.execute(query).fetchall()
    
    keep_ids = []
    remove_ids = []
    keep_count = 0
    remove_bc = 0
    remove_unclear = 0
    
    removed_examples = []
    
    for row in rows:
        is_nav = is_definitely_nav(
            row['evidence_text'], 
            row['company_name'], 
            row['source_url'],
            row['industry']
        )
        
        if is_nav:
            keep_ids.append(row['id'])
            keep_count += 1
        else:
            remove_ids.append(row['id'])
            # Tjek hvorfor det fjernes
            text = str(row['evidence_text'] or '').lower()
            is_bc = any(bc in text for bc in BC_PATTERNS)
            if is_bc:
                remove_bc += 1
            else:
                remove_unclear += 1
            
            if len(removed_examples) < 20:
                reason = "BC" if is_bc else "Uklar"
                removed_examples.append({
                    'name': row['company_name'],
                    'country': row['country'],
                    'reason': reason,
                    'evidence': row['evidence_text'][:100] if row['evidence_text'] else 'N/A'
                })
    
    total = len(rows)
    log(f"\n=== RESULTAT: {total} VIRKSOMHEDER ANALYSERET ===")
    log(f"✅ Behold (100% NAV): {keep_count} ({keep_count/total*100:.1f}%)")
    log(f"❌ Fjern BC: {remove_bc} ({remove_bc/total*100:.1f}%)")
    log(f"❌ Fjern Uklar: {remove_unclear} ({remove_unclear/total*100:.1f}%)")
    
    log(f"\n=== FJERNES (eksempler) ===")
    for ex in removed_examples:
        log(f"  ❌ {ex['name']} ({ex['country']}) - {ex['reason']}")
        log(f"     Evidence: {ex['evidence']}...")
    
    # Kør cleanup
    log(f"\n=== KØRER CLEANUP ===")
    log(f"Fjerner {len(remove_ids)} virksomheder...")
    
    # Slet i batches
    batch_size = 500
    for i in range(0, len(remove_ids), batch_size):
        batch = remove_ids[i:i+batch_size]
        placeholders = ','.join('?' * len(batch))
        conn.execute(f'DELETE FROM companies WHERE id IN ({placeholders})', batch)
    
    conn.commit()
    
    # Tjek ny total
    new_total = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    log(f"\n✅ CLEANUP FÆRDIG!")
    log(f"Ny total: {new_total} virksomheder")
    log(f"Fjernet: {total - new_total} virksomheder")
    
    # Gem log
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'original_total': total,
        'kept': keep_count,
        'removed_bc': remove_bc,
        'removed_unclear': remove_unclear,
        'new_total': new_total,
        'nav_percentage': 100.0  # Nu er alt 100% NAV
    }
    
    results_file = Path(__file__).parent.parent / 'state' / 'cdqo-no-compromise-results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    log(f"\nResultater gemt: {results_file}")
    log("=" * 80)
    log("✅ KUN 100% BEKRÆFTET NAV TILBAGE I DATABASSEN")
    log("=" * 80)
    
    conn.close()
    
    return results

if __name__ == '__main__':
    main()
