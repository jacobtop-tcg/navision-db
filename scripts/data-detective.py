#!/usr/bin/env python3
"""
DATA DETECTIVE - Find ægte NAVISION kunder (IKKE BC!)
======================================================

Analyserer databasen og finder virksomheder der:
1. Stadig bruger GAMMEL NAVISION (on-premise)
2. IKKE er migreret til Business Central
3. Har "smoking gun" beviser

Output: Liste over målgruppe-virksomheder til migrationssalg
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
OUTPUT_PATH = Path(__file__).parent.parent / 'state' / 'nav-targets.json'

# Keywords der indikerer GAMMEL NAVISION (ikke BC)
NAVISION_KEYWORDS = [
    # Versioner (pre-BC)
    'navision 2009', 'navision 2013', 'navision 2015', 'navision 2016',
    'navision 2017', 'navision 2018', 'navision 2019', 'navision 2020',
    'dynamics nav 2009', 'dynamics nav 2013', 'dynamics nav 2015',
    'dynamics nav 2016', 'dynamics nav 2017', 'dynamics nav 2018',
    'dynamics nav 2019', 'dynamics nav 2020',
    'nav 5.0', 'nav 6.0', 'nav 7.0', 'nav 7.1',  # Version numbers
    'nav 14.0', 'nav 15.0',  # NAV 2018/2019
    
    # On-premise indicators
    'on-premise', 'on premise', 'lokal installation', 'lokal server',
    'own server', 'self-hosted',
    
    # Old technology
    'c/al', 'C/AL',  # Old Navision language (pre-BC)
    'navision classic', 'navision client',
    
    # Danish specific
    'navision stat',  # Government version
]

# Keywords der indikerer BUSINESS CENTRAL (skal filtreres FRA)
BC_KEYWORDS = [
    'business central', 'bc cloud', 'dynamics 365 bc',
    'dynamics 365 business central', 'bc online',
    'cloud erp', 'saas', 'cloud-hosted',
    'went live with business central', 'migrated to business central',
    'gået live med business central', 'migreret til business central',
]

# Smoking gun evidence types (høj værdi)
SMOKING_GUN_TYPES = [
    'job_posting',  # De søger NAV folk = bruger det stadig!
    'nav_evidence',  # Specifik NAV evidence
    'nav_customer_list',  # Kundeliste med NAV
    'technology_stack',  # Tech stack med NAV
]

def analyze_database():
    """Analyser databasen og find ægte NAV kunder"""
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("=" * 80)
    print("🔍 DATA DETECTIVE - Ægte NAVISION kunder (IKKE BC)")
    print("=" * 80)
    print()
    
    # Hent alle companies med evidence
    cur.execute('''
        SELECT id, company_name, country, evidence_type, evidence_text, 
               source_url, confidence_score, discovered_at
        FROM companies
        WHERE confidence_score >= 3
        AND evidence_text IS NOT NULL
        AND evidence_text != ''
        LIMIT 5000
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Analyserer {len(rows)} virksomheder med evidence...")
    print()
    
    results = {
        'genuine_nav': [],  # Ægte NAV kunder (målgruppe)
        'already_bc': [],   # Allerede på BC (ikke målgruppe)
        'unclear': [],      # Uklart
        'stats': {
            'total_analyzed': 0,
            'genuine_nav_count': 0,
            'already_bc_count': 0,
            'unclear_count': 0,
            'by_country': {},
            'by_evidence_type': {},
        }
    }
    
    for i, row in enumerate(rows):
        results['stats']['total_analyzed'] += 1
        
        company = row['company_name']
        country = row['country']
        evidence = (row['evidence_text'] or '').lower()
        url = row['source_url'] or ''
        evidence_type = row['evidence_type']
        
        # Tjek for BC keywords (ikke målgruppe)
        is_bc = any(bc in evidence for bc in BC_KEYWORDS)
        
        # Tjek for NAV keywords (målgruppe)
        is_nav = any(nav in evidence for nav in NAVISION_KEYWORDS)
        
        # Tjek evidence type
        is_smoking_gun = evidence_type in SMOKING_GUN_TYPES
        
        # Klassificér
        if is_bc and not is_nav:
            # Allerede på BC = ikke målgruppe
            results['already_bc'].append({
                'company': company,
                'country': country,
                'evidence': evidence[:200],
                'url': url,
                'reason': 'Already on BC'
            })
            results['stats']['already_bc_count'] += 1
        elif is_nav:
            # Bruger NAV = MÅLGRUPPE! ✅
            results['genuine_nav'].append({
                'company': company,
                'country': country,
                'evidence': evidence[:200],
                'url': url,
                'evidence_type': evidence_type,
                'is_smoking_gun': is_smoking_gun,
                'confidence': row['confidence_score']
            })
            results['stats']['genuine_nav_count'] += 1
            
            # Track country
            if country not in results['stats']['by_country']:
                results['stats']['by_country'][country] = 0
            results['stats']['by_country'][country] += 1
            
            # Track evidence type
            if evidence_type not in results['stats']['by_evidence_type']:
                results['stats']['by_evidence_type'][evidence_type] = 0
            results['stats']['by_evidence_type'][evidence_type] += 1
        else:
            # Uklart
            results['unclear'].append({
                'company': company,
                'country': country,
                'evidence': evidence[:200],
                'url': url
            })
            results['stats']['unclear_count'] += 1
        
        # Progress
        if (i + 1) % 1000 == 0:
            print(f"  ⏳ {i+1}/{len(rows)} (NAV: {results['stats']['genuine_nav_count']}, BC: {results['stats']['already_bc_count']})")
    
    conn.close()
    
    # Print results
    print()
    print("=" * 80)
    print("📊 RESULTATER")
    print("=" * 80)
    print()
    print(f"Analyseret: {results['stats']['total_analyzed']}")
    print(f"✅ Ægte NAV kunder (MÅLGRUPPE): {results['stats']['genuine_nav_count']}")
    print(f"❌ Allerede BC (IKKE målgruppe): {results['stats']['already_bc_count']}")
    print(f"❓ Uklart: {results['stats']['unclear_count']}")
    print()
    
    # Top lande
    print("🌍 TOP LANDE (NAV kunder):")
    sorted_countries = sorted(results['stats']['by_country'].items(), key=lambda x: x[1], reverse=True)[:10]
    for country, count in sorted_countries:
        print(f"  {country}: {count}")
    print()
    
    # Top evidence types
    print("📋 TOP EVIDENCE TYPES:")
    sorted_types = sorted(results['stats']['by_evidence_type'].items(), key=lambda x: x[1], reverse=True)[:10]
    for etype, count in sorted_types:
        print(f"  {etype}: {count}")
    print()
    
    # Vis nogle eksempler
    print("🎯 EKSEMPLER PÅ ÆGTE NAV KUNDER (MÅLGRUPPE):")
    for item in results['genuine_nav'][:20]:
        smoking_gun_marker = "🔫" if item['is_smoking_gun'] else "  "
        print(f"  {smoking_gun_marker} {item['company']} ({item['country']})")
        print(f"     Type: {item['evidence_type']}")
        print(f"     Evidence: {item['evidence'][:100]}...")
        print()
    
    # Gem results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Gemt til: {OUTPUT_PATH}")
    print()
    
    return results

if __name__ == '__main__':
    try:
        analyze_database()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
