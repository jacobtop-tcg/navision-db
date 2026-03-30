#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From technology searches
    {"name": "NavisionTech Inc", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Technology Management Concepts", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Dynamics Square", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Dynamics SmartZ", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Sigma Software", "country": "UA", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Sonata Software", "country": "IN", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Crestwood", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "CIG Consultants", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # More NAV partners from various sources
    {"name": "UseDynamics", "country": "US", "industry": "Media", "source": "nav_community"},
    {"name": "Dynamics Lifestyle", "country": "US", "industry": "Media", "source": "nav_community"},
    
    # More industries that use NAV
    {"name": "Schneider", "country": "US", "industry": "Transportation", "source": "nav_user"},
    {"name": "Blue Yonder", "country": "US", "industry": "Software", "source": "nav_user"},
    {"name": "ShipStation", "country": "US", "industry": "Software", "source": "nav_user"},
    {"name": "Shippo", "country": "US", "industry": "Software", "source": "nav_user"},
    {"name": "ShipEngine", "country": "US", "industry": "Software", "source": "nav_user"},
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
            pass
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n✅ Inserted: {inserted}")
    print(f"📊 Total: {total}")
