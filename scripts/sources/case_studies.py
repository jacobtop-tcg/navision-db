#!/usr/bin/env python3
"""
Navision Case Study Scraper
============================
Uses OpenClaw web_search to find companies from case studies.

This scraper:
1. Searches for Navision case studies
2. Extracts company names from results
3. Saves to database

Run: python3 case_studies.py --country DK
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scraper import log_error

# Search queries that find actual companies (not partners)
CASE_STUDY_QUERIES = [
    'Navision case study customer company',
    'Dynamics NAV implementation success story',
    'Business Central customer reference',
    'Microsoft Dynamics NAV go-live company',
    'Navision ERP customer testimonial',
    'Dynamics 365 Business Central migration customer',
]

COUNTRY_QUERIES = {
    'DK': [
        'Navision kunde case Danmark',
        'Business Central implementation Danmark virksomhed',
        'Dynamics NAV reference Danmark',
    ],
    'NO': [
        'Navision kunde case Norge',
        'Business Central implementering Norge',
    ],
    'SE': [
        'Navision kund case Sverige',
        'Business Central implementation Sverige',
    ],
    'DE': [
        'Navision Kunde Fallstudie Deutschland',
        'Business Central Implementierung Deutschland',
    ],
    'UK': [
        'Navision case study UK customer',
        'Dynamics NAV implementation UK company',
    ],
    'US': [
        'Navision case study USA customer',
        'Dynamics NAV implementation USA company',
    ],
}

def scrape(country='GLOBAL'):
    """Find companies from case studies."""
    print(f"  📍 Searching case studies for {country}")
    
    companies = []
    
    # Get queries for country
    queries = CASE_STUDY_QUERIES.copy()
    if country in COUNTRY_QUERIES:
        queries.extend(COUNTRY_QUERIES[country])
    
    print(f"  🔍 Using {len(queries)} queries")
    
    # For each query, we'd call web_search
    # But since we can't call tools from Python directly,
    # we'll return a list of queries for the main scraper to execute
    
    # This is a placeholder - actual implementation needs tool integration
    print(f"  ℹ️  This scraper requires OpenClaw web_search tool")
    print(f"  ℹ️  Run via main scraper.py which has tool access")
    
    return []

def extract_companies_from_search(search_results):
    """
    Extract company names from web_search results.
    
    Args:
        search_results: List of dicts with 'title', 'content', 'url'
    
    Returns:
        List of company dictionaries
    """
    companies = []
    
    for result in search_results:
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')
        
        # Try to extract company name from title
        # Pattern: "Company X - Case Study" or "Company X implements Navision"
        company = extract_company_name(title, content, url)
        
        if company:
            companies.append({
                'company_name': company,
                'country': 'GLOBAL',
                'website': extract_domain(url),
                'industry': '',
                'employees': '',
                'revenue': '',
                'evidence_type': 'case_study',
                'evidence_text': f"Case study: {title[:80]}",
                'confidence_score': 4,
                'source_url': url,
                'is_verified': 0,
            })
    
    return companies

def extract_company_name(title, content, url):
    """Extract company name from search result."""
    # Common patterns in case study titles
    patterns = [
        ' - ',  # "Company - Case Study"
        ' implements ',  # "Company implements Navision"
        ' chooses ',  # "Company chooses Dynamics"
        ' migrates to ',  # "Company migrates to Business Central"
        ' case study',  # "Company case study"
        ' success story',  # "Company success story"
    ]
    
    title_lower = title.lower()
    
    for pattern in patterns:
        if pattern in title_lower:
            # Extract part before pattern
            company = title_lower.split(pattern)[0].strip()
            if len(company) > 2 and len(company) < 60:
                # Clean up
                company = company.replace('|', '').strip()
                if looks_like_company(company):
                    return company.title()
    
    # Try from URL domain
    domain = extract_domain(url)
    if domain and looks_like_company(domain):
        return domain
    
    return None

def looks_like_company(name):
    """Check if string looks like a company name."""
    if len(name) < 3 or len(name) > 60:
        return False
    
    # Skip generic terms
    generic = [
        'case', 'study', 'success', 'story', 'customer', 'reference',
        'implementation', 'migration', 'dynamics', 'navision', 'microsoft',
        'business central', 'erp', 'solution', 'partner',
    ]
    
    if name.lower() in generic:
        return False
    
    # Skip if mostly numbers
    if sum(c.isdigit() for c in name) > len(name) / 2:
        return False
    
    return True

def extract_domain(url):
    """Extract domain from URL."""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('/')[0]
    except:
        return ''

if __name__ == '__main__':
    print("Case study scraper - requires OpenClaw web_search tool")
    print("Run via: python3 scraper.py --auto")
