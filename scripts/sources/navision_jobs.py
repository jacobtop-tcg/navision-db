#!/usr/bin/env python3
"""
Navision Job Scraper - Find Companies via Job Postings
========================================================
Searches for job postings mentioning Navision/Dynamics NAV across ALL job sites.

Strategy:
- Search for "Navision" + "job" + [country]
- Search for "Dynamics NAV" + "required" + [country]
- Search for "C/AL developer" (DEFINITELY Navision)
- Extract company names from job postings

This finds END USERS who are hiring for Navision skills.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict

SEARXNG_URL = "http://127.0.0.1:8080"

# NAV job search queries (all job sites, not just LinkedIn)
NAV_JOB_QUERIES = {
    'DK': [
        '"Navision" job Danmark',
        '"Dynamics NAV" job København',
        '"C/AL" udvikler',
        '"Navision" konsulent',
        '"Dynamics NAV 2016" job',
        '"Dynamics NAV 2017" job',
        '"Dynamics NAV 2018" job',
        '"Navision" stilling',
        '"Microsoft NAV" job',
    ],
    'DE': [
        '"Navision" Stelle Deutschland',
        '"Dynamics NAV" Entwickler',
        '"C/AL" Entwickler',
        '"Navision" Berater',
    ],
    'SE': [
        '"Navision" jobb Sverige',
        '"Dynamics NAV" utvecklare',
        '"C/AL" utvecklare',
        '"Navision" konsult',
    ],
    'NO': [
        '"Navision" stilling Norge',
        '"Dynamics NAV" utvikler',
        '"Navision" konsulent',
    ],
    'GB': [
        '"Navision" job UK',
        '"Dynamics NAV" developer',
        '"C/AL" developer',
        '"Navision" consultant',
    ],
    'US': [
        '"Navision" developer USA',
        '"Dynamics NAV" consultant',
        '"Microsoft NAV" job',
    ],
    'NL': [
        '"Navision" ontwikkelaar',
        '"Dynamics NAV" developer',
    ],
    'FI': [
        '"Navision" kehittäjä',
        '"Dynamics NAV" developer',
    ],
    'PL': [
        '"Navision" developer Polska',
        '"Dynamics NAV" programista',
    ],
    'IN': [
        '"Navision" developer India',
        '"Dynamics NAV" consultant',
    ],
}

def extract_company_from_snippet(text: str) -> str:
    """Extract company name from job snippet"""
    
    # Look for company patterns
    patterns = [
        r'(?:virksomhed|company|organisation)[:\s]*([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'(?:hos|at|for)\s+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})\s+(?:søger|searching|hiring|ansætter)',
        r'(?:til\s+)?(?:kund|client)[:\s]*([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Skip generic terms
            if company.lower() in ['job', 'jobs', 'career', 'stillinger', 'ledige']:
                continue
            return company
    
    return ""

def scrape(country: str = 'DK') -> List[Dict]:
    """Scrape job postings for Navision skills"""
    
    country_code = country.upper()
    queries = NAV_JOB_QUERIES.get(country_code, NAV_JOB_QUERIES['DK'])
    
    print(f"🔍 Navision Jobs - {country_code}")
    
    companies = []
    seen_companies = set()
    
    for query in queries[:6]:  # Limit queries
        try:
            resp = requests.get(
                f"{SEARXNG_URL}/search",
                params={'q': query, 'format': 'html'},
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for result in soup.find_all('article', class_='result', limit=3):
                title_elem = result.find('a', class_='result_header')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                content = result.get_text(strip=True)[:600]
                
                # Skip if it's clearly BC (Business Central)
                if 'Business Central' in content and 'Navision' not in content:
                    continue
                
                # Extract company
                company = extract_company_from_snippet(content)
                
                if not company or len(company) < 3:
                    # Try extracting from title
                    company = title.split('-')[0].strip() if '-' in title else ""
                
                if not company or len(company) < 3:
                    continue
                
                # Skip job boards and consultancies
                skip_keywords = ['jobindex', 'indeed', 'glassdoor', 'linkedin', 'consultant', 'recruiter', 'vikar', 'temporay']
                if any(kw in company.lower() for kw in skip_keywords):
                    continue
                
                company_key = company.lower()
                if company_key in seen_companies:
                    continue
                seen_companies.add(company_key)
                
                # Determine confidence
                confidence = 3
                evidence = []
                
                if 'C/AL' in content:
                    confidence = 5
                    evidence.append('C/AL')
                
                if any(v in content for v in ['NAV 2013', 'NAV 2015', 'NAV 2016', 'NAV 2017', 'NAV 2018']):
                    confidence = max(confidence, 4)
                    evidence.append('NAV version')
                
                if 'Navision' in content:
                    confidence = max(confidence, 4)
                    evidence.append('Navision')
                
                companies.append({
                    'company_name': company,
                    'country': country_code,
                    'industry': '',
                    'employees': '',
                    'evidence_type': 'job_posting',
                    'evidence_text': f"Job: {', '.join(evidence)}" if evidence else 'Navision job posting',
                    'confidence_score': confidence,
                    'source_url': url,
                })
                
        except Exception as e:
            continue
        
        time.sleep(1)
    
    print(f"✅ Navision Jobs/{country}: {len(companies)} companies")
    return companies

if __name__ == '__main__':
    result = scrape('DK')
    print(f"\nFound {len(result)} companies")
    for c in result[:10]:
        print(f"  [{c['confidence_score']}] {c['company_name']} - {c['evidence_text']}")
