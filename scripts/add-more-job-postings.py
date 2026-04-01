#!/usr/bin/env python3
"""
Tilføj FLERE JOB POSTINGS - Smoking Guns
Finder virksomheder der søger NAV-brugere (ikke konsulenter!)
"""

import sqlite3
import requests
from datetime import datetime
from pathlib import Path
import time

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
SEARXNG_URL = "http://127.0.0.1:8080"

# Job queries per land - KUN interne stillinger!
JOB_QUERIES = {
    'DK': [
        '"økonomimedarbejder" "Dynamics NAV"',
        '"regnskabsansvarlig" "Navision"',
        '"CFO" "Dynamics NAV"',
        '"bogholder" "Navision"',
        '"indkøber" "Dynamics NAV"',
        '"lageransvarlig" "Navision"',
        '"finansiel" "Dynamics NAV"',
        '"øonomichef" "Navision"',
    ],
    'DE': [
        '"Buchhalter" "Dynamics NAV"',
        '"Finanzleiter" "Navision"',
        '"Einkäufer" "Dynamics NAV"',
        '"Lagerleiter" "Navision"',
    ],
    'SE': [
        '"ekonomi" "Dynamics NAV"',
        '"redovisning" "Navision"',
        '"inköp" "Dynamics NAV"',
        '"lageransvarig" "Navision"',
    ],
    'NO': [
        '"regnskap" "Dynamics NAV"',
        '"økonomisjef" "Navision"',
        '"innkjøp" "Dynamics NAV"',
    ],
    'UK': [
        '"accountant" "Dynamics NAV"',
        '"finance manager" "Navision"',
        '"purchasing" "Dynamics NAV"',
        '"warehouse manager" "Navision"',
    ],
    'US': [
        '"accountant" "Dynamics NAV"',
        '"finance manager" "Navision"',
        '"purchasing manager" "Dynamics NAV"',
    ],
    'NL': [
        '"boekhouder" "Dynamics NAV"',
        '"finance manager" "Navision"',
    ],
    'FR': [
        '"comptable" "Dynamics NAV"',
        '"directeur financier" "Navision"',
    ],
}

# Filtrer konsulenter/vikarbureauer FRA
EXCLUDE_TERMS = [
    'konsulent', 'consultant', 'vikar', 'temp',
    'for vores kunde', 'for our client',
    'implementering', 'implementation',
    'partner', 'rådgivning', 'advisory',
]

def search_searxng(query):
    """Search via SearXNG"""
    try:
        url = f"{SEARXNG_URL}/search"
        params = {
            "q": query,
            "format": "json",
            "language": "en",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('results', [])
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
    return []

def extract_company(title, content, url):
    """Extract company name from job posting"""
    # Simple extraction - take first part before common separators
    text = title + " " + content
    
    # Try to extract from URL
    if 'linkedin.com' in url:
        # LinkedIn company pages
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'company' and i+1 < len(parts):
                return parts[i+1].replace('-', ' ').title()
    
    # Try common patterns
    for sep in [' - ', ' | ', ' @ ']:
        if sep in text:
            company = text.split(sep)[0].strip()
            if len(company) > 3 and len(company) < 100:
                return company
    
    return None

def add_job_posting(cur, company, country, title, url, content):
    """Add job posting to database if not exists"""
    
    # Check exists
    cur.execute('SELECT id FROM companies WHERE company_name = ? AND country = ?', 
              (company[:200], country))
    if cur.fetchone():
        return False
    
    # Insert
    cur.execute('''
        INSERT INTO companies 
        (company_name, country, evidence_type, evidence_text, confidence_score, 
         source, source_url, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        company[:200],
        country,
        'job_posting_smoking_gun',
        f'Hiring: {title[:300]} - {content[:200]}',
        5,  # Highest confidence - smoking gun!
        'job_posting_scrape',
        url[:500],
        datetime.utcnow().isoformat() + 'Z'
    ))
    return True

def scrape_jobs():
    """Scrape job postings for all countries"""
    
    print("=" * 80)
    print("🔍 SCRAPING JOB POSTINGS - SMOKING GUNS")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    total_added = 0
    
    for country, queries in JOB_QUERIES.items():
        print(f"\n📍 {country}")
        country_added = 0
        
        for query in queries:
            results = search_searxng(query)
            
            for result in results[:10]:  # Top 10 per query
                title = result.get('title', '')
                url = result.get('url', '')
                content = result.get('content', '')
                
                # Skip if exclude terms
                text_lower = (title + " " + content).lower()
                if any(term in text_lower for term in EXCLUDE_TERMS):
                    continue
                
                # Extract company
                company = extract_company(title, content, url)
                if not company or len(company) < 3:
                    continue
                
                # Add to database
                if add_job_posting(cur, company, country, title, url, content):
                    country_added += 1
                    total_added += 1
                    print(f"  ✅ {company} - {title[:50]}...")
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"  📊 {country}: +{country_added}")
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ TOTAL TILFØJET: {total_added} job postings (smoking guns!)")
    print("=" * 80)
    
    return total_added

if __name__ == '__main__':
    try:
        scrape_jobs()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
