#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From Infoclutch - major companies (check if already added)
    {"name": "Walmart", "country": "US", "industry": "Retail", "source": "infoclutch"},
    {"name": "Amazon", "country": "US", "industry": "Technology", "source": "infoclutch"},
    {"name": "CVS Health", "country": "US", "industry": "Healthcare", "source": "infoclutch"},
    {"name": "ExxonMobil", "country": "US", "industry": "Energy", "source": "infoclutch"},
    {"name": "Toyota", "country": "JP", "industry": "Automotive", "source": "infoclutch"},
    {"name": "Shell", "country": "NL", "industry": "Energy", "source": "infoclutch"},
    {"name": "JPMorgan Chase", "country": "US", "industry": "Finance", "source": "infoclutch"},
    {"name": "Microsoft", "country": "US", "industry": "Technology", "source": "infoclutch"},
    {"name": "Foxconn", "country": "TW", "industry": "Manufacturing", "source": "infoclutch"},
    {"name": "Home Depot", "country": "US", "industry": "Retail", "source": "infoclutch"},
    
    # From case studies
    {"name": "Leading Medical Supply Manufacturer", "country": "US", "industry": "Healthcare", "source": "archerpoint_case"},
    
    # From partner searches
    {"name": "Codeless Platforms", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "Simego", "country": "SE", "industry": "Software", "source": "nav_partner"},
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
                5 if "infoclutch" in company["source"] else 4,
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
