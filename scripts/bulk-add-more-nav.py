#!/usr/bin/env python3
"""
Bulk add more NAV companies from various sources
"""

COMPANIES = [
    # From msdynamicsworld.com searches
    {"name": "DPFE Corp", "country": "US", "industry": "IT Services", "source": "msdw_partner"},
    {"name": "NAVDNA", "country": "US", "industry": "IT Services", "source": "msdw_partner"},
    {"name": "Business Automation Specialists", "country": "US", "industry": "IT Services", "source": "msdw_partner"},
    {"name": "Qixas Group", "country": "US", "industry": "IT Services", "source": "msdw_partner"},
    {"name": "DynamicsGlobalProjects GmbH", "country": "DE", "industry": "IT Services", "source": "msdw_partner"},
    
    # More from previous searches
    {"name": "Nevas Technologies", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "MetaOption", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Innovia", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "The 365 People", "country": "GB", "industry": "IT Services", "source": "nav_partner"},
    {"name": "NavisionWorld", "country": "US", "industry": "Media", "source": "nav_community"},
    {"name": "Navision Planet", "country": "US", "industry": "Media", "source": "nav_community"},
    {"name": "ERP Software Blog", "country": "US", "industry": "Media", "source": "nav_community"},
    
    # More industries that use NAV
    {"name": "Tri-Mountain", "country": "US", "industry": "Apparel", "source": "nav_case"},
    {"name": "Mountain Gear Corporation", "country": "US", "industry": "Retail", "source": "nav_case"},
    
    # More from job searches
    {"name": "Hire Dynamics Developers", "country": "IN", "industry": "IT Services", "source": "nav_jobs"},
    {"name": "Inoday", "country": "IN", "industry": "IT Services", "source": "nav_jobs"},
    
    # Additional NAV companies
    {"name": "Solochain", "country": "US", "industry": "Software", "source": "nav_integration"},
    {"name": "ChargeLogic", "country": "US", "industry": "Software", "source": "nav_integration"},
    {"name": "PrintVis", "country": "US", "industry": "Software", "source": "nav_integration"},
    
    # More manufacturing/retail companies using NAV
    {"name": "Westfield Group", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Friedman's Home Improvement", "country": "US", "industry": "Retail", "source": "nav_user"},
    {"name": "Harvey Industries", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Dohmen Company", "country": "US", "industry": "Healthcare", "source": "nav_user"},
    {"name": "Lakeland Labs", "country": "US", "industry": "Healthcare", "source": "nav_user"},
    {"name": "Custom Manufacturing & Engineering", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Fulton & Roark", "country": "US", "industry": "Retail", "source": "nav_user"},
    {"name": "American Sportswear", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Pacific Health Laboratories", "country": "US", "industry": "Healthcare", "source": "nav_user"},
    {"name": "Weller Truck Parts", "country": "US", "industry": "Distribution", "source": "nav_user"},
    {"name": "RCS Computer Systems", "country": "US", "industry": "IT Services", "source": "nav_user"},
    {"name": "Kewill", "country": "GB", "industry": "Software", "source": "nav_user"},
    {"name": "Tookan", "country": "IN", "industry": "Software", "source": "nav_user"},
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
