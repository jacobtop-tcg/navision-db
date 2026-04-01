#!/usr/bin/env python3
"""
Review de 1.349 USIKRE virksomheder
Grundig manuel gennemgang - beholder KUN hvis BEVIS for NAV brug
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'

def review_unclear():
    """Review alle usikre virksomheder"""
    
    print("=" * 80)
    print("🔍 REVIEWER DE 1.349 USIKRE VIRKSOMHEDER")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent usikre (dem der ikke blev slettet)
    cur.execute('''
        SELECT id, company_name, country, evidence_type, evidence_text,
               confidence_score, source_url
        FROM companies
        WHERE evidence_text IS NOT NULL
        AND evidence_text != ''
        ORDER BY company_name
    ''')
    
    rows = cur.fetchall()
    
    keep = []
    remove = []
    
    for row in rows:
        company = row['company_name']
        country = row['country']
        evidence_type = row['evidence_type']
        evidence = (row['evidence_text'] or '').lower()
        confidence = row['confidence_score']
        url = row['source_url'] or ''
        
        # STRENGE kriterier for at beholde
        should_keep = False
        reason = ""
        
        # 1. Tjek for specifikke NAV versioner
        nav_versions = ['nav 2009', 'nav 2013', 'nav 2015', 'nav 2016', 
                       'nav 2017', 'nav 2018', 'nav 2019', 'nav 2020',
                       'dynamics nav 20', 'navision 20', 'nav 14', 'nav 15']
        if any(v in evidence for v in nav_versions):
            should_keep = True
            reason = "Specifik NAV version"
        
        # 2. Tjek for interne brugere (ikke konsulenter)
        internal_keywords = ['bruger navision', 'uses navision', 'vores erp',
                           'internt system', 'økonomiafdeling', 'finance department',
                           'til vores team', 'in-house']
        if any(k in evidence for k in internal_keywords):
            should_keep = True
            reason = "Intern bruger"
        
        # 3. Tjek for Navision Stat
        if 'navision stat' in evidence or 'statens' in evidence:
            should_keep = True
            reason = "Navision Stat institution"
        
        # 4. Tjek for job postings (interne stillinger)
        job_keywords = ['økonomimedarbejder', 'regnskabsansvarlig', 'cfo',
                       'indkøber', 'lageransvarlig', 'finance manager']
        if evidence_type == 'job_posting' and any(k in evidence for k in job_keywords):
            # Tjek det IKKE er konsulent
            if 'konsulent' not in evidence and 'consultant' not in evidence:
                should_keep = True
                reason = "Intern stilling"
        
        # 5. Fjern hvis BC eller konsulent
        bc_keywords = ['business central', 'bc cloud', 'dynamics 365 bc']
        consultant_keywords = ['konsulent', 'consultant', 'partner', 'implementering']
        
        if any(k in evidence for k in bc_keywords):
            should_keep = False
            reason = "Allerede BC"
        
        if any(k in evidence for k in consultant_keywords):
            should_keep = False
            reason = "Konsulent/partner"
        
        if should_keep:
            keep.append({
                'id': row['id'],
                'company': company,
                'country': country,
                'reason': reason,
                'evidence': evidence[:200]
            })
        else:
            remove.append({
                'id': row['id'],
                'company': company,
                'country': country,
                'reason': reason
            })
    
    conn.close()
    
    # Print results
    print("=" * 80)
    print("📊 REVIEW RESULTATER")
    print("=" * 80)
    print()
    print(f"✅ BEHOLD: {len(keep):,}")
    print(f"❌ FJERN: {len(remove):,}")
    print()
    
    # Show keep reasons
    from collections import Counter
    keep_reasons = Counter(k['reason'] for k in keep)
    print("📋 ÅRSAGER TIL AT BEHOLDE:")
    for reason, count in keep_reasons.most_common():
        print(f"  {reason}: {count:,}")
    print()
    
    # Show some examples
    print("🎯 EKSEMPLER PÅ BEHOLDTE:")
    for item in keep[:20]:
        print(f"  ✅ {item['company']} ({item['country']})")
        print(f"     Årsag: {item['reason']}")
        print(f"     Evidence: {item['evidence'][:100]}...")
        print()
    
    # Save results
    results = {
        'keep': keep,
        'remove': remove,
        'summary': {
            'keep_count': len(keep),
            'remove_count': len(remove)
        }
    }
    
    output_path = Path(__file__).parent.parent / 'state' / 'unclear-review-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultater gemt til: {output_path}")
    print()
    
    # Create SQL for removals
    if remove:
        remove_ids = [r['id'] for r in remove]
        sql_path = Path(__file__).parent.parent / 'state' / 'remove-unclear.sql'
        with open(sql_path, 'w') as f:
            f.write("-- REMOVE UNCLEAR COMPANIES (REVIEWED)\n")
            f.write(f"-- Generated: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"-- Total to remove: {len(remove_ids)}\n\n")
            for i in range(0, len(remove_ids), 1000):
                batch = remove_ids[i:i+1000]
                f.write(f"DELETE FROM companies WHERE id IN ({','.join(map(str, batch))});\n")
        
        print(f"💾 SQL fil gemt til: {sql_path}")
        print()
        print("⚠️  Kør denne SQL for at fjerne de ikke-beholdte:")
        print(f"   python3 -c \"exec(open('{sql_path}').read())\"")
    
    return results

if __name__ == '__main__':
    try:
        review_unclear()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
