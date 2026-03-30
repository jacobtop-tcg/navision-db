#!/usr/bin/env python3
"""
FJERN ALLE BULLSHIT CASE STUDIES
Som ikke nævner Navision/Dynamics/ERP specifikt
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

def is_fake_casestudy(name, evidence, source_url):
    """
    Tjek om dette er en BULLSHIT case study
    Som ikke beviser Navision brug
    """
    text = f"{name} {evidence} {source_url}".lower()
    
    # ❌ Fjern hvis det IKKE nævner Navision/Dynamics/ERP
    navision_terms = [
        'navision', 'nav', 'dynamics', 'erp', 'business central',
        'microsoft dynamics', 'ms dynamics', 'd365', 'bc365',
    ]
    
    # Tjek om der er NOGEN Navision-relaterede ord
    has_navision = any(term in text for term in navision_terms)
    
    if not has_navision:
        return True, "NO_NAVISION_MENTION"
    
    # ❌ Fjern hvis det er generisk marketing
    bullshit_patterns = [
        # Generisk marketing uden konkret indhold
        r'case study.*virksomhed',
        r'case study.*customer',
        r'case study.*client',
        r'stærk branding',
        r'website design',
        r'digital marketing',
        r'seo',
        r'social media',
        
        # Ikke ERP relateret
        r'cloud transition',
        r'digital transformation',
        r'it strategi',
        r'rådgivning',
        
        # Uden konkret Navision mention
        r'microsoft.*partner',
        r'certified partner',
    ]
    
    for pattern in bullshit_patterns:
        if re.search(pattern, text):
            # MEN hvis der er konkret Navision mention, behold
            if not any(term in text for term in ['navision', 'dynamics nav', 'using nav', 'went live with nav']):
                return True, f"BULLSHIT:{pattern}"
    
    # ❌ Fjern hvis URL er generisk
    bullshit_urls = [
        '/case-study', '/case-studies', '/kunden/', '/referencer/',
        'erpsoftwareblog', 'nav24', 'tbkconsult',
    ]
    
    for url in bullshit_urls:
        if url in source_url.lower():
            # Tjek om evidence nævner Navision konkret
            if not any(term in evidence.lower() for term in ['navision', 'dynamics nav', 'using nav']):
                return True, f"BULLSHIT_URL:{url}"
    
    return False, None

def remove_fake():
    """Fjern alle bullshit case studies"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter FJERN BULLSHIT...")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent alle med høj kvalitet
    cur.execute('''
        SELECT id, company_name, evidence_text, source_url, source
        FROM companies
        WHERE confidence_score >= 4
        ORDER BY id DESC
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Total: {len(rows):,}")
    print()
    
    remove = []
    reasons = {}
    examples = []
    
    for i, row in enumerate(rows):
        is_fake, reason = is_fake_casestudy(
            row['company_name'],
            row['evidence_text'] or '',
            row['source_url'] or ''
        )
        
        if is_fake:
            remove.append(row['id'])
            reasons[reason] = reasons.get(reason, 0) + 1
            
            if len(examples) < 20:
                examples.append((row['company_name'], row['source'], reason, row['evidence_text'][:80] if row['evidence_text'] else ''))
        
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ {i+1}/{len(rows)} (remove: {len(remove)})")
    
    print()
    print("=" * 80)
    print("📊 RESULTATER:")
    print("=" * 80)
    print(f"❌ FJERN: {len(remove):,} ({len(remove)/len(rows)*100:.1f}%)")
    print(f"✅ BEHOLD: {len(rows) - len(remove):,} ({(len(rows)-len(remove))/len(rows)*100:.1f}%)")
    print()
    
    print("📋 ÅRSAGER:")
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1])[:10]:
        print(f"   {reason}: {count:,}")
    print()
    
    print("❌ EKSEMPLER PÅ BULLSHIT DER BLIVER FJERNET:")
    for name, source, reason, evidence in examples[:15]:
        print(f"   • {name} ({source})")
        print(f"     Årsag: {reason}")
        print(f"     Evidence: {evidence[:80]}...")
        print()
    
    # Opdater database
    if remove:
        print(f"🗑️  Fjerner {len(remove):,} bullshit case studies...")
        cur.execute('''
            UPDATE companies
            SET confidence_score = 1
            WHERE id IN ({})
        '''.format(','.join(['?' for _ in remove])), remove)
        conn.commit()
        print("✅ Opdateret!")
    
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ FJERNET {len(remove):,} BULLSHIT CASE STUDIES!")
    print("=" * 80)
    
    return len(remove)

if __name__ == '__main__':
    try:
        remove_fake()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
