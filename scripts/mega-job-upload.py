#!/usr/bin/env python3
"""
MEGA UPLOAD - Add ALL companies from job postings across all platforms
"""

import sqlite3
from datetime import datetime

# ALL companies from Indeed, Glassdoor, ZipRecruiter, LinkedIn
COMPANIES = [
    # From Glassdoor - actively hiring NAV/BC people
    {"name": "Elite Search Professionals", "country": "US", "industry": "Recruiting", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Sr. Dynamics NAV/BC Developer"},
    {"name": "OmniVue Business Solutions", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring NAV/BC consultants"},
    {"name": "Vaco by Highspring", "country": "US", "industry": "Recruiting", "confidence": 4, "source": "glassdoor_jobs_2025", "proof": "Recruiting for NAV positions"},
    {"name": "Nature Fresh Farms", "country": "US", "industry": "Agriculture", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Stone Coast Fund Services", "country": "US", "industry": "Finance", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Mosaic Personnel", "country": "US", "industry": "Recruiting", "confidence": 4, "source": "glassdoor_jobs_2025", "proof": "Recruiting for NAV positions"},
    {"name": "Pasona NA", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring ERP Consultant with NAV experience"},
    {"name": "Krauth Electric", "country": "US", "industry": "Construction/Electrical", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "T&D Metal Products", "country": "US", "industry": "Manufacturing", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Trova Advisory Group", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "RSM", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Dynamics NAV consultant"},
    {"name": "Revvity", "country": "US", "industry": "Technology", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Velosio", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring NAV/BC consultant"},
    {"name": "Auto Air Export", "country": "US", "industry": "Logistics", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Xtivia", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "EarthSoft", "country": "US", "industry": "Software", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Camelot 3PL Software", "country": "US", "industry": "Software/Logistics", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Western Computer", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring NAV/BC consultant"},
    {"name": "Swedish Trade Council", "country": "US", "industry": "Government", "confidence": 4, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "MediaMath", "country": "US", "industry": "Technology", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Business Central Functional Consultant"},
    {"name": "Chronos Solutions", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Navision Developer"},
    {"name": "Aura Innovative Technology", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Data Masons Software", "country": "US", "industry": "Software", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "Victor Stanley", "country": "US", "industry": "Manufacturing", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring ERP Analyst with NAV"},
    {"name": "LS Retail", "country": "IS", "industry": "Software", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring LS Central/BC consultant"},
    {"name": "Kreischer Miller", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "New Charter Technologies", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Senior Software Engineer D365 BC"},
    {"name": "Sikich", "country": "US", "industry": "Professional Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring Dynamics NAV consultant"},
    {"name": "Clients First Business Solutions", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring D365 BC/NAV consultant"},
    {"name": "Terran Industries", "country": "US", "industry": "Manufacturing", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring D365 Architect & IT Manager"},
    {"name": "Adroit North America", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    {"name": "ZOOK", "country": "US", "industry": "IT Services", "confidence": 5, "source": "glassdoor_jobs_2025", "proof": "Hiring for NAV roles"},
    
    # From Indeed
    {"name": "Steel Dynamics", "country": "US", "industry": "Manufacturing/Steel", "confidence": 5, "source": "indeed_jobs_2025", "proof": "Fortune 500 - Hiring Dynamics Navision Accounting"},
    
    # From ZipRecruiter / SimplyHired
    {"name": "Sagebrook Home", "country": "US", "industry": "Retail/Home Goods", "confidence": 5, "source": "ziprecruiter_2025", "proof": "Hiring Dynamics Navision Developer/Analyst"},
    {"name": "TravelOperations", "country": "EU", "industry": "Travel", "confidence": 5, "source": "ziprecruiter_2025", "proof": "Hiring BC/Navision Finance Consultant"},
    
    # From SimplyHired
    {"name": "Napa Valley Wine Manufacturer", "country": "US", "industry": "Beverages/Wine", "confidence": 5, "source": "simplyhired_2025", "proof": "Hiring Sr. NAV/BC Developer - 800K cases/year"},
]

if __name__ == "__main__":
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    # Create comprehensive job postings table
    cursor.execute('DROP TABLE IF EXISTS nav_all_job_postings')
    cursor.execute('''
        CREATE TABLE nav_all_job_postings (
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
                INSERT INTO nav_all_job_postings
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
        except Exception as e:
            pass
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM nav_all_job_postings")
    count = cursor.fetchone()[0]
    
    # Also count previous tables
    cursor.execute("SELECT COUNT(*) FROM nav_job_postings")
    prev_count = cursor.fetchone()[0]
    
    print(f"{'='*70}")
    print(f"🎯 MEGA UPLOAD COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ New companies added: {inserted}")
    print(f"✅ Previous job postings: {prev_count}")
    print(f"✅ Total in nav_all_job_postings: {count}")
    print(f"\n🔥 These companies are ACTIVELY hiring for NAV/BC roles RIGHT NOW!")
    print(f"   Perfect targets for migration to Business Central!")
    
    conn.close()
