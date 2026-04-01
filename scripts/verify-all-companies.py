#!/usr/bin/env python3
"""
VERIFIER ALLE VIRKSOMHEDER - Grundig kvalitetstjek
Fjerner falske positiver, beholder kun ægte NAV kunder
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import re

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'

# ❌ FJERN DISSE (ikke målgruppe)
REMOVE_KEYWORDS = [
    # Already on BC
    'business central', 'bc cloud', 'dynamics 365 bc',
    'migrated to business central', 'gået live med business central',
    'bc online', 'cloud erp',
    
    # Partners/consultants (sælger det, bruger det ikke selv)
    'microsoft partner', 'nav partner', 'dynamics partner',
    'implementering', 'implementation partner',
    'consultant', 'konsulent', 'rådgivning',
    'for vores kunder', 'for our clients',
    'vi implementerer', 'we implement',
    
    # Udviklere/freelancers (ikke slutbrugere)
    'nav udvikler', 'nav developer', 'freelance',
    'udviklingsbureau', 'development agency',
    
    # Job portals (ikke virksomheder)
    'jobindex', 'indeed', 'glassdoor', 'linkedin jobs',
    'jobportal', 'job board',
    
    # For vague
    'maybe uses', 'possibly uses', 'might use',
]

# ✅ BEHOLD DISSE (ægte NAV kunder)
KEEP_KEYWORDS = [
    # Specific NAV versions
    'nav 2009', 'nav 2013', 'nav 2015', 'nav 2016',
    'nav 2017', 'nav 2018', 'nav 2019', 'nav 2020',
    'dynamics nav 20', 'navision 20',
    
    # Internal users
    'bruger navision', 'uses navision', 'bruger dynamics nav',
    'voreserp', 'our erp', 'internt system',
    'økonomiafdeling', 'finance department',
    'indkøber', 'purchaser', 'lageransvarlig', 'warehouse',
    
    # Navision Stat (offentlige)
    'navision stat', 'statens', 'offentlig', 'institution',
    
    # Job postings for INTERNAL positions
    'til vores team', 'internal', 'in-house',
    'økonomimedarbejder', 'regnskabsansvarlig', 'cfo',
]

# ✅ BEHOLD DISSE EVIDENCE TYPES
KEEP_EVIDENCE_TYPES = [
    'job_posting',      # Job postings (hvis interne)
    'navision_stat',    # Offentlige institutioner
    'theirstack',       # TheirStack tech detection
    'technology_stack', # Tech stack pages
    'customer_reference', # Customer references
    'verified_customer', # Verified customers
    'smoking_gun',      # Smoking guns
]

# ❌ FJERN DISSE EVIDENCE TYPES (lav kvalitet)
REMOVE_EVIDENCE_TYPES = [
    'market_research',  # For vague
    'case_study',       # Ofte BC eller partnere
    'partner',          # Partnere, ikke kunder
    'services',         # Konsulenter
    'community',        # Communities, ikke virksomheder
    'freelance',        # Freelancere
    'jobportal',        # Job portals
]

def verify_company(row):
    """
    Verificer én virksomhed
    Returnerer: ('keep', 'remove', 'unclear'), reason
    """
    company = row['company_name']
    country = row['country']
    evidence_type = row['evidence_type']
    evidence = (row['evidence_text'] or '').lower()
    url = row['source_url'] or ''
    confidence = row['confidence_score']
    
    # 1. Tjek evidence type først
    if evidence_type in REMOVE_EVIDENCE_TYPES:
        return 'remove', f'Evidence type {evidence_type} for lav kvalitet'
    
    if evidence_type in KEEP_EVIDENCE_TYPES:
        # High quality evidence type - keep unless proven otherwise
        pass
    
    # 2. Tjek for REMOVE keywords
    for keyword in REMOVE_KEYWORDS:
        if keyword in evidence:
            return 'remove', f'Indeholder "{keyword}" - ikke målgruppe'
    
    # 3. Tjek for KEEP keywords
    for keyword in KEEP_KEYWORDS:
        if keyword in evidence:
            return 'keep', f'Indeholder "{keyword}" - ægte NAV kunde'
    
    # 4. Tjek confidence score
    if confidence >= 4:
        return 'keep', f'Høj confidence ({confidence}) - beholder'
    
    if confidence == 1:
        return 'remove', f'Lav confidence (1) - for usikker'
    
    # 5. Tjek company name for konsulenter/partnere
    company_lower = company.lower()
    consultant_patterns = [
        'consulting', 'konsulent', 'advisor', 'partner',
        'solutions', 'services', 'group', 'aps', 'a/s',
    ]
    
    # Hvis navn indeholder consultant/partner OG evidence er vag
    if any(p in company_lower for p in consultant_patterns):
        if len(evidence) < 50:  # Vag evidence
            return 'unclear', f'Konsulent/partner navn med vag evidence'
    
    # 6. Default - beholder hvis tvivl
    return 'unclear', 'Kan ikke afgøre - beholder indtil videre'

def verify_all():
    """Verificer alle virksomheder i databasen"""
    
    print("=" * 80)
    print("🔍 VERIFICERER ALLE VIRKSOMHEDER - GRUNDIG KVALITETSTJEK")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent alle virksomheder
    cur.execute('''
        SELECT id, company_name, country, evidence_type, evidence_text,
               confidence_score, source_url, discovered_at
        FROM companies
    ''')
    
    rows = cur.fetchall()
    total = len(rows)
    
    print(f"📊 Verificerer {total:,} virksomheder...")
    print()
    
    results = {
        'keep': [],
        'remove': [],
        'unclear': [],
    }
    
    for i, row in enumerate(rows):
        decision, reason = verify_company(row)
        
        results[decision].append({
            'id': row['id'],
            'company': row['company_name'],
            'country': row['country'],
            'evidence_type': row['evidence_type'],
            'reason': reason,
        })
        
        # Progress
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ {i+1:,}/{total:,} (Keep: {len(results['keep']):,}, Remove: {len(results['remove']):,}, Unclear: {len(results['unclear']):,})")
    
    conn.close()
    
    # Print results
    print()
    print("=" * 80)
    print("📊 VERIFIKATION RESULTATER")
    print("=" * 80)
    print()
    print(f"✅ BEHOLD (ægte NAV kunder): {len(results['keep']):,}")
    print(f"❌ FJERN (ikke målgruppe): {len(results['remove']):,}")
    print(f"❓ USIKKER (manuel review): {len(results['unclear']):,}")
    print()
    
    # Show removal reasons
    from collections import Counter
    remove_reasons = Counter(r['reason'].split(' - ')[0] for r in results['remove'])
    print("🗑️ TOP ÅRSAGER TIL FJERNELSE:")
    for reason, count in remove_reasons.most_common(10):
        print(f"  {reason}: {count:,}")
    print()
    
    # Save results
    import json
    output_path = Path(__file__).parent.parent / 'state' / 'verification-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultater gemt til: {output_path}")
    print()
    
    # Create SQL to remove companies
    remove_ids = [r['id'] for r in results['remove']]
    sql_path = Path(__file__).parent.parent / 'state' / 'remove-companies.sql'
    with open(sql_path, 'w') as f:
        f.write("-- REMOVE UNVERIFIED COMPANIES\n")
        f.write(f"-- Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"-- Total to remove: {len(remove_ids)}\n\n")
        
        # Write in batches of 1000
        for i in range(0, len(remove_ids), 1000):
            batch = remove_ids[i:i+1000]
            f.write(f"DELETE FROM companies WHERE id IN ({','.join(map(str, batch))});\n")
    
    print(f"💾 SQL fil gemt til: {sql_path}")
    print()
    print("⚠️  REVIEW SQL FILEN FØR DU KØRER DEN!")
    print()
    
    return results

if __name__ == '__main__':
    try:
        verify_all()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
