#!/usr/bin/env python3
"""
Add NAV partners from Europe, Asia, and reseller searches
"""

COMPANIES = [
    # From Dynamics International partner network - 80+ countries
    {"name": "Dynamics International", "country": "US", "industry": "IT Services", "source": "nav_partner_network"},
    
    # From Europe partners
    {"name": "4PS Construct", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Dynamics Connect", "country": "GB", "industry": "IT Services", "source": "nav_partner"},
    {"name": "SS Dynamics", "country": "NZ", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Naviona", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Trident Info", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # From SAP partners
    {"name": "AlphaBOLD", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "BILL", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "NMB Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Vena Solutions", "country": "CA", "industry": "Software", "source": "nav_partner"},
    {"name": "Dynamic Budgets", "country": "US", "industry": "Software", "source": "nav_partner"},
    {"name": "ERP Mechanics", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Insight Works", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Mekorma", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "insightsoftware", "country": "US", "industry": "Software", "source": "nav_partner"},
    
    # From various partner directories
    {"name": "Elioplus", "country": "SG", "industry": "IT Services", "source": "nav_partner"},
    
    # More major partners from erp_research
    {"name": "Hitachi Solutions", "country": "JP", "industry": "IT Services", "source": "erp_research"},
    {"name": "Tectura", "country": "US", "industry": "IT Services", "source": "erp_research"},
    {"name": "Dynamic Consultants Group", "country": "AE", "industry": "IT Services", "source": "erp_research"},
    {"name": "AXSource", "country": "AU", "industry": "IT Services", "source": "erp_research"},
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
