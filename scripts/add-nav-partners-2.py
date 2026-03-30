#!/usr/bin/env python3
"""
Add NAV partners from latest searches
"""

COMPANIES = [
    # From partner searches
    {"name": "Artifex Partners", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Encore Business Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Stoneridge Software", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Calsoft Systems", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # From customer lists
    {"name": "Harvest Health & Recreation", "country": "US", "industry": "Healthcare", "source": "nav_customer"},
    {"name": "Avient Corporation", "country": "US", "industry": "Chemicals", "source": "nav_customer"},
    {"name": "Chippenhook Corporation", "country": "US", "industry": "Technology", "source": "nav_customer"},
    {"name": "The Intelligencer and Wheeling News Register", "country": "US", "industry": "Media", "source": "nav_customer"},
    {"name": "Moderno Porcelain Works", "country": "US", "industry": "Manufacturing", "source": "nav_customer"},
    {"name": "EZ Funding Solutions", "country": "US", "industry": "Finance", "source": "nav_customer"},
    {"name": "Cokal Drugs", "country": "IN", "industry": "Healthcare", "source": "nav_customer"},
    {"name": "PwC Germany", "country": "DE", "industry": "Professional Services", "source": "nav_customer"},
    
    # From NAV addons
    {"name": "Dynamics NAV Addons", "country": "US", "industry": "Software", "source": "nav_addon"},
    {"name": "Navision Planet", "country": "US", "industry": "Media", "source": "nav_community"},
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
