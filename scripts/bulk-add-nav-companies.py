#!/usr/bin/env python3
"""
Bulk add NAV companies from search results
Focus: Companies that STILL use NAV (not BC!)
"""

COMPANIES = [
    # From LinkedIn profiles - NAV developers at these companies
    {"name": "The Phoenix Group", "country": "US", "industry": "Financial Services", "source": "linkedin_nav_dev"},
    {"name": "Tuxon Group", "country": "US", "industry": "IT Services", "source": "linkedin_nav_dev"},
    {"name": "Direction Software LLP", "country": "IN", "industry": "IT Services", "source": "microsoft_gold_nav"},
    
    # From job postings - actively hiring NAV developers
    {"name": "Reed", "country": "GB", "industry": "Recruiting", "source": "nav_jobs_uk"},
    {"name": "Jooble", "country": "US", "industry": "Recruiting", "source": "nav_jobs_global"},
    
    # NAV hiring platforms (they have clients!)
    {"name": "HireDynamicsDevelopers", "country": "IN", "industry": "IT Services", "source": "nav_hiring_platform"},
    {"name": "Inoday", "country": "IN", "industry": "IT Services", "source": "nav_hiring_platform"},
    {"name": "Nigel Frank", "country": "GB", "industry": "Recruiting", "source": "nav_hiring_platform"},
    
    # From previous searches
    {"name": "Barclays Bank", "country": "GB", "industry": "Finance", "source": "nav_upgrade_project"},
    {"name": "Dynamic Nation", "country": "GB", "industry": "IT Services", "source": "nav_jobs"},
    {"name": "Dynamics Career", "country": "US", "industry": "Recruiting", "source": "nav_jobs"},
    {"name": "Dynamics Recruiters", "country": "GB", "industry": "Recruiting", "source": "nav_jobs"},
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
                5,  # Highest confidence
                company["source"],
                "nav_user_evidence",
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
