#!/usr/bin/env python3
"""
Add more NAV companies from industry searches
"""

COMPANIES = [
    # From industry searches
    {"name": "MetaOption", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "IESGP", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Dynamics International", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Active Business Solutions", "country": "DK", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Top10ERP", "country": "US", "industry": "Media", "source": "nav_partner"},
    {"name": "Navision Planet", "country": "US", "industry": "Media", "source": "nav_community"},
    {"name": "WM Dynamics", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "MetadataCorp", "country": "US", "industry": "Software", "source": "nav_partner"},
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
