#!/usr/bin/env python3
"""
Scraper der finder virksomheder via job postings
- Indeed, LinkedIn, Glassdoor
- Søger på: "Dynamics NAV", "Business Central", "Navision"
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time
import random

# Job sites med Dynamics NAV / Business Central jobs
JOB_SOURCES = [
    {
        "name": "linkedin_jobs",
        "queries": [
            '"Dynamics NAV" developer',
            '"Business Central" consultant',
            '"Microsoft Dynamics" ERP',
            '"Navision" developer',
            '"Dynamics 365" Business Central'
        ],
        "countries": ["DK", "NO", "SE", "DE", "NL", "BE", "UK", "US"]
    },
    {
        "name": "indeed_jobs", 
        "queries": [
            "Dynamics NAV",
            "Business Central Microsoft",
            "Navision developer"
        ],
        "countries": ["DK", "NO", "SE", "DE", "NL", "UK", "US"]
    }
]

def extract_company_from_job(text):
    """Extract company names from job posting text"""
    companies = []
    # Simple extraction - look for company-like patterns
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if any(keyword in line.lower() for keyword in ['dynamics', 'navision', 'business central']):
            # Try to extract company name
            if ' - ' in line:
                company = line.split(' - ')[0].strip()
                if len(company) > 3 and len(company) < 50:
                    companies.append(company)
    return companies

def search_via_searxng(query, country):
    """Search via local SearXNG"""
    try:
        url = "http://127.0.0.1:8080/search"
        params = {
            "q": f"{query} {country} site:linkedin.com/jobs OR site:indeed.com OR site:glassdoor.com",
            "format": "json",
            "language": "en"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('results', [])
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
    return []

def main():
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    total_found = 0
    total_inserted = 0
    
    print("🔍 JOB POSTING SCRAPER - Finding Dynamics NAV companies\n")
    
    for source in JOB_SOURCES:
        print(f"\n📍 Source: {source['name']}")
        
        for query in source['queries'][:3]:  # Limit queries per source
            for country in source['countries'][:5]:  # Limit countries
                print(f"  🔎 {query} in {country}")
                
                results = search_via_searxng(query, country)
                
                for result in results[:5]:  # Top 5 results per query
                    title = result.get('title', '')
                    url = result.get('url', '')
                    content = result.get('content', '')
                    
                    # Extract company name from result
                    companies = extract_company_from_job(title + " " + content)
                    
                    for company in companies[:2]:  # Max 2 per result
                        total_found += 1
                        
                        # Check if already exists
                        cursor.execute("SELECT id FROM companies WHERE company_name = ?", (company,))
                        if not cursor.fetchone():
                            # Insert new company
                            cursor.execute("""
                                INSERT INTO companies 
                                (company_name, country, industry, confidence_score, source, evidence_type, evidence_text, source_url, discovered_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                company,
                                country,
                                "Unknown",  # Would need more scraping to determine
                                3,  # Medium confidence from job posting
                                source['name'],
                                "job_posting",
                                title[:200],
                                url[:500],
                                datetime.utcnow().isoformat()
                            ))
                            total_inserted += 1
                            print(f"    ✅ NEW: {company} ({country})")
                        else:
                            print(f"    ⏭️  Exists: {company}")
                    
                    time.sleep(random.uniform(0.5, 1.5))  # Rate limiting
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Complete!")
    print(f"   Found: {total_found} potential companies")
    print(f"   New inserted: {total_inserted}")

if __name__ == "__main__":
    main()
