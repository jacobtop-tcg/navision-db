#!/usr/bin/env python3
"""
Add NAV partners from latest searches
"""

COMPANIES = [
    # From partner searches
    {"name": "Naviona", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Navisiontech", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Active Business Solutions", "country": "DK", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Western Computer", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Innovia Consulting", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "SAGlobal", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "ICEPTS", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "DynamicPoint", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "Codeless Platforms", "country": "US", "industry": "Software", "source": "nav_partner"},
    
    # From customer lists
    {"name": "Infoclutch", "country": "US", "industry": "Data", "source": "nav_database"},
    {"name": "Avention Media", "country": "US", "industry": "Media", "source": "nav_database"},
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
