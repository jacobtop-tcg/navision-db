#!/usr/bin/env python3
"""
LinkedIn Navision Job Scraper
==============================
Finds companies by scraping job postings that REQUIRE Navision/Dynamics NAV skills.

KEY INSIGHT:
- Companies hiring for "Navision" or "Dynamics NAV" are CURRENT users
- Historical job postings (2-3 years old) = companies that haven't migrated yet
- "C/AL" = DEFINITIVELY Navision (not Business Central which uses AL)

Search Strategy:
- "Navision developer" + [country]
- "Dynamics NAV 2013/2015/2016/2017/2018" + [country]
- "C/AL developer" + [country]
- "Navision consultant" + [country]
- Historical: Add year filters (2022, 2023, 2024)
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from typing import List, Dict

SEARXNG_URL = "http://127.0.0.1:8080"

# NAV-SPECIFIC job search queries (not BC!)
# Using general job sites that SearXNG indexes well
NAV_JOB_QUERIES = {
    'DK': [
        '"Navision" "job" Danmark',
        '"Dynamics NAV" 2016 job',
        '"Dynamics NAV" 2017 job',
        '"Dynamics NAV" 2018 job',
        '"C/AL" udvikler',
        '"Navision" konsulent',
        '"Microsoft NAV" job',
        # Historical (companies still using NAV)
        '"Navision" 2023',
        '"Dynamics NAV" 2023',
    ],
    'DE': [
        'Navision Entwickler site:linkedin.com/jobs',
        'Dynamics NAV 2016 site:linkedin.com/jobs',
        'Dynamics NAV 2017 site:linkedin.com/jobs',
        'C/AL Entwickler site:linkedin.com/jobs',
        'Navision Berater site:linkedin.com/jobs',
    ],
    'SE': [
        'Navision utvecklare site:linkedin.com/jobs',
        'Dynamics NAV 2016 site:linkedin.com/jobs',
        'C/AL utvecklare site:linkedin.com/jobs',
        'Navision konsult site:linkedin.com/jobs',
    ],
    'NO': [
        'Navision utvikler site:linkedin.com/jobs',
        'Dynamics NAV 2016 site:linkedin.com/jobs',
        'C/AL utvikler site:linkedin.com/jobs',
    ],
    'GB': [
        'Navision developer site:linkedin.com/jobs',
        'Dynamics NAV 2016 site:linkedin.com/jobs',
        'C/AL developer site:linkedin.com/jobs',
        'Navision consultant site:linkedin.com/jobs',
    ],
    'US': [
        'Navision developer site:linkedin.com/jobs',
        'Dynamics NAV site:linkedin.com/jobs',
        'C/AL developer site:linkedin.com/jobs',
        'Microsoft NAV site:linkedin.com/jobs',
    ],
    'NL': [
        'Navision ontwikkelaar site:linkedin.com/jobs',
        'Dynamics NAV site:linkedin.com/jobs',
        'C/AL ontwikkelaar site:linkedin.com/jobs',
    ],
    'FI': [
        'Navision kehittäjä site:linkedin.com/jobs',
        'Dynamics NAV site:linkedin.com/jobs',
    ],
    'PL': [
        'Navision developer site:linkedin.com/jobs',
        'Dynamics NAV site:linkedin.com/jobs',
    ],
    'IN': [
        'Navision developer site:linkedin.com/jobs',
        'Dynamics NAV 2016 site:linkedin.com/jobs',
        'C/AL developer site:linkedin.com/jobs',
    ],
}

# Also search for LinkedIn PROFILES (people who work with Navision)
LINKEDIN_PROFILE_QUERIES = {
    'DK': [
        '"Navision" "site:linkedin.com/in" "Copenhagen"',
        '"Dynamics NAV" "site:linkedin.com/in" "Denmark"',
        '"Navision udvikler" "site:linkedin.com/in"',
    ],
    'SE': [
        '"Navision" "site:linkedin.com/in" "Stockholm"',
        '"Dynamics NAV" "site:linkedin.com/in" "Sweden"',
    ],
    'NO': [
        '"Navision" "site:linkedin.com/in" "Oslo"',
        '"Dynamics NAV" "site:linkedin.com/in" "Norway"',
    ],
    'DE': [
        '"Navision" "site:linkedin.com/in" "Germany"',
        '"Dynamics NAV" "site:linkedin.com/in" "Deutschland"',
    ],
}

def extract_company_from_job(text: str, url: str) -> str:
    """Extract company name from job posting text"""
    
    # Common patterns in job postings
    patterns = [
        r'(?:virksomhed|company|organisation)[:\s]+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'(?:hos|at|for)\s+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'(?:til\s+)?(?:kund|client)[:\s]+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})\s+(?:søger|searching|hiring|ansætter)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Try to extract from URL (linkedin.com/jobs/view/XXXX-company-name)
    if 'linkedin.com/jobs' in url:
        parts = url.split('-')
        if len(parts) > 3:
            # Last parts before job ID are usually company name
            company = ' '.join(parts[-3:-1])
            return company.replace('/', '').strip()
    
    return ""

def extract_company_from_profile(text: str) -> str:
    """Extract current company from LinkedIn profile"""
    
    # Look for current position
    patterns = [
        r'(?:Current|Nuværende|Aktuell)[:\s]+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)',
        r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})\s+(?:|Full-time|Del-time)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""

def scrape_jobs(country: str = 'DK') -> List[Dict]:
    """Scrape LinkedIn job postings for Navision skills"""
    
    country_code = country.upper()
    queries = NAV_JOB_QUERIES.get(country_code, NAV_JOB_QUERIES['DK'])
    
    print(f"🔍 LinkedIn Navision Jobs - {country_code}")
    
    companies = []
    seen_companies = set()
    
    for query in queries[:5]:  # Limit queries
        print(f"  📍 Query: {query[:50]}...")
        
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
            
            for result in soup.find_all('article', class_='result', limit=5):
                title_elem = result.find('a', class_='result_header')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                content = result.get_text(strip=True)[:500]
                
                # Extract company
                company = extract_company_from_job(content, url)
                
                if not company or len(company) < 3:
                    continue
                
                # Skip job boards and consultancies
                skip_keywords = ['linkedin', 'indeed', 'glassdoor', 'jobindex', 'consultant', 'recruiter', 'vikar']
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
                    evidence.append('C/AL mentioned')
                
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
                    'evidence_type': 'linkedin_job',
                    'evidence_text': f"Job posting: {', '.join(evidence)}" if evidence else 'LinkedIn Navision job',
                    'confidence_score': confidence,
                    'source_url': url,
                })
                
        except Exception as e:
            continue
        
        time.sleep(1)
    
    print(f"✅ LinkedIn Jobs/{country}: {len(companies)} companies")
    return companies

def scrape_profiles(country: str = 'DK') -> List[Dict]:
    """Scrape LinkedIn profiles for Navision professionals"""
    
    country_code = country.upper()
    queries = LINKEDIN_PROFILE_QUERIES.get(country_code, LINKEDIN_PROFILE_QUERIES['DK'])
    
    print(f"🔍 LinkedIn Navision Profiles - {country_code}")
    
    companies = []
    seen_companies = set()
    
    for query in queries[:3]:
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
            
            for result in soup.find_all('article', class_='result', limit=5):
                content = result.get_text(strip=True)[:500]
                url = result.find('a', class_='result_header')
                url = url.get('href', '') if url else ''
                
                company = extract_company_from_profile(content)
                
                if not company or len(company) < 3:
                    continue
                
                # Skip consultancies (they work with many clients)
                skip_keywords = ['consultant', 'advisor', 'implement', 'partner']
                if any(kw in company.lower() for kw in skip_keywords):
                    continue
                
                company_key = company.lower()
                if company_key in seen_companies:
                    continue
                seen_companies.add(company_key)
                
                companies.append({
                    'company_name': company,
                    'country': country_code,
                    'industry': '',
                    'employees': '',
                    'evidence_type': 'linkedin_profile',
                    'evidence_text': f'LinkedIn profile mentions Navision/Dynamics NAV',
                    'confidence_score': 3,  # Medium - person works there but may be consultant
                    'source_url': url,
                })
                
        except Exception as e:
            continue
        
        time.sleep(1)
    
    print(f"✅ LinkedIn Profiles/{country}: {len(companies)} companies")
    return companies

def scrape(country: str = 'DK') -> List[Dict]:
    """Main scrape function"""
    
    jobs = scrape_jobs(country)
    profiles = scrape_profiles(country)
    
    all_companies = jobs + profiles
    
    # Deduplicate
    seen = set()
    unique = []
    for c in all_companies:
        key = c['company_name'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)
    
    print(f"✅ LinkedIn Navision/{country}: {len(unique)} total unique companies")
    return unique

if __name__ == '__main__':
    result = scrape('DK')
    print(f"\nFound {len(result)} companies")
    for c in result[:10]:
        print(f"  [{c['confidence_score']}] {c['company_name']} - {c['evidence_type']}")
