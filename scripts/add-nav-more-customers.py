#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From LinkedIn search results
    {"name": "Targus", "country": "US", "industry": "Technology", "source": "linkedin_nav"},
    {"name": "Coca-Cola Bottlers", "country": "US", "industry": "Beverages", "source": "linkedin_nav"},
    {"name": "Revlon", "country": "US", "industry": "Consumer Products", "source": "linkedin_nav"},
    {"name": "Pandora Jewelry", "country": "DK", "industry": "Retail", "source": "linkedin_nav"},
    
    # From Navision Planet
    {"name": "Hevo Data", "country": "US", "industry": "Data", "source": "nav_partner"},
    {"name": "ThoughtSpot", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "Hornblower", "country": "US", "industry": "Transportation", "source": "nav_partner"},
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
