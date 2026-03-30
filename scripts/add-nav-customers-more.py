#!/usr/bin/env python3
"""
Add more NAV companies from customer lists
"""

COMPANIES = [
    # From ReadyContacts list
    {"name": "Dovetail Recruitment Ltd", "country": "GB", "industry": "Recruiting", "source": "readycontacts"},
    {"name": "Baker Tilly Virchow Krause", "country": "US", "industry": "Professional Services", "source": "readycontacts"},
    {"name": "Global System", "country": "US", "industry": "IT Services", "source": "readycontacts"},
    {"name": "Spence & Partners Limited", "country": "GB", "industry": "Professional Services", "source": "readycontacts"},
    {"name": "C&F Foods Inc", "country": "US", "industry": "Food Production", "source": "readycontacts"},
    {"name": "Columbus Regional Airport Authority", "country": "US", "industry": "Transportation", "source": "readycontacts"},
    {"name": "DownEast Outfitters", "country": "US", "industry": "Retail", "source": "readycontacts"},
    
    # From Avention Media / Thomson Data
    {"name": "Harvest Health & Recreation", "country": "US", "industry": "Healthcare", "source": "thomsondata"},
    {"name": "Odyssey Systems Consulting Group", "country": "US", "industry": "IT Services", "source": "thomsondata"},
    {"name": "4over", "country": "US", "industry": "Printing", "source": "thomsondata"},
    
    # From Infoclutch
    {"name": "LDC", "country": "US", "industry": "Finance", "source": "infoclutch"},
    
    # From Apps Run The World
    {"name": "Spar International", "country": "NL", "industry": "Retail", "source": "appsruntheworld"},
    {"name": "Puma Energy", "country": "CH", "industry": "Energy", "source": "appsruntheworld"},
    {"name": "EZ Funding Solutions", "country": "US", "industry": "Finance", "source": "appsruntheworld"},
    {"name": "Cokal Drugs", "country": "IN", "industry": "Healthcare", "source": "appsruntheworld"},
    {"name": "PwC Germany", "country": "DE", "industry": "Professional Services", "source": "appsruntheworld"},
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
