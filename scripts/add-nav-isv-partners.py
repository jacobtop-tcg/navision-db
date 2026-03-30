#!/usr/bin/env python3
"""
Add more NAV partners from ISV/Partner directories
"""

COMPANIES = [
    # From MSDynamicsWorld ISV/Partner directory
    {"name": "AlphaBOLD", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "BILL", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "NMB Solutions", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "Vena Solutions", "country": "CA", "industry": "Software", "source": "nav_partner"},
    {"name": "Dynamic Budgets", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "ERP Mechanics", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Insight Works", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "Mekorma", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "insightsoftware", "country": "US", "industry": "Software", "source": "nav_partner"},
    
    # From partner searches
    {"name": "sa.global", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Naviona", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Artifex Partners", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Encore Business Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
]

if __name__ == "__main__":
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect('database/navision-global.db')
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
                4,
                company["source"],
                "nav_evidence",
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
    
    print(f"\n✅ Inserted: {inserted}")
    print(f"📊 Total: {total}")
