#!/usr/bin/env python3
"""
Add more NAV companies from job boards and partner lists
"""

COMPANIES = [
    # From job boards
    {"name": "R2 Global", "country": "US", "industry": "Recruiting", "source": "linkedin_jobs"},
    {"name": "Navision India", "country": "IN", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Nigel Frank", "country": "GB", "industry": "Recruiting", "source": "nav_jobs"},
    {"name": "Skyline Consultants", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "GraVoc", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # From Apps Run The World partner list
    {"name": "365 Cannabis", "country": "US", "industry": "Retail", "source": "appsruntheworld"},
    {"name": "365 Vertical", "country": "US", "industry": "IT Services", "source": "appsruntheworld"},
    {"name": "4PS Construct", "country": "NL", "industry": "Construction", "source": "appsruntheworld"},
    {"name": "4th Quarter Solutions", "country": "US", "industry": "IT Services", "source": "appsruntheworld"},
    {"name": "A. B. Computer Systems", "country": "US", "industry": "IT Services", "source": "appsruntheworld"},
    
    # From partner searches
    {"name": "Calsoft", "country": "US", "industry": "IT Services", "source": "nav_partner"},
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
