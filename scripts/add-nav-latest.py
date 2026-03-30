#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From LinkedIn searches
    {"name": "Sana Commerce", "country": "US", "industry": "Software", "source": "linkedin_nav"},
    {"name": "Open Door Technology", "country": "CA", "industry": "IT Services", "source": "linkedin_nav"},
    
    # From implementation searches
    {"name": "Dynamics Fanatics", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "Volt Technologies", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "CherrieBS", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "Wiise", "country": "US", "industry": "Software", "source": "nav_implementation"},
    
    # From various sources
    {"name": "EOne Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "The Data Crew", "country": "US", "industry": "Data", "source": "nav_community"},
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
