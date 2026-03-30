#!/usr/bin/env python3
"""
VERIFIED Export - Kun virksomheder med høj kvalitet
Krav:
  ✅ evidence_text IKKE tom (skal have konkret tekst, ikke bare URL)
  ✅ source_url IKKE tom (direkte link til kilde)
  ✅ confidence_score >= 4
  ✅ IKKE noise (best, top, maps, porn, etc.)
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

# NOISE patterns
NOISE_PATTERNS = [
    r'^best\s*\d*', r'^top\s*\d*', r'^\d+\s*best', r'near\s*me', r'directory',
    r'currency', r'converter', r'exchange\s*rate', r'valuta', r'usd\s*to', r'eur\s*to',
    r'calculator', r'omregner', r'rechner', r'speed\s*test',
    r'^how\s+(to|long|much)', r'^what\s+is', r'^guide\s+to', r'tutorial', r'faq',
    r'vs\b', r'versus', r'comparison', r'review\b', r'horoscope', r'zodiac',
    r'^r/', r'reddit', r'forum', r'thread', r'discussion', r'comments',
    r'^maps\s', r'google\s+maps', r'yahoo\s+search', r'login\b', r'sign\s+in',
    r'qr\s+code', r'password', r'email\s+recovery',
    r'xxx', r'porn', r'casino', r'betting',
    r'time\s+in', r'timezone', r'clock\s+', r'live\s*$',
    r'clothing\s+online', r'boutique\s+', r'damen\s+', r'herren\s+',
]

def is_noise(name):
    name_lower = name.lower()
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return True
    if name[0].isdigit() and len(name) < 5:
        return True
    if len(name) < 4 and ' ' not in name:
        return True
    return False

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def export_verified():
    """Exporter KUN verificerede virksomheder"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter VERIFIED export...")
    print("=" * 60)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # KRITISK: Hent KUN virksomheder med:
    # - evidence_text IKKE tom (har BEVIS)
    # - source_url IKKE tom (har DIREKTE LINK til kilde)
    # - confidence >= 4 (høj kvalitet)
    cur.execute('''
        SELECT 
            company_name,
            country,
            industry,
            evidence_type,
            evidence_text,
            confidence_score,
            source,
            website,
            source_url,
            discovered_at,
            employees,
            headquarters_address,
            linkedin_url
        FROM companies
        WHERE 
            evidence_text IS NOT NULL 
            AND evidence_text != ''
            AND source_url IS NOT NULL 
            AND source_url != ''
            AND confidence_score >= 4
        ORDER BY confidence_score DESC, discovered_at DESC
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Fra database: {len(rows)} virksomheder (har evidence + source_url + 4★)")
    
    # Filtrer noise
    companies = []
    noise_removed = 0
    for row in rows:
        if is_noise(row['company_name']):
            noise_removed += 1
            continue
        
        companies.append({
            'name': row['company_name'],
            'country': row['country'],
            'industry': row['industry'] or '',
            'evidence_type': row['evidence_type'] or '',
            'evidence': row['evidence_text'][:500],  # Trim meget lang evidence
            'confidence': row['confidence_score'],
            'source': row['source'] or '',
            'website': row['website'] or '',
            'source_url': row['source_url'] or '',  # DIREKTE LINK TIL KILDE
            'discovered': row['discovered_at'] or '',
            'employees': row['employees'] or '',
            'address': row['headquarters_address'] or '',
            'linkedin': row['linkedin_url'] or ''
        })
    
    conn.close()
    
    # Statistik
    total_before = len(rows)
    total_after = len(companies)
    
    print(f"❌ Fjernet noise: {noise_removed}")
    print(f"✅ Kvalificeret: {total_after}")
    print()
    print("=" * 60)
    print("📁 OUTPUT:")
    print("=" * 60)
    
    # Gem JSON
    with open(EXPORT_DIR / 'companies-verified.json', 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    print(f"  ✅ companies-verified.json ({total_after:,} virksomheder)")
    
    # Gem CSV
    df = pd.DataFrame(companies)
    df.to_csv(EXPORT_DIR / 'companies-verified.csv', index=False, encoding='utf-8')
    print(f"  ✅ companies-verified.csv ({total_after:,} virksomheder)")
    
    # Eksempel på data
    print()
    print("=" * 60)
    print("📋 EKSEMPLER PÅ VERIFICERET DATA:")
    print("=" * 60)
    for i, c in enumerate(companies[:5], 1):
        print(f"\n{i}. {c['name']} ({c['country']}) - {c['confidence']}★")
        print(f"   📝 Evidence: {c['evidence'][:100]}...")
        print(f"   🔗 Kilde: {c['source_url']}")
        if c['website']:
            print(f"   🌐 Website: {c['website']}")
    
    # Metadata
    metadata = {
        'total_companies': len(companies),
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'quality_criteria': {
            'evidence_required': True,
            'source_url_required': True,
            'min_confidence': 4,
            'noise_filtered': True
        },
        'removed': {
            'noise': noise_removed,
            'missing_evidence': total_before - len(companies) - noise_removed
        }
    }
    
    with open(EXPORT_DIR / 'metadata-verified.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ metadata-verified.json")
    
    print()
    print("=" * 60)
    print("✅ VERIFIED EXPORT FÆRDIG!")
    print("=" * 60)
    print(f"\n🎯 KVALITET: 100% har:")
    print(f"   ✅ Konkret evidence/bevis")
    print(f"   ✅ Direkte link til kilde (source_url)")
    print(f"   ✅ Høj kvalitet (4-5★)")
    print(f"\n💡 Brug: companies-verified.json for den RENE liste!")
    
    return len(companies)

if __name__ == '__main__':
    try:
        export_verified()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
