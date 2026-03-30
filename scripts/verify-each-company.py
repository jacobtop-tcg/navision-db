#!/usr/bin/env python3
"""
VERIFIER HVIRK VIRKSOMHED INDIVIDUELT
Går igennem ALT data og tjekker om det er:
✅ Rigtig Navision bruger (behold)
❌ Konsulent/partner (fjern)
❌ Job aggregator (fjern)
❌ Andet skrald (fjern)
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# ❌ KONSELLENTHUSE - Navne der indikerer de SÆLGER Navision
CONSULTANT_PATTERNS = [
    # Danske konsulenthuse
    r'columbus', r'twentyfour', r'abakion', r'jcd', r'obtain',
    r'alfapeople', r'cepheo', r'logos consult', r'micropartner',
    r'nav-vision', r'navision', r'dynamics.?consult', r'erp.?consult',
    r'consulting', r'konsulent', r'advisor', r'partner',
    
    # Internationale
    r'avanade', r'readify', r'hitachi.?solutions', r'insight',
    r'computer.?world', r'cdw', r'softchoice',
    
    # Generelt
    r'implement', r'reseller', r'integrator', r'solutions?',
    r'services?', r'technologies?', r'systems?',
]

# ❌ JOB AGGREGATORS - Ikke rigtige virksomheder
AGGREGATOR_PATTERNS = [
    r'simplyhired', r'naukri', r'indeed', r'glassdoor',
    r'monster', r'careerbuilder', r'ziprecruiter',
    r'jobindex', r'jobserve', r'totaljobs', r'reed',
]

# ❌ NOISE
NOISE_PATTERNS = [
    r'^best\s*\d*', r'^top\s*\d*', r'directory',
    r'currency', r'converter', r'calculator',
    r'^maps\s', r'google\s+maps',
    r'xxx', r'porn', r'casino',
]

# ✅ GODE KILDER
GOOD_SOURCES = [
    'theirstack', 'TheirStack',  # Teknologi scan
    'appsruntheworld',  # Kundedatabase
    'cepheo',  # Case studies om kunder
    'msft_stories',  # Microsoft customer stories
    'nav_customer',  # Navision kunder
    'nav_user',  # Navision brugere
]

def is_consultant(name, evidence, source):
    """Tjek om dette er et konsulenthus/partner"""
    text = f"{name} {evidence} {source}".lower()
    
    # Tjek for konsulent/partner mønstre
    for pattern in CONSULTANT_PATTERNS:
        if re.search(pattern, text):
            return True, pattern
    
    # Tjek om de sælger Navision
    if any(word in text for word in ['microsoft partner', 'gold partner', 'navision partner', 'dynamics partner']):
        return True, 'partner'
    
    if any(word in text for word in ['implementerer', 'implementering', 'go-live', 'implementation']):
        # KUN hvis det er partner der implementerer
        if 'partner' in text or 'consult' in text:
            return True, 'implementation_partner'
    
    return False, None

def is_aggregator(name, evidence, source_url):
    """Tjek om dette er en job aggregator"""
    text = f"{name} {evidence} {source_url}".lower()
    
    for pattern in AGGREGATOR_PATTERNS:
        if re.search(pattern, text):
            return True, pattern
    
    return False, None

def is_noise(name):
    """Tjek om dette er noise"""
    name_lower = name.lower()
    
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return True, pattern
    
    if name[0].isdigit() and len(name) < 5:
        return True, 'starts_with_number'
    
    return False, None

def is_good_source(source, evidence_type):
    """Tjek om kilden er SOLID"""
    source_lower = source.lower() if source else ""
    evidence_lower = evidence_type.lower() if evidence_type else ""
    
    for good in GOOD_SOURCES:
        if good.lower() in source_lower:
            return True, f"good_source:{good}"
    
    return False, None

def verify_company(row):
    """
    Verificer én virksomhed
    Returnerer: (keep, reason)
    """
    name = row['company_name']
    country = row['country']
    evidence = row['evidence_text'] or ""
    source = row['source'] or ""
    source_url = row['source_url'] or ""
    website = row['website'] or ""
    confidence = row['confidence_score']
    
    # 1. Tjek for noise
    noise, pattern = is_noise(name)
    if noise:
        return False, f"NOISE: {pattern}"
    
    # 2. Tjek for job aggregators
    aggregator, pattern = is_aggregator(name, evidence, source_url)
    if aggregator:
        return False, f"AGGREGATOR: {pattern}"
    
    # 3. Tjek for konsulenthuse
    consultant, pattern = is_consultant(name, evidence, source)
    if consultant:
        # MEDMINDER: Nogle konsulenthuse BRUGER også Navision internt
        # Men vi er conservative - fjern dem medmindre TheirStack siger de bruger det
        if 'theirstack' not in source.lower():
            return False, f"CONSULTANT: {pattern}"
    
    # 4. Tjek om det er en GOD kilde
    good_source, reason = is_good_source(source, row['evidence_type'])
    if good_source:
        return True, f"KEEP: {reason}"
    
    # 5. TheirStack er ALTID godt (teknologi scan)
    if 'theirstack' in source.lower():
        return True, "KEEP: TheirStack tech scan"
    
    # 6. Tjek evidence for konkrete beviser
    evidence_lower = evidence.lower()
    
    # Gode tegn
    good_signs = [
        'using dynamics', 'using navision', 'runs on nav',
        'went live', 'go-live', 'production',
        'customer since', 'user since',
        'back-office', 'erp system',
    ]
    
    for sign in good_signs:
        if sign in evidence_lower:
            return True, f"KEEP: evidence has '{sign}'"
    
    # Dårlige tegn
    bad_signs = [
        'hiring.*nav', 'jobs.*nav', 'career.*nav',
        'looking for.*nav', 'seeking.*nav',
        'consultant.*nav', 'partner.*nav',
    ]
    
    for sign in bad_signs:
        if re.search(sign, evidence_lower):
            return False, f"REMOVE: evidence has '{sign}'"
    
    # 7. Hvis vi er her - vurder baseret på kontekst
    # Har de et rigtigt website?
    if website and not website.startswith('http') or 'linkedin' in website.lower():
        # Website ser ikke rigtigt ud
        pass
    
    # Default: Behold hvis confidence er høj og vi ikke fandt problemer
    if confidence >= 4:
        return True, "KEEP: high confidence, no red flags"
    
    return False, "REMOVE: low confidence, uncertain"

def verify_all():
    """Verificer ALLE virksomheder"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter VERIFICATION af alle virksomheder...")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent alle med høj kvalitet
    cur.execute('''
        SELECT * FROM companies
        WHERE confidence_score >= 4
        ORDER BY confidence_score DESC
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Total der skal verificeres: {len(rows):,}")
    print()
    
    keep = []
    remove = []
    reasons = {}
    
    for i, row in enumerate(rows):
        should_keep, reason = verify_company(row)
        
        if should_keep:
            keep.append(row['id'])
        else:
            remove.append(row['id'])
        
        # Tæl årsager
        reason_category = reason.split(':')[0]
        reasons[reason_category] = reasons.get(reason_category, 0) + 1
        
        # Progress
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ Progress: {i+1}/{len(rows)} (keep: {len(keep)}, remove: {len(remove)})")
    
    print()
    print("=" * 80)
    print("📊 RESULTATER:")
    print("=" * 80)
    print(f"✅ BEHOLD: {len(keep):,} ({len(keep)/len(rows)*100:.1f}%)")
    print(f"❌ FJERN: {len(remove):,} ({len(remove)/len(rows)*100:.1f}%)")
    print()
    
    print("📋 ÅRSAGER:")
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"   {reason}: {count:,}")
    print()
    
    # Opdater database - marker fjernede
    if remove:
        print(f"🗑️  Markerer {len(remove):,} virksomheder til fjernelse...")
        # Vi sletter ikke, men markerer med lav confidence
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
    print("✅ VERIFICATION FÆRDIG!")
    print("=" * 80)
    print()
    print(f"Nuværende database har {len(keep):,} VERIFICEREDE virksomheder")
    print(f"Kør export-verified.py for at opdatere JSON/CSV filer")
    
    return len(keep)

if __name__ == '__main__':
    try:
        verify_all()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
