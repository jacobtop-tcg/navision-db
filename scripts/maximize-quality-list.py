#!/usr/bin/env python3
"""
MAKSIMER LISTEN: Størst MULIGE liste med HØJ kvalitet
Strategi:
1. BEHOLD TheirStack (teknologi scan - 100% sikkert)
2. BEHOLD kendte kunder (Fortune 500, etc.)
3. ANALYSER resten grundigt med bedre logik
4. FJERN kun åbenlyse partnere/aggregatorer
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# ❌ KLARE PARTNERE (fjern ALTID)
PARTNER_KEYWORDS = [
    'microsoft partner', 'gold partner', 'navision partner', 'dynamics partner',
    'certified partner', 'implementation partner', 'reseller',
    'our customer', 'our client', 'we implemented', 'we delivered',
    'customer success', 'case study for', 'project for',
]

# ❌ KLARE AGGREGATORS
AGGREGATORS = [
    'simplyhired', 'naukri', 'indeed', 'glassdoor', 'monster',
    'linkedin.com/search', 'stackoverflow.com', 'community.dynamics.com',
]

# ❌ KENDTE KONSELLENTHUSE
CONSULTANT_NAMES = [
    'columbus', 'twentyfour', 'abakion', 'jcd', 'obtain', 'alfapeople',
    'cepheo', 'logos consult', 'micropartner', 'nav-vision', 'elbis',
    'nnit', 'kmd', 'systematic', 'devoteam', 'nigel frank',
    'avanade', 'readify', 'hitachi solutions', 'insight',
    'archerpoint', 'turnkey', 'dynamicsdanmark', 'norriq', 'twoday',
    'ecit', 'innovia', 'saglobal', 'nav24', 'tbk consult',
]

# ✅ GODE KILDER (behold ALTID)
GOOD_SOURCES = ['theirstack', 'TheirStack']

# ✅ KENDTE KUNDER (behold ALTID)
KNOWN_CUSTOMERS = [
    'rema 1000', 'ørsted', 'vestas', 'carlsberg', 'arla', 'maersk',
    'dsv', 'pandora', 'lego', 'iss', 'tryg', 'novozymes',
    'sandvik', 'scania', 'volvo', 'electrolux', 'h&m', 'ikea',
    'morgan stanley', 'hsbc', 'barclays', 'siemens', 'bosch',
    'bmw', 'mercedes', 'vw', 'audi', 'heineken', 'nestlé',
    'unilever', 'p&g', 'cocacola', 'walmart', 'amazon',
    'target', 'costco', 'home depot', 'lowes', 'best buy',
]

def analyze(row):
    """
    Analyser virksomhed - returner (keep, reason)
    """
    name = row['company_name'].lower()
    evidence = (row['evidence_text'] or '').lower()
    source = (row['source'] or '').lower()
    source_url = (row['source_url'] or '').lower()
    
    # 1. Gode kilder = BEHOLD
    for good in GOOD_SOURCES:
        if good in source:
            return True, "THEIRSTACK"
    
    # 2. Kendte kunder = BEHOLD
    for customer in KNOWN_CUSTOMERS:
        if customer in name:
            return True, f"KNOWN_CUSTOMER:{customer}"
    
    # 3. Kendte partnere = FJERN
    for partner in CONSULTANT_NAMES:
        if partner in name:
            return False, f"CONSULTANT:{partner}"
    
    # 4. Aggregatorer = FJERN
    for agg in AGGREGATORS:
        if agg in source_url:
            return False, f"AGGREGATOR:{agg}"
    
    # 5. Partner keywords i evidence = FJERN
    for kw in PARTNER_KEYWORDS:
        if kw in evidence:
            return False, f"PARTNER_KW:{kw}"
    
    # 6. Tjek om navn indikerer konsulent
    consultant_words = ['consult', 'solutions', 'services', 'technologies', 'systems']
    if sum(1 for w in consultant_words if w in name) >= 2:
        # Multiple consultant words = sandsynligvis konsulent
        # MEN hvis de har TheirStack data, behold
        if 'theirstack' not in source:
            return False, "CONSULTANT_NAME"
    
    # 7. Tjek evidence for faktiske brugssignaler
    use_signs = [
        'using', 'uses', 'run on', 'runs on', 'went live',
        'go-live', 'production', 'back-office', 'erp system',
        'butikker', 'medarbejdere', 'employees', 'orders',
    ]
    
    has_use_sign = any(sign in evidence for sign in use_signs)
    
    # 8. Hvis ingen røde flag og har brugssignaler = BEHOLD
    if has_use_sign:
        return True, "USE_SIGN"
    
    # 9. Default: BEHOLD hvis ingen åbenlyse problemer
    # (bedre at være lidt for inklusiv end for eksklusiv)
    return True, "DEFAULT_KEEP"

def maximize_list():
    """Lav den største mulige korrekte liste"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter MAXIMIZE LIST...")
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
    
    keep = []
    remove = []
    reasons_keep = {}
    reasons_remove = {}
    
    for i, row in enumerate(rows):
        should_keep, reason = analyze(row)
        
        if should_keep:
            keep.append(row['id'])
            reasons_keep[reason] = reasons_keep.get(reason, 0) + 1
        else:
            remove.append(row['id'])
            reasons_remove[reason] = reasons_remove.get(reason, 0) + 1
        
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ {i+1}/{len(rows)} (keep: {len(keep)}, remove: {len(remove)})")
    
    print()
    print("=" * 80)
    print("📊 RESULTATER:")
    print("=" * 80)
    print(f"✅ BEHOLD: {len(keep):,} ({len(keep)/len(rows)*100:.1f}%)")
    print(f"❌ FJERN: {len(remove):,} ({len(remove)/len(rows)*100:.1f}%)")
    print()
    
    print("📋 HVORFOR BEHOLDT:")
    for reason, count in sorted(reasons_keep.items(), key=lambda x: -x[1])[:10]:
        print(f"   {reason}: {count:,}")
    print()
    
    print("📋 HVORFOR FJERNET:")
    for reason, count in sorted(reasons_remove.items(), key=lambda x: -x[1])[:10]:
        print(f"   {reason}: {count:,}")
    print()
    
    # Opdater database
    if remove:
        print(f"🗑️  Fjerner {len(remove):,} virksomheder...")
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
    print(f"✅ MAKSIMERET LISTE: {len(keep):,} virksomheder")
    print("=" * 80)
    
    return len(keep)

if __name__ == '__main__':
    try:
        maximize_list()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
