#!/usr/bin/env python3
"""
GENOPBYG DATABASEN - Behold kvalitet, fjern kun falske
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'

def rebuild():
    """Genopbyg databasen med sund fornuft"""
    
    print("=" * 80)
    print("🔍 GENOPBYGGER DATABASE - SUND FORNUFT TILGANG")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent alle
    cur.execute('''
        SELECT id, company_name, country, evidence_type, evidence_text,
               confidence_score, source_url
        FROM companies
    ''')
    
    rows = cur.fetchall()
    total = len(rows)
    
    print(f"📊 Gennemgår {total:,} virksomheder...")
    print()
    
    keep = []
    remove = []
    
    # Evidence types vi BEHOLDER (kvalitet)
    KEEP_TYPES = [
        'theirstack', 'TheirStack', 'TheirStack/Web',  # Tech stack detection
        'technology_stack',  # Tech stack
        'job_posting', 'Job Posting', 'Jobopslag',  # Job postings
        'smoking_gun', 'smoking_gun_enterprise', 'smoking_gun_job',
        'smoking_gun_conference', 'smoking_gun_tech_stack', 'smoking_gun_go_live', 'smoking_gun_case',
        'nav_evidence', 'nav_user_evidence',  # NAV evidence
        'Navision Stat', 'Offentlig',  # Offentlige institutioner
        'customer_reference', 'enterprise_customer', 'verified_customer',  # Kundereferencer
        'case_study', 'Case Study', 'Kundecitat', 'Succeshistorie',  # Case studies (tjekkes)
        'partner_customer', 'partner_customer_list', 'partner_customer_logo',  # Partner kunder
        'web_search', 'enterprise', 'major_customer_database',  # Web research
        'nav_partner_directory', 'Partner kunde',  # Partner directories
        'Jet Reports case study', 'JCD Case', 'DynamicWeb case', 'customer_case',  # Specific cases
    ]
    
    # Evidence types vi FJERNER (lav kvalitet)
    REMOVE_TYPES = [
        'Services', 'Freelance', 'Community', 'Media', 'LinkedIn profil',
        'Facebook', 'Database', 'Lokal avis', 'Partner',  # Ikke slutbrugere
    ]
    
    # Keywords der indikerer IKKE målgruppe
    REMOVE_KEYWORDS = [
        'business central', 'bc cloud', 'dynamics 365 bc',  # Allerede BC
        'migrated to business central', 'gået live med business central',
    ]
    
    # Keywords der indikerer konsulent (ikke slutbruger)
    CONSULTANT_KEYWORDS = [
        'microsoft partner', 'nav partner', 'dynamics partner',
        'vi implementerer', 'we implement', 'for vores kunder', 'for our clients',
    ]
    
    for row in rows:
        company = row['company_name']
        country = row['country']
        evidence_type = row['evidence_type']
        evidence = (row['evidence_text'] or '').lower()
        confidence = row['confidence_score']
        
        should_remove = False
        reason = ""
        
        # 1. Tjek evidence type
        if evidence_type in REMOVE_TYPES:
            should_remove = True
            reason = f"Evidence type {evidence_type}"
        
        # 2. Tjek for BC (allerede migreret)
        if any(k in evidence for k in REMOVE_KEYWORDS):
            should_remove = True
            reason = "Allerede BC"
        
        # 3. Tjek for konsulenter (kun hvis ikke anden god evidence)
        if any(k in evidence for k in CONSULTANT_KEYWORDS):
            # Behold hvis TheirStack eller smoking_gun
            if evidence_type not in ['theirstack', 'TheirStack', 'smoking_gun', 'technology_stack']:
                should_remove = True
                reason = "Konsulent/partner"
        
        if should_remove:
            remove.append({
                'id': row['id'],
                'company': company,
                'country': country,
                'evidence_type': evidence_type,
                'reason': reason
            })
        else:
            keep.append({
                'id': row['id'],
                'company': company,
                'country': country,
                'evidence_type': evidence_type,
            })
    
    conn.close()
    
    # Print results
    print("=" * 80)
    print("📊 GENOPBYGNING RESULTATER")
    print("=" * 80)
    print()
    print(f"✅ BEHOLD: {len(keep):,}")
    print(f"❌ FJERN: {len(remove):,}")
    print()
    
    # Show keep by type
    from collections import Counter
    keep_types = Counter(k['evidence_type'] for k in keep)
    print("📋 BEHOLDT PR. TYPE:")
    for etype, count in keep_types.most_common(20):
        print(f"  {etype}: {count:,}")
    print()
    
    # Show remove reasons
    remove_reasons = Counter(r['reason'] for r in remove)
    print("🗑️  FJERNET ÅRSAG:")
    for reason, count in remove_reasons.most_common():
        print(f"  {reason}: {count:,}")
    print()
    
    # Save results
    results = {
        'keep': keep,
        'remove': remove,
        'summary': {
            'keep_count': len(keep),
            'remove_count': len(remove),
            'keep_by_type': dict(keep_types)
        }
    }
    
    output_path = Path(__file__).parent.parent / 'state' / 'rebuild-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultater gemt til: {output_path}")
    print()
    
    # Create SQL for removals
    if remove:
        remove_ids = [r['id'] for r in remove]
        sql_path = Path(__file__).parent.parent / 'state' / 'rebuild-remove.sql'
        with open(sql_path, 'w') as f:
            f.write("-- REBUILD: REMOVE LOW QUALITY\n")
            f.write(f"-- Generated: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"-- Total to remove: {len(remove_ids)}\n\n")
            for i in range(0, len(remove_ids), 1000):
                batch = remove_ids[i:i+1000]
                f.write(f"DELETE FROM companies WHERE id IN ({','.join(map(str, batch))});\n")
        
        print(f"💾 SQL fil gemt til: {sql_path}")
    
    return results

if __name__ == '__main__':
    try:
        rebuild()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
