#!/usr/bin/env python3
"""
THOROUGH REVIEW - LÆS OG FORSTÅ hvert item
Ikke bare filtre på keywords - faktisk analyse!
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# ❌ KLARE PARTNERE/KONSELENTHUSE (sælger Navision)
KNOWN_PARTNERS = {
    # Danske
    'columbus', 'twentyfour', 'abakion', 'jcd', 'obtain', 'alfapeople', 
    'cepheo', 'logos', 'micropartner', 'nav-vision', 'elbis', 'sourceware',
    'nnit', 'kmd', 'systematic', 'bek', 'devoteam', 'recruitit', 'nigel frank',
    'avanade', 'readify', 'hitachi', 'insight', 'softchoice',
    'archerpoint', 'isc', 'turnkey', 'confluent', 'hechler', 'planit',
    'dynamicsdanmark', 'formula micro', 'norriq', 'relateit', 'twoday',
    'ecit', 'innovia', 'saglobal', 'nav24', 'tbk consult', 'bdl',
    
    # Internationale partnere
    'microsoft partner', 'gold partner', 'certified partner',
    'dynamics partner', 'nav partner',
}

# ❌ KLARE AGGREGATORS/NOISE
AGGREGATORS = {
    'simplyhired', 'naukri', 'indeed', 'glassdoor', 'monster',
    'careerbuilder', 'ziprecruiter', 'jobindex', 'jobserve', 'totaljobs',
    'reed', 'linkedin search', 'stackoverflow', 'community.dynamics.com',
    'erpsoftwareblog', 'navisionjobs', 'dynamicsuser',
}

# ✅ GODE KUNDER (kendte Navision brugere)
KNOWN_CUSTOMERS = {
    'rema 1000', 'ørsted', 'vestas', 'carlsberg', 'arla', 'maersk',
    'dsv', 'pandora', 'lego', 'bang olufsen', 'iss', 'tryg', 'novozymes',
    'genmab', 'demant', 'coloplast', 'foss', 'jyske bank', 'spar nord',
    'bilkas', 'føtex', 'netto', 'matas', 'power', 'elgiganten',
    'sandvik', 'scania', 'volvo', 'electrolux', 'h&m', 'ikea',
    'morgan stanley', 'hsbc', 'barclays', 'deutsche bank',
    'siemens', 'bosch', 'bmw', 'mercedes', 'vw', 'audi',
    'heineken', 'nestlé', 'unilever', 'p&g', 'cocacola',
}

def analyze_company(row):
    """
    Analyser EN virksomhed GRUNDIGT
    Returnerer: (keep, confidence_level, reason)
    """
    name = row['company_name'].lower().strip()
    country = row['country']
    evidence = (row['evidence_text'] or '').lower()
    source = (row['source'] or '').lower()
    source_url = (row['source_url'] or '').lower()
    website = (row['website'] or '').lower()
    evidence_type = (row['evidence_type'] or '').lower()
    
    # 1. Er det en KENDT PARTNER?
    for partner in KNOWN_PARTNERS:
        if partner in name:
            return False, 'REJECT', f"KNOWN PARTNER: {partner}"
    
    # 2. Er det en AGGREGATOR/NOISE?
    for agg in AGGREGATORS:
        if agg in source_url or agg in source:
            return False, 'REJECT', f"AGGREGATOR: {agg}"
    
    # 3. Er det en KENDT KUNDE?
    for customer in KNOWN_CUSTOMERS:
        if customer in name:
            return True, 'CONFIRMED', f"KNOWN CUSTOMER: {customer}"
    
    # 4. Læs evidence TEKSTEN grundigt
    # Hvad siger det FAKTISK?
    
    # GODT: Virksomheden BRUGER Navision
    good_signs = [
        # De bruger det selv
        'using dynamics', 'using navision', 'using nav',
        'runs on nav', 'runs on dynamics',
        'went live with', 'gone live with',
        'implemented navision for internal',
        'customer since', 'user since',
        'back-office erp', 'their erp system',
        'production environment',
        
        # TheirStack tech scan
        'theirstack', 'technology detection', 'tech stack',
        
        # Konkrete tal
        'butikker med', 'medarbejdere', 'employees',
        'order', 'daily', 'pr. dag',
    ]
    
    # DÅRLIGT: Partner der skriver om deres arbejde
    bad_signs = [
        # Partner marketing
        'our customer', 'our client', 'their implementation',
        'we implemented', 'we delivered', 'we helped',
        'partner reference', 'customer success story',
        'case study for', 'project for',
        
        # Job postings (ikke faktisk brug)
        'hiring', 'looking for', 'seeking', 'job opportunity',
        'career opportunity', 'now hiring',
        
        # For generisk
        'possibly uses', 'might use', 'likely uses',
    ]
    
    good_count = sum(1 for sign in good_signs if sign in evidence)
    bad_count = sum(1 for sign in bad_signs if sign in evidence)
    
    # 5. Analyser URL
    # Er det virksomhedens EGEN side eller en partners?
    
    # Partner URLs
    partner_url_signs = [
        '/case-studies/', '/case-study/', '/customer-stories/',
        '/referencer/', '/kunden/', '/clients/',
        'partner.microsoft.com', 'appsource.microsoft.com',
    ]
    
    is_partner_url = any(sign in source_url for sign in partner_url_signs)
    
    # 6. Tjek navn for forretningsmodel
    # Konsulenthuse har ofte disse ord
    consultant_words = [
        'consult', 'advisor', 'solutions', 'services',
        'implementation', 'integration', 'systems',
        'technologies', 'group', 'holding',
    ]
    
    is_consultant_name = sum(1 for word in consultant_words if word in name) >= 2
    
    # 7. Saml alt og vurder
    
    # DeresStack = ALTID god (teknologi scan)
    if 'theirstack' in source:
        return True, 'CONFIRMED', 'TheirStack tech scan'
    
    # Kendt kunde = god
    if good_count >= 2 and bad_count == 0:
        return True, 'LIKELY', f'Good evidence ({good_count} signs)'
    
    # Partner URL med "our customer" = dårlig
    if is_partner_url and bad_count >= 1:
        return False, 'REJECT', 'Partner writing about client'
    
    # Konsulenthus navn + partner URL = dårlig
    if is_consultant_name and is_partner_url:
        return False, 'REJECT', 'Consultant company'
    
    # Meget bad signs = dårlig
    if bad_count >= 2:
        return False, 'REJECT', f'Too many bad signs ({bad_count})'
    
    # Tvedligehold: hvis vi er usikre, vær konservativ
    if good_count == 0 and bad_count == 0:
        # Ingen klare tegn - vær konservativ
        if is_consultant_name:
            return False, 'UNCERTAIN', 'Likely consultant (no proof of own use)'
    
    # Default: beholder hvis ikke åbenlyst dårlig
    if bad_count == 0:
        return True, 'UNCERTAIN', 'No red flags found'
    
    return False, 'REJECT', f'Bad signs outweigh good ({bad_count} vs {good_count})'

def thorough_review():
    """Gennemgå ALT grundigt"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter THOROUGH REVIEW...")
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
    print(f"📊 Total: {len(rows):,}")
    print()
    
    confirmed = []
    likely = []
    uncertain = []
    rejected = []
    
    reasons = {}
    
    for i, row in enumerate(rows):
        keep, confidence, reason = analyze_company(row)
        
        if keep:
            if confidence == 'CONFIRMED':
                confirmed.append(row['id'])
            elif confidence == 'LIKELY':
                likely.append(row['id'])
            else:
                uncertain.append(row['id'])
        else:
            rejected.append(row['id'])
        
        # Tæl årsager
        reason_key = reason.split(':')[0]
        reasons[reason_key] = reasons.get(reason_key, 0) + 1
        
        # Progress
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ {i+1}/{len(rows)} (confirmed: {len(confirmed)}, likely: {len(likely)}, uncertain: {len(uncertain)}, rejected: {len(rejected)})")
    
    print()
    print("=" * 80)
    print("📊 RESULTATER:")
    print("=" * 80)
    print(f"✅ CONFIRMED: {len(confirmed):,} ({len(confirmed)/len(rows)*100:.1f}%)")
    print(f"🟡 LIKELY: {len(likely):,} ({len(likely)/len(rows)*100:.1f}%)")
    print(f"🟠 UNCERTAIN: {len(uncertain):,} ({len(uncertain)/len(rows)*100:.1f}%)")
    print(f"❌ REJECTED: {len(rejected):,} ({len(rejected)/len(rows)*100:.1f}%)")
    print()
    
    print("📋 ÅRSAGER:")
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1])[:15]:
        print(f"   {reason}: {count:,}")
    print()
    
    # Eksempler på rejected
    print("❌ EKSEMPLER PÅ REJECTED:")
    cur.execute('''
        SELECT company_name, country, source, evidence_text
        FROM companies
        WHERE id IN ({})
        LIMIT 10
    '''.format(','.join(['?' for _ in rejected[:10]])), rejected[:10])
    for row in cur.fetchall():
        print(f"   • {row[0]} ({row[1]}) - {row[2]}")
        print(f"     Evidence: {row[3][:100]}...")
    print()
    
    # Eksempler på confirmed
    print("✅ EKSEMPLER PÅ CONFIRMED:")
    cur.execute('''
        SELECT company_name, country, source, evidence_text
        FROM companies
        WHERE id IN ({})
        LIMIT 10
    '''.format(','.join(['?' for _ in confirmed[:10]])), confirmed[:10])
    for row in cur.fetchall():
        print(f"   • {row[0]} ({row[1]}) - {row[2]}")
        print(f"     Evidence: {row[3][:100]}...")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("💡 ANBEFALING:")
    print("=" * 80)
    print()
    print(f"BEHOLD: {len(confirmed) + len(likely):,} (confirmed + likely)")
    print(f"FJERN: {len(rejected):,} (rejected)")
    print(f"MANUEL REVIEW: {len(uncertain):,} (uncertain)")
    
    return len(confirmed), len(likely), len(uncertain), len(rejected)

if __name__ == '__main__':
    try:
        thorough_review()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
