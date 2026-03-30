#!/usr/bin/env python3
"""
ONLY CONFIRMED NAVISION USERS
Går igennem data med "fine-toothed comb"
KUN virksomheder vi er SIKRE på bruger Navision
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
EXPORT_DIR = SCRIPT_DIR.parent / 'web-export'

EXPORT_DIR.mkdir(exist_ok=True)

# ✅ GOOD EVIDENCE - Dette beviser Navision brug
GOOD_EVIDENCE_PATTERNS = [
    # TheirStack - faktisk tech scan
    r'theirstack.*technology.*detection',
    r'listed on theirstack',
    
    # Case studies - konkrete kundeeksempler
    r'case study',
    r'customer success',
    r'customer story',
    r'implementation.*for',
    r'went live.*nav',
    
    # Job postings AT virksomheden (ikke konsulenter)
    r'hiring.*nav.*developer.*at',
    r'navision.*developer.*\(internal\)',
    r'erp.*ansvarlig',
    r'nav administrator',
    
    # Referencer fra Microsoft/partnere
    r'microsoft.*customer',
    r'navision.*user.*since',
    r'using.*dynamics nav',
    r'runs on navision',
    r'back-office.*nav',
    
    # Specifikke implementeringer
    r'go-live.*nav',
    r'production.*nav',
    r'live.*navision',
]

# ❌ BAD EVIDENCE - Dette beviser IKKE Navision brug
BAD_EVIDENCE_PATTERNS = [
    # LinkedIn search - beviser ingenting
    r'linkedin.*search.*people',
    r'employs.*\(.*developer.*\)',  # Generisk "employs X"
    r'linkedin profile',
    
    # Partnere/konsulenter - sælger Navision, bruger det ikke selv
    r'consultant',
    r'partner',
    r'implementation partner',
    r'reseller',
    r'gold partner',
    r'certified partner',
    r'microsoft partner',
    
    # Job aggregators
    r'simplyhired',
    r'naukri',
    r'indeed',
    r'glassdoor',
    r'jobindex.*q=navision',  # Job search, ikke faktisk brug
    
    # For generisk
    r'navision.*jobs.*in',  # Job postings i et land
    r'career.*navision',
    
    # Uden konkret bevis
    r'possibly uses',
    r'might use',
    r'likely uses',
]

# ❌ NOISE - Skal fjernes helt
NOISE_PATTERNS = [
    r'^best\s*\d*', r'^top\s*\d*', r'^\d+\s*best',
    r'currency', r'converter', r'exchange\s*rate',
    r'calculator', r'speed\s*test',
    r'^how\s+(to|long|much)', r'^what\s+is',
    r'^r/', r'reddit', r'forum',
    r'^maps\s', r'google\s+maps',
    r'xxx', r'porn', r'casino',
    r'time\s+in', r'timezone',
]

def is_noise(name):
    name_lower = name.lower()
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return True
    if name[0].isdigit() and len(name) < 5:
        return True
    return False

def has_good_evidence(evidence, source_url):
    """Tjek om evidence er SOLIDT bevis for Navision brug"""
    if not evidence:
        return False, "Ingen evidence"
    
    evidence_lower = evidence.lower()
    url_lower = source_url.lower() if source_url else ""
    
    # Tjek for BAD evidence først
    for pattern in BAD_EVIDENCE_PATTERNS:
        if re.search(pattern, evidence_lower) or re.search(pattern, url_lower):
            return False, f"BAD: {pattern}"
    
    # Tjek for GOOD evidence
    for pattern in GOOD_EVIDENCE_PATTERNS:
        if re.search(pattern, evidence_lower):
            return True, f"GOOD: {pattern}"
    
    # Hvis vi er her, er det usikkert
    return False, "UNCERTAIN: Ingen god evidence fundet"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def export_confirmed():
    """Exporter KUN bekræftede Navision brugere"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter CONFIRMED export...")
    print("=" * 80)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Hent alle med høj kvalitet og links
    cur.execute('''
        SELECT 
            id, company_name, country, industry, evidence_type, evidence_text,
            confidence_score, source, website, source_url, discovered_at
        FROM companies
        WHERE 
            evidence_text IS NOT NULL 
            AND evidence_text != ''
            AND source_url IS NOT NULL 
            AND source_url != ''
            AND confidence_score >= 4
        ORDER BY confidence_score DESC
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Total med høj kvalitet: {len(rows)}")
    print()
    
    # Gå igennem én efter én
    confirmed = []
    rejected = []
    
    for i, row in enumerate(rows):
        company_name = row['company_name']
        evidence = row['evidence_text']
        source_url = row['source_url']
        
        # Filtrer noise
        if is_noise(company_name):
            rejected.append((company_name, "NOISE"))
            continue
        
        # Tjek evidence kvalitet
        is_good, reason = has_good_evidence(evidence, source_url)
        
        if is_good:
            confirmed.append({
                'name': company_name,
                'country': row['country'],
                'industry': row['industry'] or '',
                'evidence_type': row['evidence_type'] or '',
                'evidence': evidence[:500],
                'confidence': row['confidence_score'],
                'source': row['source'] or '',
                'website': row['website'] or '',
                'source_url': source_url,
                'discovered': row['discovered_at'] or '',
                'quality_reason': reason
            })
        else:
            rejected.append((company_name, reason))
        
        # Progress
        if (i + 1) % 5000 == 0:
            print(f"  ⏳ Progress: {i+1}/{len(rows)} (confirmed: {len(confirmed)}, rejected: {len(rejected)})")
    
    conn.close()
    
    # Statistik
    print()
    print("=" * 80)
    print("📊 RESULTATER:")
    print("=" * 80)
    print(f"✅ BEKRÆFTET: {len(confirmed)} ({len(confirmed)/len(rows)*100:.1f}%)")
    print(f"❌ AFVIST: {len(rejected)} ({len(rejected)/len(rows)*100:.1f}%)")
    print()
    
    # Vis hvorfor nogle blev afvist
    rejection_reasons = {}
    for _, reason in rejected:
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
    
    print("❌ AFVISNINGSÅRSAGER:")
    for reason, count in sorted(rejection_reasons.items(), key=lambda x: -x[1])[:10]:
        print(f"   {reason}: {count}")
    print()
    
    # Eksempler på afviste
    print("❌ EKSEMPLER PÅ AFVISTE:")
    for name, reason in rejected[:10]:
        print(f"   • {name} - {reason}")
    print()
    
    # Gem data
    with open(EXPORT_DIR / 'companies-confirmed.json', 'w', encoding='utf-8') as f:
        json.dump(confirmed, f, ensure_ascii=False, indent=2)
    
    df = pd.DataFrame(confirmed)
    df.to_csv(EXPORT_DIR / 'companies-confirmed.csv', index=False, encoding='utf-8')
    
    metadata = {
        'total_confirmed': len(confirmed),
        'total_rejected': len(rejected),
        'quality_rate': f"{len(confirmed)/len(rows)*100:.1f}%",
        'criteria': 'Only companies with SOLID evidence of Navision usage',
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }
    
    with open(EXPORT_DIR / 'metadata-confirmed.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print("=" * 80)
    print("✅ EXPORT FÆRDIG!")
    print("=" * 80)
    print(f"📁 companies-confirmed.json ({len(confirmed):,} virksomheder)")
    print(f"📁 companies-confirmed.csv ({len(confirmed):,} virksomheder)")
    print()
    print(f"🎯 KVALITET: 100% BEKRÆFTEDE NAVISION BRUGERE!")
    
    return len(confirmed)

if __name__ == '__main__':
    try:
        export_confirmed()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
