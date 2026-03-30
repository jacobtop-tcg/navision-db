#!/usr/bin/env python3
"""
Add NAV companies from latest searches
"""

COMPANIES = [
    # From customer lists
    {"name": "Walmart", "country": "US", "industry": "Retail", "source": "nav_customer"},
    {"name": "Amazon", "country": "US", "industry": "Technology", "source": "nav_customer"},
    {"name": "CVS Health", "country": "US", "industry": "Healthcare", "source": "nav_customer"},
    {"name": "ExxonMobil", "country": "US", "industry": "Energy", "source": "nav_customer"},
    {"name": "Toyota", "country": "JP", "industry": "Automotive", "source": "nav_customer"},
    {"name": "Shell", "country": "NL", "industry": "Energy", "source": "nav_customer"},
    {"name": "JPMorgan Chase", "country": "US", "industry": "Finance", "source": "nav_customer"},
    {"name": "Microsoft", "country": "US", "industry": "Technology", "source": "nav_customer"},
    {"name": "Foxconn", "country": "TW", "industry": "Manufacturing", "source": "nav_customer"},
    {"name": "Home Depot", "country": "US", "industry": "Retail", "source": "nav_customer"},
    {"name": "LDC", "country": "US", "industry": "Finance", "source": "nav_customer"},
    {"name": "Michelin", "country": "FR", "industry": "Manufacturing", "source": "nav_customer"},
    
    # From case studies
    {"name": "PointClickCare", "country": "CA", "industry": "Healthcare", "source": "nav_customer"},
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
                5,
                company["source"],
                "nav_customer_list",
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
