#!/usr/bin/env python3
"""
Add companies from go-live stories and customer lists
"""

COMPANIES = [
    # From go-live stories
    {"name": "Displays2go", "country": "US", "industry": "Manufacturing/Retail", "source": "nav_golive"},
    
    # From Readycontacts customer list
    {"name": "Dovetail Recruitment Ltd", "country": "GB", "industry": "Recruiting", "source": "readycontacts_nav_list"},
    {"name": "Baker Tilly Virchow Krause", "country": "US", "industry": "Professional Services", "source": "readycontacts_nav_list"},
    {"name": "Global System", "country": "US", "industry": "IT Services", "source": "readycontacts_nav_list"},
    {"name": "Spence & Partners Limited", "country": "GB", "industry": "Professional Services", "source": "readycontacts_nav_list"},
    {"name": "C&F Foods Inc", "country": "US", "industry": "Food Production", "source": "readycontacts_nav_list"},
    {"name": "Columbus Regional Airport Authority", "country": "US", "industry": "Transportation", "source": "readycontacts_nav_list"},
    {"name": "DownEast Outfitters", "country": "US", "industry": "Retail", "source": "readycontacts_nav_list"},
    
    # From Nordic partner searches
    {"name": "Qsys Sverige AB", "country": "SE", "industry": "IT Services", "source": "nordic_partner"},
    {"name": "Grant Thornton Sverige", "country": "SE", "industry": "Professional Services", "source": "nordic_partner"},
    {"name": "Mediaplanet Group", "country": "SE", "industry": "Media", "source": "nordic_partner"},
    {"name": "Polaris Industries", "country": "NO", "industry": "Manufacturing", "source": "nordic_partner"},
    {"name": "Schibsted", "country": "NO", "industry": "Media", "source": "nordic_partner"},
    {"name": "Color Line", "country": "NO", "industry": "Transportation", "source": "nordic_partner"},
    {"name": "Kemetyl", "country": "SE", "industry": "Chemicals", "source": "nordic_partner"},
    
    # From various sources
    {"name": "NevaTech", "country": "US", "industry": "IT Services", "source": "nav_content"},
    {"name": "Fidesic", "country": "US", "industry": "IT Services", "source": "nav_content"},
    {"name": "AFON", "country": "SG", "industry": "IT Services", "source": "nav_content"},
    {"name": "Lansweeper", "country": "BE", "industry": "Software", "source": "nav_content"},
    {"name": "O365 Cloud Experts", "country": "AU", "industry": "IT Services", "source": "nav_content"},
    
    # More from partner sites
    {"name": "Tecman", "country": "GB", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Dynamics NAV Addons", "country": "US", "industry": "Software", "source": "nav_partner"},
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
                5 if "golive" in company["source"] or "readycontacts" in company["source"] else 4,
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
