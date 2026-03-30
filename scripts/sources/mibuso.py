#!/usr/bin/env python3
"""
Mibuso.com Forum Scraper
=========================
Scrapes mibuso.com - the Microsoft Business Solutions User Group forum.

WHY THIS WORKS:
- Real NAV users ask questions here (not consultants)
- NAV version-specific discussions (NAV 2013, 2015, 2016, 2017, 2018)
- C/AL code discussions (NAV, not BC which uses AL)
- Company names mentioned in posts

This finds END USERS of Navision, not Business Central migrants.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict

MIBUSO_BASE = "https://forum.mibuso.com"

# Forum categories/threads to scrape
FORUM_URLS = [
    "https://forum.mibuso.com/categories/navision",
    "https://forum.mibuso.com/categories/dynamics-nav",
    "https://forum.mibuso.com/categories/nav-2013",
    "https://mibuso.com/forum/categories/nav-2015",
    "https://mibuso.com/forum/categories/nav-2016",
    "https://mibuso.com/forum/categories/nav-2017",
    "https://mibuso.com/forum/categories/nav-2018",
    "https://mibuso.com/forum/categories/c-al",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

def extract_companies_from_thread(url: str) -> List[Dict]:
    """Extract company mentions from a forum thread"""
    companies = []
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find posts
        for post in soup.find_all('div', class_='Message'):
            text = post.get_text(strip=True)[:1000]
            
            # Look for company patterns (capitalized words that look like company names)
            # Skip common forum terms
            skip_words = ['Microsoft', 'Mibuso', 'Navision', 'Dynamics', 'C/AL', 'SQL', 'Azure']
            
            # Extract potential company names
            matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}(?:\s+(?:A/S|ApS|AS|AB|Ltd|Inc|GmbH))?)\b', text)
            
            for match in matches:
                if match in skip_words or len(match) < 4:
                    continue
                
                companies.append({
                    'company_name': match,
                    'evidence': text[:200],
                    'url': url,
                })
        
    except Exception as e:
        pass
    
    return companies

def scrape(country: str = 'DK') -> List[Dict]:
    """Scrape mibuso.com for company mentions"""
    
    print(f"🔍 Mibuso.com Forum Scraper")
    print(f"   Note: Mibuso has ~66K discussions, mostly NAV users")
    
    all_companies = []
    seen = set()
    
    # Scrape main forum categories
    for url in FORUM_URLS[:3]:  # Start with top 3 categories
        print(f"  📍 {url}")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find thread links
            threads = soup.find_all('a', class_='ItemLink')
            
            for thread in threads[:10]:  # Limit threads per category
                thread_url = thread.get('href', '')
                if not thread_url.startswith('http'):
                    thread_url = MIBUSO_BASE + thread_url
                
                # Extract companies from thread
                thread_companies = extract_companies_from_thread(thread_url)
                
                for c in thread_companies:
                    key = c['company_name'].lower()
                    if key not in seen:
                        seen.add(key)
                        all_companies.append({
                            'company_name': c['company_name'],
                            'country': country.upper(),
                            'industry': '',
                            'employees': '',
                            'evidence_type': 'mibuso_forum',
                            'evidence_text': f'Mentioned on mibuso.com NAV forum',
                            'confidence_score': 3,  # Medium - could be consultant or user
                            'source_url': c['url'],
                        })
                
                time.sleep(0.5)  # Be nice
        
        except Exception as e:
            continue
        
        time.sleep(1)
    
    print(f"✅ Mibuso: Found {len(all_companies)} unique company mentions")
    return all_companies

if __name__ == '__main__':
    result = scrape('DK')
    print(f"\nFound {len(result)} companies")
    for c in result[:15]:
        print(f"  - {c['company_name']}")
