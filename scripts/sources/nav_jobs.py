#!/usr/bin/env python3
"""
NAV-SPECIFIC Job Scraper - C/AL Focus
======================================
Finds companies using Dynamics NAV (NOT Business Central) by searching for
job postings that mention C/AL (NAV's language) and NAV versions.

KEY DISTINCTION:
- NAV uses C/AL (Client/Server Application Language)
- Business Central uses AL (Application Language)

This scraper ONLY finds NAV companies by filtering for C/AL mentions.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict

SEARXNG_URL = "http://127.0.0.1:8080"

# NAV-SPECIFIC queries - These indicate actual NAV usage (not BC)
NAV_QUERIES = {
    'DK': [
        'C/AL developer Danmark',
        'Navision developer C/AL',
        'Dynamics NAV 2013 jobs',
        'Dynamics NAV 2015 jobs',
        'Dynamics NAV 2016 jobs',
        'Dynamics NAV 2017 jobs',
        'Dynamics NAV 2018 jobs',
        'Navision konsulent C/AL',
        'Microsoft NAV udvikler',
        'Navision programmør',
    ],
    'DE': [
        'C/AL Entwickler Deutschland',
        'Navision Developer C/AL',
        'Dynamics NAV 2013 Stellen',
        'Dynamics NAV 2015 Stellen',
        'Dynamics NAV 2016 Stellen',
        'Dynamics NAV Entwickler',
        'Navision Berater C/AL',
    ],
    'SE': [
        'C/AL utvecklare Sverige',
        'Navision utvecklare',
        'Dynamics NAV 2013 jobb',
        'Dynamics NAV 2015 jobb',
        'Dynamics NAV utvecklare',
    ],
    'NO': [
        'C/AL utvikler Norge',
        'Navision utvikler',
        'Dynamics NAV 2013 stilling',
        'Dynamics NAV utvikler',
    ],
    'GB': [
        'C/AL developer UK',
        'Navision developer C/AL',
        'Dynamics NAV consultant UK',
        'Microsoft NAV developer',
    ],
    'US': [
        'C/AL developer USA',
        'Navision developer',
        'Dynamics NAV consultant',
        'Microsoft NAV developer remote',
    ],
    'NL': [
        'C/AL ontwikkelaar Nederland',
        'Navision ontwikkelaar',
        'Dynamics NAV developer',
    ],
    'BE': [
        'C/AL developer België',
        'Navision developer',
        'Dynamics NAV consultant België',
    ],
    'FI': [
        'C/AL kehittäjä Suomi',
        'Navision kehittäjä',
        'Dynamics NAV kehittäjä',
    ],
    'PL': [
        'C/AL developer Polska',
        'Navision developer',
        'Dynamics NAV programista',
    ],
    'IN': [
        'C/AL developer India',
        'Navision developer',
        'Dynamics NAV consultant India',
    ],
    'FR': [
        'développeur C/AL France',
        'développeur Navision',
        'consultant Dynamics NAV',
    ],
    'ES': [
        'desarrollador C/AL España',
        'desarrollador Navision',
        'consultor Dynamics NAV',
    ],
    'IT': [
        'sviluppatore C/AL Italia',
        'sviluppatore Navision',
        'consulente Dynamics NAV',
    ],
}

def extract_company_from_job(text: str) -> str:
    """Try to extract company name from job posting"""
    # Common patterns
    patterns = [
        r'virksomhed[:\s]+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'company[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'i\s+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""

def scrape(country: str = 'DK') -> List[Dict]:
    """Scrape for NAV-specific job postings"""
    
    country_code = country.upper()
    queries = NAV_QUERIES.get(country_code, NAV_QUERIES['DK'])
    
    print(f"🔍 NAV-specific job search for {country_code}")
    
    companies = []
    seen_companies = set()
    
    for query in queries[:5]:  # Limit to 5 queries per country
        print(f"  📍 Query: {query}")
        
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
            
            # Extract results
            for result in soup.find_all('article', class_='result', limit=5):
                title_elem = result.find('a', class_='result_header')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                content = result.get_text(strip=True)[:500]
                
                # Extract company (try from title first)
                company = extract_company_from_job(title) or extract_company_from_job(content)
                
                if not company or len(company) < 3:
                    continue
                
                # Skip job boards
                if any(x in url.lower() for x in ['linkedin.com/jobs', 'indeed.com', 'glassdoor.com/job', 'jobindex.dk/job']):
                    # Extract company from job board posting
                    company = title.split('-')[0].strip() if '-' in title else company
                
                company_key = company.lower()
                if company_key in seen_companies:
                    continue
                seen_companies.add(company_key)
                
                # Determine confidence based on evidence
                confidence = 3  # Base confidence
                evidence_parts = []
                
                if 'C/AL' in content or 'C/AL' in title:
                    confidence = 5
                    evidence_parts.append('C/AL mentioned')
                
                if any(v in content for v in ['NAV 2013', 'NAV 2015', 'NAV 2016', 'NAV 2017', 'NAV 2018']):
                    confidence = max(confidence, 4)
                    evidence_parts.append('NAV version mentioned')
                
                if 'Navision' in content or 'Navision' in title:
                    confidence = max(confidence, 4)
                    evidence_parts.append('Navision mentioned')
                
                if confidence < 3:
                    continue  # Skip low-confidence
                
                companies.append({
                    'company_name': company,
                    'country': country_code,
                    'industry': '',
                    'employees': '',
                    'evidence_type': 'job_posting',
                    'evidence_text': f"NAV job: {', '.join(evidence_parts)} - {query}",
                    'confidence_score': confidence,
                    'source_url': url,
                    'website': '',
                })
                
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            continue
        
        time.sleep(1)  # Be nice
    
    print(f"✅ NAV Jobs/{country}: {len(companies)} companies (confidence ≥3)")
    return companies

if __name__ == '__main__':
    import time
    result = scrape('DK')
    print(f"\nFound {len(result)} NAV companies from job postings")
    for c in result[:10]:
        print(f"  [{c['confidence_score']}] {c['company_name']} - {c['evidence_text']}")
