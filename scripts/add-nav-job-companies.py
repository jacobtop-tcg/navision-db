#!/usr/bin/env python3
"""
Add companies with ACTIVE NAV jobs (NOT BC!)
These companies STILL use NAV = migration prospects!
"""

COMPANIES = [
    # From job searches - companies hiring NAV people NOW
    {"name": "John Hardy", "country": "TH", "industry": "Retail/Jewelry", "source": "nav_jobs", "note": "Hiring Senior Navision Developer"},
    {"name": "Chronos Solutions", "country": "US", "industry": "IT Services", "source": "nav_jobs", "note": "Hiring Navision Developer (NAV 2013-2018)"},
    {"name": "B3 Technologies", "country": "IN", "industry": "IT Services", "source": "nav_jobs", "note": "Hiring Senior Dynamics NAV Consultant"},
    {"name": "Cambridge Online Systems", "country": "GB", "industry": "IT Services", "source": "nav_jobs", "note": "Has NAV developers on staff"},
    {"name": "UNIKUL Solutions", "country": "IN", "industry": "IT Services", "source": "nav_jobs", "note": "Hiring Navision/BC consultants"},
    {"name": "MBD Group", "country": "IN", "industry": "Publishing", "source": "nav_jobs", "note": "Hiring Navision consultants"},
    {"name": "Arting Digital", "country": "IN", "industry": "IT Services", "source": "nav_jobs", "note": "Hiring D365 Navision consultants"},
    
    # From previous searches - still valid NAV users
    {"name": "Paulsen Consult LLC", "country": "US", "industry": "IT Services", "source": "nav_consultants", "note": "NAV consultant/owner"},
    
    # Companies with old NAV versions mentioned
    {"name": "Fonds du Logement", "country": "LU", "industry": "Finance", "source": "nav_jobs", "note": "Using NAV 2018, migrating to BC"},
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
                5,  # HIGHEST - actively hiring NAV people = DEFINITELY use NAV!
                company["source"],
                "active_nav_job",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ Added: {company['name']} ({company['country']}) - {company.get('note', '')}")
        except Exception as e:
            print(f"❌ Error adding {company['name']}: {e}")
    
    conn.commit()
    
    # Show total
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n✅ Complete! Inserted {inserted} new companies")
    print(f"📊 Total in database: {total}")
