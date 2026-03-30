#!/usr/bin/env python3
"""
Navision Web Search Scraper - Fallback using OpenClaw web_search
=================================================================
Uses OpenClaw's web_search tool (Brave API) when SearXNG is down.

Usage:
    python3 websearch_scraper.py --country DK
"""

import sqlite3
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
NAVISION_DB = SCRIPT_DIR.parent
DB_PATH = NAVISION_DB / 'database' / 'navision-global.db'

# Search queries for finding Navision companies
QUERIES = {
    'DK': [
        'Navision case study Danmark virksomhed',
        'Dynamics NAV implementation kunde Danmark',
        'Business Central kunde reference',
        'Microsoft Dynamics partner Danmark kunder',
        'Navision ERP virksomhed',
    ],
    'NO': [
        'Navision case study Norge',
        'Dynamics NAV kunde Norge',
        'Business Central referanse',
    ],
    'SE': [
        'Navision case study Sverige',
        'Dynamics NAV kund Sverige',
    ],
    'DE': [
        'Navision Fallstudie Deutschland',
        'Dynamics NAV Kunde',
    ],
    'GLOBAL': [
        'Navision customer case study',
        'Dynamics NAV implementation success',
        'Business Central customer story',
    ],
}

def web_search(query, count=10):
    """Use OpenClaw web_search tool via subprocess."""
    try:
        # Call OpenClaw web_search via Python (simulating the tool)
        import requests
        # Use Brave Search API directly (what web_search uses)
        # For now, return empty - this needs OpenClaw integration
        print(f"  🔍 Web search: {query}")
        return []
    except Exception as e:
        print(f"  ⚠️  Web search failed: {e}")
        return []

def extract_company_from_result(result):
    """Extract company info from search result."""
    title = result.get('title', '')
    url = result.get('url', '')
    content = result.get('content', '')
    
    # Skip job boards and generic sites
    skip = ['linkedin.com/jobs', 'indeed', 'glassdoor', 'jobindex', 
            'wikipedia', 'youtube', 'microsoft.com']
    if any(s in url.lower() for s in skip):
        return None
    
    # Extract company name from title/URL
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        if len(domain) > 3 and len(domain) < 50:
            # Clean up domain
            company = domain.split('.')[0].replace('-', ' ').title()
            if len(company) > 2:
                return {
                    'company_name': company,
                    'website': domain,
                    'evidence_text': title[:100],
                    'source_url': url,
                }
    except:
        pass
    return None

def save_companies(companies, source, country):
    """Save companies to database."""
    if not companies:
        return 0
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    inserted = 0
    for company in companies:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (company_name, country, website, evidence_type, evidence_text, 
             confidence_score, source, source_url, discovered_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('company_name', ''),
                country,
                company.get('website', ''),
                'web_search',
                company.get('evidence_text', ''),
                3,
                source,
                company.get('source_url', ''),
                datetime.utcnow().isoformat() + 'Z',
                datetime.utcnow().isoformat() + 'Z',
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"  ⚠️  Failed to insert: {e}")
    
    conn.commit()
    conn.close()
    return inserted

def scrape(country='GLOBAL'):
    """Scrape companies using web search."""
    print(f"🕸️  Web scraping for {country}")
    
    queries = QUERIES.get(country, QUERIES['GLOBAL'])
    all_companies = []
    seen = set()
    
    for query in queries:
        results = web_search(query, count=10)
        for result in results:
            company = extract_company_from_result(result)
            if company:
                key = f"{company['company_name'].lower()}_{country}"
                if key not in seen:
                    seen.add(key)
                    company['country'] = country
                    all_companies.append(company)
    
    inserted = save_companies(all_companies, 'websearch', country)
    print(f"✅ Found {len(all_companies)} companies, inserted {inserted} new")
    return inserted

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--country', default='DK', help='Country code')
    args = parser.parse_args()
    
    scrape(args.country)
