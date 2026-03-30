#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From manufacturing searches
    {"name": "Dynamics International", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "MetaOption", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Naviona", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Sabre Limited", "country": "GB", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Lean MFG Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # From partner searches
    {"name": "Apps Run The World", "country": "US", "industry": "Research", "source": "nav_partner"},
    {"name": "MSDynamicsWorld", "country": "US", "industry": "Media", "source": "nav_partner"},
    {"name": "Artifex Partners", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Top Dynamics Partners", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "ERP Software Blog", "country": "US", "industry": "Media", "source": "nav_partner"},
    
    # From customer lists
    {"name": "Laboratoires Servier", "country": "FR", "industry": "Healthcare", "source": "nav_customer"},
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
                5 if "customer" in company["source"] else 4,
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
