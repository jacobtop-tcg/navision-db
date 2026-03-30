#!/usr/bin/env python3
"""
Add NAV partners from latest searches
"""

COMPANIES = [
    # From implementation searches
    {"name": "Kepler Management Systems", "country": "RO", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "NEX Softsys", "country": "IN", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "3K Technologies", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "Narola Solutions", "country": "IN", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "Navision Functional Expert", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    
    # From partner searches
    {"name": "Solution Systems", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Artifex Partners", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Apps Run The World", "country": "US", "industry": "Research", "source": "nav_partner"},
    
    # More NAV partners
    {"name": "ERP Consultors", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Campaign Lake", "country": "US", "industry": "Data", "source": "nav_partner"},
    
    # From Apps Run The World - NAV resellers
    {"name": "365 Cannabis", "country": "US", "industry": "Retail", "source": "nav_reseller"},
    {"name": "365 Vertical", "country": "US", "industry": "IT Services", "source": "nav_reseller"},
    {"name": "4PS Construct", "country": "US", "industry": "Construction", "source": "nav_reseller"},
    {"name": "4th Quarter Solutions", "country": "US", "industry": "IT Services", "source": "nav_reseller"},
    {"name": "A.B. Computer Systems", "country": "US", "industry": "IT Services", "source": "nav_reseller"},
    
    # More NAV partners
    {"name": "Solsyst", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Naviona", "country": "US", "industry": "IT Services", "source": "nav_partner"},
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
                5 if "reseller" in company["source"] or "implementation" in company["source"] else 4,
                company["source"],
                "nav_partner_directory",
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
