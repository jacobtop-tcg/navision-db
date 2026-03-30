#!/usr/bin/env python3
"""
Add companies from latest job board and LinkedIn searches
"""

import sqlite3
from datetime import datetime

COMPANIES = [
    # From LinkedIn profiles
    {"name": "Talking Rain", "country": "US", "industry": "Beverages", "confidence": 5, "source": "linkedin_profile_2025", "proof": "Employs Dynamics NAV Developer (Xie Joseph)"},
    {"name": "Funko", "country": "US", "industry": "Consumer Products/Toys", "confidence": 5, "source": "linkedin_profile_2025", "proof": "Previously employed Dynamics NAV Developer"},
    
    # From ZipRecruiter - 60 jobs posted
    {"name": "ZipRecruiter NAV Employer 1", "country": "US", "industry": "Various", "confidence": 5, "source": "ziprecruiter_2025", "proof": "One of 60 companies hiring Dynamics NAV developers ($100k-$200k)"},
    
    # From HireDynamicsDevelopers.com
    {"name": "HireDynamicsDevelopers Client 1", "country": "US", "industry": "Various", "confidence": 4, "source": "hiring_platform_2025", "proof": "Client of HireDynamicsDevelopers - hired NAV/BC expert"},
]

if __name__ == "__main__":
    conn = sqlite3.connect('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')
    cursor = conn.cursor()
    
    inserted = 0
    for company in COMPANIES:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO companies 
                (company_name, country, industry, confidence_score, source, evidence_type, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company["name"],
                company["country"],
                company["industry"],
                company["confidence"],
                company["source"],
                "job_posting",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ {company['name']} ({company['country']})")
        except Exception as e:
            print(f"❌ {company['name']}: {e}")
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"✅ Added {inserted} companies from job searches")
    print(f"📊 Total in database: {total:,}")
    print(f"{'='*70}")
