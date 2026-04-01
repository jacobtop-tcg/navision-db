#!/usr/bin/env python3
"""
Filter database to find TRUE NAV customers (not Business Central)
Identifies companies using OLD NAVISION (pre-BC migration targets)
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'

# Keywords that indicate OLD NAV (migration targets)
NAV_ONLY_KEYWORDS = [
    'dynamics nav', 'navision', 'nav 2009', 'nav 2013', 'nav 2015',
    'nav 2016', 'nav 2017', 'nav 2018', 'nav 2019', 'nav 2020',
    'dynamics nav 2009', 'dynamics nav 2013', 'dynamics nav 2015',
    'dynamics nav 2016', 'dynamics nav 2017', 'dynamics nav 2018',
    'dynamics nav 2019', 'dynamics nav 2020', 'nav 14.0', 'nav 15.0',
    'c/al', 'nav on-premise', 'navision stat',
]

# Keywords that indicate BC (already migrated - NOT targets)
BC_KEYWORDS = [
    'business central', 'bc cloud', 'dynamics 365 bc',
    'dynamics 365 business central', 'bc online',
    'cloud erp', 'saas', 'cloud-hosted',
    'went live with business central', 'migrated to business central',
    'gået live med business central', 'migreret til business central',
]

def analyze_database():
    """Analyze database and identify TRUE NAV customers"""
    
    print("=" * 80)
    print("🔍 FILTERING FOR TRUE NAV CUSTOMERS (MIGRATION TARGETS)")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get total count
    cur.execute('SELECT COUNT(*) FROM companies')
    total = cur.fetchone()[0]
    print(f"📊 Total companies in database: {total:,}")
    print()
    
    # Find companies with NAV keywords
    cur.execute('''
        SELECT id, company_name, country, evidence_type, evidence_text, 
               confidence_score, source_url
        FROM companies
        WHERE evidence_text IS NOT NULL
        AND evidence_text != ''
    ''')
    
    rows = cur.fetchall()
    
    nav_only = []  # TRUE NAV customers (migration targets)
    bc_customers = []  # Already on BC (NOT targets)
    unclear = []  # Can't determine
    
    for row in rows:
        evidence = (row['evidence_text'] or '').lower()
        
        # Check for BC (already migrated)
        has_bc = any(bc in evidence for bc in BC_KEYWORDS)
        
        # Check for NAV (could be target)
        has_nav = any(nav in evidence for nav in NAV_ONLY_KEYWORDS)
        
        if has_bc and not has_nav:
            bc_customers.append({
                'company': row['company_name'],
                'country': row['country'],
                'evidence': evidence[:200],
                'url': row['source_url']
            })
        elif has_nav:
            nav_only.append({
                'company': row['company_name'],
                'country': row['country'],
                'evidence': evidence[:200],
                'evidence_type': row['evidence_type'],
                'url': row['source_url'],
                'confidence': row['confidence_score']
            })
        else:
            unclear.append({
                'company': row['company_name'],
                'country': row['country'],
                'evidence': evidence[:200],
                'url': row['source_url']
            })
        
        # Progress
        if len(nav_only) + len(bc_customers) + len(unclear) % 1000 == 0:
            print(f"  ⏳ Processed {len(nav_only) + len(bc_customers) + len(unclear)}...")
    
    conn.close()
    
    # Print results
    print()
    print("=" * 80)
    print("📊 ANALYSIS RESULTS")
    print("=" * 80)
    print()
    print(f"✅ TRUE NAV customers (migration targets): {len(nav_only):,}")
    print(f"❌ Already on BC (NOT targets): {len(bc_customers):,}")
    print(f"❓ Unclear: {len(unclear):,}")
    print()
    
    # Show top NAV customers
    print("🎯 TOP NAV CUSTOMERS (Migration Targets):")
    for item in nav_only[:50]:
        print(f"  ✅ {item['company']} ({item['country']})")
        print(f"     Type: {item['evidence_type']}")
        print(f"     Evidence: {item['evidence'][:100]}...")
        print()
    
    # Show top BC customers
    print()
    print("❌ ALREADY ON BC (NOT targets):")
    for item in bc_customers[:20]:
        print(f"  ❌ {item['company']} ({item['country']})")
        print(f"     Evidence: {item['evidence'][:100]}...")
        print()
    
    # Save results
    results = {
        'nav_only': nav_only,
        'bc_customers': bc_customers,
        'unclear': unclear,
        'summary': {
            'total': total,
            'nav_only_count': len(nav_only),
            'bc_count': len(bc_customers),
            'unclear_count': len(unclear)
        }
    }
    
    import json
    output_path = Path(__file__).parent.parent / 'state' / 'nav-filter-results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_path}")
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
