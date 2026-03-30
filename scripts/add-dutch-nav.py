#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From LinkedIn searches
    {"name": "ProjectWire", "country": "US", "industry": "Recruiting", "source": "linkedin_nav"},
    {"name": "Leafbyte Technology", "country": "US", "industry": "IT Services", "source": "linkedin_nav"},
    
    # From partner searches
    {"name": "Synergy Business Systems", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Plumbline Consulting", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "NAVA Software Solutions", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "HCLTech", "country": "IN", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Mibuso", "country": "EU", "industry": "Community", "source": "nav_community"},
    {"name": "The Dynamics Society", "country": "NL", "industry": "Community", "source": "nav_community"},
    
    # More NAV partners from Dutch companies
    {"name": "Fraxco", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Axpertise", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "AxaptIT", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "YorIT", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "PTC-ICT", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Internamics", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "FreelAX", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "PractICT", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "AxDev", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Rocks BV", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Virtuo BV", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "DynamicBlue", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    {"name": "Hartevelt-IT", "country": "NL", "industry": "IT Services", "source": "nav_partner"},
    
    # More US companies using NAV
    {"name": "Progressus", "country": "US", "industry": "Software", "source": "nav_user"},
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
