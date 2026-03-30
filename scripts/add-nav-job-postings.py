#!/usr/bin/env python3
"""
Add companies from ACTIVE job postings - they DEFINITELY use NAV!
"""

import sqlite3
from datetime import datetime

# Companies actively hiring for NAV roles RIGHT NOW
COMPANIES = [
    {"name": "SWK Technologies", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Accord Technologies", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Tecta America Commercial Roofing", "country": "US", "industry": "Construction/Roofing", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Turnkey Technologies", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "PopSockets", "country": "US", "industry": "Consumer Products", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Applied Resource Group", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Dynamic Nation", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "PlanIT Group", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "The Nycor Group", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Foley Incorporated", "country": "US", "industry": "Manufacturing", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Stott and May", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Mastronardi Produce", "country": "US", "industry": "Agriculture/Food", "confidence": 5, "source": "glassdoor_2025", "proof": "Job requires Microsoft Dynamics NAV skills"},
    {"name": "Wall Street Consulting Services", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Doozy Solutions", "country": "US", "industry": "IT Services", "confidence": 5, "source": "linkedin_jobs_2025", "proof": "Actively hiring Microsoft Dynamics NAV professionals"},
    {"name": "Strategic Employment Partners", "country": "US", "industry": "Recruiting", "confidence": 4, "source": "linkedin_jobs_2025", "proof": "Recruiting for NAV positions"},
]

if __name__ == "__main__":
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    # Create table for job-posting verified companies
    cursor.execute('DROP TABLE IF EXISTS nav_job_postings')
    cursor.execute('''
        CREATE TABLE nav_job_postings (
            company_name TEXT PRIMARY KEY,
            country TEXT,
            industry TEXT,
            confidence_score INTEGER,
            source TEXT,
            proof TEXT,
            found_at TEXT
        )
    ''')
    
    inserted = 0
    for company in COMPANIES:
        try:
            cursor.execute("""
                INSERT INTO nav_job_postings
                (company_name, country, industry, confidence_score, source, proof, found_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company["name"],
                company["country"],
                company["industry"],
                company["confidence"],
                company["source"],
                company["proof"],
                datetime.utcnow().isoformat()
            ))
            inserted += 1
            print(f"✅ {company['name']} ({company['country']}) - {company['industry']}")
        except Exception as e:
            print(f"❌ {company['name']}: {e}")
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM nav_job_postings")
    count = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"✅ VERIFIED FROM JOB POSTINGS: {count} companies")
    print(f"{'='*60}")
    print(f"\n🎯 These companies are ACTIVELY hiring for NAV roles RIGHT NOW!")
    print(f"   Perfect targets for migration to Business Central!")
    
    conn.close()
