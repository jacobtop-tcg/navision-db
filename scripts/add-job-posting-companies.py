#!/usr/bin/env python3
"""
Add companies from job postings - LinkedIn & Indeed
Companies hiring NAV/BC people ARE customers!
"""

COMPANIES = [
    # From LinkedIn Jobs
    {"name": "Fonds du Logement", "country": "LU", "industry": "Finance", "source": "linkedin_jobs"},
    {"name": "Tecta America Commercial Roofing", "country": "US", "industry": "Construction", "source": "linkedin_jobs"},
    {"name": "Turnkey Technologies", "country": "US", "industry": "IT Services", "source": "linkedin_jobs"},
    {"name": "PlanIT Group", "country": "US", "industry": "IT Services", "source": "linkedin_jobs"},
    {"name": "PopSockets", "country": "US", "industry": "Consumer Products", "source": "linkedin_jobs"},
    {"name": "Southern States Toyotalift", "country": "US", "industry": "Industrial Equipment", "source": "linkedin_jobs"},
    {"name": "Conspicuous", "country": "GB", "industry": "IT Services", "source": "linkedin_jobs"},
    {"name": "R2 Global", "country": "US", "industry": "Recruiting", "source": "linkedin_jobs"},
    {"name": "EnQuest Energy Solutions", "country": "US", "industry": "Energy", "source": "linkedin_jobs"},
    {"name": "Sikich", "country": "US", "industry": "Professional Services", "source": "linkedin_jobs"},
    {"name": "DYWIDAG", "country": "DE", "industry": "Construction", "source": "linkedin_jobs"},
    
    # From Nigel Frank jobs
    {"name": "Nigel Frank International", "country": "GB", "industry": "Recruiting", "source": "nigelfrank_jobs"},
    
    # More from Indeed search results
    {"name": "Tecta America", "country": "US", "industry": "Construction", "source": "indeed_jobs"},
    {"name": "Western Computer", "country": "US", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "Clients First Business Solutions", "country": "US", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "ArcherPoint", "country": "US", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "Innovia Consulting", "country": "US", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "Encore Business Solutions", "country": "US", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "The NAV People", "country": "GB", "industry": "IT Services", "source": "indeed_jobs"},
    {"name": "Sabre Limited", "country": "GB", "industry": "IT Services", "source": "indeed_jobs"},
    
    # From job descriptions - companies mentioned
    {"name": "Tesla Grohmann Automation", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Kawasaki Robotics", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Crown Equipment Corporation", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Barton Malow Company", "country": "US", "industry": "Construction", "source": "job_desc"},
    {"name": "Portacool", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Caleres", "country": "US", "industry": "Retail", "source": "job_desc"},
    {"name": "Morrison Container Handling Solutions", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Sunrise Technologies", "country": "US", "industry": "IT Services", "source": "job_desc"},
    {"name": "Dixon Valve & Coupling Company", "country": "US", "industry": "Manufacturing", "source": "job_desc"},
    {"name": "Targus", "country": "US", "industry": "Technology", "source": "job_desc"},
    {"name": "Coca-Cola Bottlers", "country": "US", "industry": "Beverages", "source": "job_desc"},
    {"name": "Revlon", "country": "US", "industry": "Consumer Products", "source": "job_desc"},
    {"name": "Pandora Jewelry", "country": "DK", "industry": "Retail", "source": "job_desc"},
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
                4,  # High confidence - hiring NAV/BC people
                company["source"],
                "job_posting",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ Added: {company['name']} ({company['country']})")
        except Exception as e:
            print(f"❌ Error adding {company['name']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Complete! Inserted {inserted} new companies")
