#!/usr/bin/env python3
"""
LinkedIn People Mapper - Global Navision Professionals
=======================================================
100% FREE - Uses local SearXNG instance

Strategy:
1. Search for Navision professionals via SearXNG
2. Extract company names from profiles
3. Map person → company → country
4. Save to consolidated database
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from pathlib import Path

# SearXNG instance
SEARXNG_URL = "http://127.0.0.1:8080"

# LinkedIn profile search queries by country
LINKEDIN_QUERIES = {
    'DK': [
        'site:linkedin.com/in Navision Danmark',
        'site:linkedin.com/in "Dynamics NAV" København',
        'site:linkedin.com/in "Business Central" Danmark',
        'site:linkedin.com/in "Navision udvikler"',
        'site:linkedin.com/in "Microsoft Dynamics" ERP',
    ],
    'NO': [
        'site:linkedin.com/in Navision Norge',
        'site:linkedin.com/in "Dynamics NAV" konsulent',
        'site:linkedin.com/in "Business Central" utvikler',
    ],
    'SE': [
        'site:linkedin.com/in Navision Sverige',
        'site:linkedin.com/in "Dynamics NAV" utvecklare',
        'site:linkedin.com/in "Business Central" konsult',
    ],
    'DE': [
        'site:linkedin.com/in Navision Deutschland',
        'site:linkedin.com/in "Dynamics NAV" Berater',
        'site:linkedin.com/in "Business Central" Entwickler',
    ],
    'UK': [
        'site:linkedin.com/in Navision UK',
        'site:linkedin.com/in "Dynamics NAV" consultant',
        'site:linkedin.com/in "Business Central" developer',
    ],
    'US': [
        'site:linkedin.com/in Navision USA',
        'site:linkedin.com/in "Dynamics NAV" developer',
        'site:linkedin.com/in "Business Central" consultant',
    ],
    'GLOBAL': [
        'site:linkedin.com/in "Navision"',
        'site:linkedin.com/in "Dynamics NAV"',
        'site:linkedin.com/in "Business Central"',
        'site:linkedin.com/in "Microsoft Dynamics NAV"',
    ],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def scrape(country='GLOBAL'):
    """Find Navision professionals via LinkedIn profiles."""
    print(f"  📍 LinkedIn people search for {country}")
    
    companies = scrape_searxng_linkedin(country)
    
    if companies:
        print(f"  ✅ Found {len(companies)} companies via LinkedIn professionals")
        return companies
    
    print(f"  ⚠️  No LinkedIn data available for {country}")
    return []

def scrape_searxng_linkedin(country='GLOBAL'):
    """
    Search SearXNG for LinkedIn profiles with Navision skills.
    
    Returns list of company dictionaries.
    """
    companies = []
    seen_companies = set()
    
    queries = LINKEDIN_QUERIES.get(country, LINKEDIN_QUERIES['GLOBAL'])
    print(f"  🔍 Using {len(queries)} LinkedIn queries via SearXNG")
    
    for query in queries:
        try:
            # Search via SearXNG
            url = f"{SEARXNG_URL}/search"
            params = {
                'q': query,
                'pageno': 1,
                'format': 'html',
            }
            
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            
            if resp.status_code != 200:
                print(f"    ⚠️  SearXNG HTTP {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract results
            results = soup.find_all('article', class_='result')
            if not results:
                results = soup.find_all('div', class_='result')
            
            for result in results[:20]:  # Max 20 per query
                try:
                    title_elem = result.find('a', class_='result_title')
                    if not title_elem:
                        title_elem = result.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # Only process LinkedIn profile URLs
                    if 'linkedin.com/in/' not in url.lower():
                        continue
                    
                    # Extract company from profile snippet
                    snippet_elem = result.find('p', class_='content')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    company = extract_company_from_profile(title, snippet, url)
                    
                    if company and company.lower() not in seen_companies:
                        # STRICT FILTERING - Same as global_jobs.py
                        if not looks_like_company(company):
                            continue
                        
                        seen_companies.add(company.lower())
                        companies.append({
                            'company_name': company,
                            'country': country if country != 'GLOBAL' else 'DK',
                            'website': '',
                            'industry': '',
                            'employees': '',
                            'revenue': '',
                            'evidence_type': 'linkedin_professional',
                            'evidence_text': f"Profile: {title[:60]}",
                            'confidence_score': 4,
                            'source_url': url,
                            'is_verified': 0,
                        })
                except Exception as e:
                    continue
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"    ⚠️  Query error: {e}")
            continue
    
    return companies

def extract_company_from_profile(title, snippet, url):
    """Extract company name from LinkedIn profile."""
    # Try snippet first - usually contains "at Company" or "Company · Location"
    if ' at ' in snippet.lower():
        parts = snippet.lower().split(' at ')
        if len(parts) > 1:
            company = parts[1].split(' · ')[0].split(' | ')[0].strip()
            if len(company) > 2 and len(company) < 50:
                return company.title()
    
    # Try "· Company ·" pattern
    if '·' in snippet:
        parts = snippet.split('·')
        for part in parts:
            part = part.strip()
            # Skip common non-company terms
            if part.lower() in ['linkedin', 'see profile', 'view profile', 'connections']:
                continue
            if len(part) > 3 and len(part) < 50:
                return part.title()
    
    # Try from URL (sometimes contains company)
    # Pattern: linkedin.com/in/name-at-company
    if '-at-' in url.lower() or '-in-' in url.lower():
        parts = url.split('/')
        for part in parts:
            if 'at' in part.lower():
                company = part.split('-at-')[-1] if '-at-' in part else part.split('-in-')[-1]
                if company and len(company) > 2:
                    return company.replace('-', ' ').title()
    
    return None


# ============== QUALITY FILTERS (same as global_jobs.py) ==============

NOISE_PATTERNS = [
    r'^best\s*\d*', r'^top\s*\d*', r'^\d+\s*best', r'near\s*me', r'directory',
    r'currency', r'converter', r'exchange\s*rate', r'valuta', r'usd\s*to', r'eur\s*to',
    r'calculator', r'omregner', r'rechner', r'speed\s*test',
    r'^how\s+(to|long|much)', r'^what\s+is', r'^guide\s+to', r'tutorial', r'faq',
    r'vs\b', r'versus', r'comparison', r'review\b', r'horoscope', r'zodiac',
    r'^r/', r'reddit', r'forum', r'thread', r'discussion', r'comments',
    r'^maps\s', r'google\s+maps', r'yahoo\s+search', r'login\b', r'sign\s+in',
    r'qr\s+code', r'password', r'email\s+recovery',
    r'xxx', r'porn', r'casino', r'betting',
    r'time\s+in', r'timezone', r'clock\s+', r'live\s*$',
    r'clothing\s+online', r'boutique\s+', r'damen\s+', r'herren\s+',
]

def looks_like_company(name):
    """Check if string looks like a real company name (not noise)."""
    if len(name) < 3 or len(name) > 80:
        return False
    
    name_lower = name.lower()
    name_stripped = name_lower.replace(' ', '').replace('.', '').replace('-', '')
    
    # Skip if mostly numbers
    if sum(c.isdigit() for c in name) > len(name) / 2:
        return False
    
    # Skip generic single words
    generic_single = ['job', 'jobs', 'career', 'careers', 'hiring', 'work', 'employment',
               'navision', 'dynamics', 'microsoft', 'erp', 'business', 'central']
    if name_lower in generic_single or name_stripped in generic_single:
        return False
    
    # Skip "X Com" patterns (generic domain references)
    if name_stripped.endswith('com') and ' ' not in name_lower:
        if len(name_stripped) < 20:
            return False
    
    # Skip "X Org" patterns
    if name_stripped.endswith('org'):
        if ' ' not in name_lower or len(name_stripped) < 20:
            return False
        if any(x in name_lower for x in ['secrets', 'best', 'top', 'guide']):
            return False
    
    # Check for NOISE patterns
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return False
    
    # Skip if starts with numbers
    if name[0].isdigit():
        return False
    
    # Skip obvious non-companies
    if any(x in name_lower for x in ['salon', 'nail', 'spa', 'tattoo', 'restaurant', 'cafe']):
        if not any(x in name_lower for x in ['group', 'inc', 'ltd', 'corporation', 'international']):
            return False
    
    # Skip generic web references
    if any(x in name_lower for x in ['docs ', 'documentation', 'forum', 'blog', 'wiki']):
        return False
    
    return True


if __name__ == '__main__':
    print("Testing linkedin_global scraper for DK...")
    result = scrape('DK')
    print(f"\nFound {len(result)} companies via LinkedIn")
    for company in result[:10]:
        print(f"  - {company['company_name']}: {company['evidence_text'][:50]}")
