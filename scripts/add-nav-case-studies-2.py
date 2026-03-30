#!/usr/bin/env python3
"""
Add NAV companies from case studies
"""

COMPANIES = [
    # From case studies
    {"name": "Electroimpact", "country": "US", "industry": "Manufacturing", "source": "nav_case_study"},
    {"name": "Omega Industries", "country": "US", "industry": "Manufacturing", "source": "nav_case_study"},
    {"name": "DirectWest", "country": "US", "industry": "Real Estate", "source": "nav_case_study"},
    {"name": "Mountain View", "country": "US", "industry": "Education", "source": "nav_case_study"},
    {"name": "Centra Windows", "country": "US", "industry": "Manufacturing", "source": "nav_case_study"},
    {"name": "North Arm", "country": "US", "industry": "Construction", "source": "nav_case_study"},
    {"name": "Oughtred", "country": "US", "industry": "Professional Services", "source": "nav_case_study"},
    {"name": "Power to Change", "country": "US", "industry": "Nonprofit", "source": "nav_case_study"},
    
    # From success stories
    {"name": "GWA Group", "country": "AU", "industry": "Manufacturing", "source": "nav_success"},
    {"name": "Michael Hill", "country": "NZ", "industry": "Retail", "source": "nav_success"},
    {"name": "TBM", "country": "MY", "industry": "Retail", "source": "nav_success"},
    
    # From customer lists
    {"name": "Investec", "country": "ZA", "industry": "Finance", "source": "nav_customer"},
    {"name": "Franklin Templeton", "country": "US", "industry": "Finance", "source": "nav_customer"},
    {"name": "Lexmark", "country": "US", "industry": "Technology", "source": "nav_customer"},
    {"name": "Andreas Stihl", "country": "DE", "industry": "Manufacturing", "source": "nav_customer"},
    {"name": "Siemens Mobility", "country": "DE", "industry": "Manufacturing", "source": "nav_customer"},
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
                5 if "customer" in company["source"] else 4,
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
