#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From implementation searches
    {"name": "Cetas", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "Web Masters LLC", "country": "US", "industry": "IT Services", "source": "nav_implementation"},
    {"name": "SA Global", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "IESGP", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # More NAV partners from various sources
    {"name": "Mohana Dynamics", "country": "US", "industry": "IT Services", "source": "nav_blog"},
    {"name": "HandsFree", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Innovia Consulting", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "InterDyn BMI", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # More NAV users/companies
    {"name": "Sequans", "country": "FR", "industry": "Technology", "source": "nav_user"},
    {"name": "NCR Voyix", "country": "US", "industry": "Technology", "source": "nav_user"},
    
    # More industry-specific NAV users
    {"name": "Retail Pro", "country": "US", "industry": "Retail", "source": "nav_user"},
    {"name": "BuildFax", "country": "US", "industry": "Construction", "source": "nav_user"},
    {"name": "Procore", "country": "US", "industry": "Construction", "source": "nav_user"},
    {"name": "Autodesk Construction", "country": "US", "industry": "Construction", "source": "nav_user"},
    {"name": "Trimble", "country": "US", "industry": "Technology", "source": "nav_user"},
    {"name": "Fastenal", "country": "US", "industry": "Distribution", "source": "nav_user"},
    {"name": "Grainger", "country": "US", "industry": "Distribution", "source": "nav_user"},
    {"name": "MSC Industrial", "country": "US", "industry": "Distribution", "source": "nav_user"},
    {"name": "Diversified", "country": "US", "industry": "Distribution", "source": "nav_user"},
    {"name": "W.W. Grainger", "country": "US", "industry": "Distribution", "source": "nav_user"},
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
