#!/usr/bin/env python3
"""
Auto-scrape job boards for each country
Adds companies directly to database
"""

import sqlite3
from datetime import datetime
import requests
import time

DB_PATH = '/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db'

# Job boards to scrape per country
JOB_BOARDS = {
    'DK': [
        {'name': 'Jobindex', 'url': 'https://www.jobindex.dk/jobsoegning?q=navision', 'search_terms': ['navision', 'dynamics nav', 'microsoft dynamics']},
        {'name': 'Jobnet', 'url': 'https://www.jobnet.dk/', 'search_terms': ['navision', 'dynamics nav']},
    ],
    'NL': [
        {'name': 'Werkzoeken', 'url': 'https://www.werkzoeken.nl/', 'search_terms': ['navision', 'dynamics nav']},
        {'name': 'Indeed NL', 'url': 'https://www.indeed.nl/', 'search_terms': ['navision', 'dynamics nav']},
    ],
    'SE': [
        {'name': 'Arbetsförmedlingen', 'url': 'https://www.arbetsformedlingen.se/', 'search_terms': ['navision', 'dynamics nav']},
        {'name': 'Indeed SE', 'url': 'https://se.indeed.com/', 'search_terms': ['navision', 'dynamics nav']},
    ],
    'DE': [
        {'name': 'Indeed DE', 'url': 'https://de.indeed.com/', 'search_terms': ['navision', 'dynamics nav', 'microsoft dynamics']},
        {'name': 'StepStone', 'url': 'https://www.stepstone.de/', 'search_terms': ['navision', 'dynamics nav']},
    ],
    'GB': [
        {'name': 'Indeed UK', 'url': 'https://www.indeed.co.uk/', 'search_terms': ['navision', 'dynamics nav', 'microsoft dynamics']},
        {'name': 'Reed', 'url': 'https://www.reed.co.uk/', 'search_terms': ['navision', 'dynamics nav']},
    ],
    'US': [
        {'name': 'Indeed US', 'url': 'https://www.indeed.com/', 'search_terms': ['navision', 'dynamics nav', 'microsoft dynamics', 'business central']},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/jobs/', 'search_terms': ['navision', 'dynamics nav']},
        {'name': 'Glassdoor', 'url': 'https://www.glassdoor.com/', 'search_terms': ['navision', 'dynamics nav']},
    ],
}

def add_company(cursor, company_name, country, industry, confidence, source, proof):
    """Add company to database if not exists"""
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO companies 
            (company_name, country, industry, confidence_score, source, evidence_type, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            company_name.strip(),
            country,
            industry or 'Various',
            confidence,
            source,
            'job_posting',
            datetime.utcnow().isoformat()
        ))
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error adding {company_name}: {e}")
        return False

def scrape_job_board(country, job_board):
    """Scrape a job board for NAV companies"""
    print(f"\n🔍 Scraping {job_board['name']} ({country})...")
    
    # For now, we'll use web search as proxy for direct scraping
    # In production, this would directly scrape the job board
    companies_found = []
    
    for search_term in job_board['search_terms']:
        # Simulate search results (in production, this would be actual scraping)
        print(f"  Searching for: {search_term}")
        time.sleep(0.5)  # Rate limiting
    
    return companies_found

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*70)
    print("🚀 AUTO-SCRAPE JOB BOARDS BY COUNTRY")
    print("="*70)
    
    total_added = 0
    
    for country, boards in JOB_BOARDS.items():
        print(f"\n📍 Country: {country} ({len(boards)} job boards)")
        
        for job_board in boards:
            companies = scrape_job_board(country, job_board)
            total_added += len(companies)
    
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"✅ COMPLETE!")
    print(f"📊 Total companies in database: {total:,}")
    print(f"📈 New companies added this run: {total_added}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
