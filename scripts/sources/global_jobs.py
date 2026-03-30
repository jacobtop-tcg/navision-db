#!/usr/bin/env python3
"""
Global Navision Company Finder - Via Multiple Strategies
=========================================================
100% FREE - Uses local SearXNG instance

Strategies:
1. Case studies - companies that implemented Navision
2. Customer references from partners
3. Press releases about Navision implementations
4. Job postings (extract company hiring)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from urllib.parse import urlparse

SEARXNG_URL = "http://127.0.0.1:8080"

# Search queries designed to find ACTUAL companies (not job boards)
# EXPANDED QUERIES - Added variations, partner mentions, certifications, events
COMPANY_QUERIES = {
    'DK': [
        # Case studies & references
        'Navision case study Danmark virksomhed',
        'Dynamics NAV implementation kunde Danmark',
        'Business Central kunde reference Danmark',
        'Microsoft Dynamics NAV kunde case',
        'Navision ERP virksomhed Danmark',
        '"bruger Navision" Danmark',
        '"anvender Navision" virksomhed',
        'Dynamics 365 Business Central kunde Danmark',
        # Partner mentions
        'Abakion kunde Danmark',
        'Logos Dynamics kunde',
        'NAV24 reference',
        'ERP-Gruppen kunde case',
        # Certifications & events
        'Microsoft Dynamics partner Danmark kunde',
        'Business Central go-live Danmark',
        'Navision opgradering virksomhed',
        # Industry specific
        'Navision manufacturing Danmark',
        'Dynamics NAV distribution virksomhed',
        'Business Central finans virksomhed',
        # Danish specific terms
        'regnskabssystem Navision',
        'ERP system Dynamics NAV',
        'Microsoft partner ERP kunde',
    ],
    'NO': [
        'Navision case study Norge',
        'Dynamics NAV kunde Norge',
        'Business Central referanse Norge',
        'NAV24 kunde Norge',
        'Microsoft Dynamics partner Norge',
        'Navision implementering bedrift',
        'Business Central go-live Norge',
    ],
    'SE': [
        'Navision case study Sverige',
        'Dynamics NAV kund Sverige',
        'Business Central referens Sverige',
        'NAV24 kund Sverige',
        'Microsoft Dynamics partner Sverige',
        'Navision implementering företag',
        'Business Central lansering Sverige',
    ],
    'DE': [
        'Navision Fallstudie Deutschland',
        'Dynamics NAV Kunde Deutschland',
        'Business Central Referenz Deutschland',
        'Microsoft Dynamics Partner Deutschland',
        'Navision Implementierung Unternehmen',
        'Business Central Einführung',
        'NAV24 Kunde Deutschland',
    ],
    'UK': [
        'Navision case study UK',
        'Dynamics NAV customer UK',
        'Business Central implementation UK',
        'Microsoft Dynamics partner UK',
        'Navision go-live United Kingdom',
        'Business Central customer story UK',
    ],
    'US': [
        'Navision case study USA',
        'Dynamics NAV customer USA',
        'Business Central implementation USA',
        'Microsoft Dynamics partner United States',
        'Navision go-live America',
        'Business Central customer success',
    ],
    'NL': [
        'Navision case study Nederland',
        'Dynamics NAV klant Nederland',
        'Business Central implementatie',
        'Microsoft Dynamics partner Nederland',
        'Navision go-live Nederland',
    ],
    'BE': [
        'Navision case study België',
        'Dynamics NAV klant België',
        'Business Central implementatie',
        'Microsoft Dynamics partner België',
    ],
    'FI': [
        'Navision case study Suomi',
        'Dynamics NAV asiakas Suomi',
        'Business Central toteutus',
        'Microsoft Dynamics partner Suomi',
    ],
    'FR': [
        'Navision étude de cas France',
        'Dynamics NAV client France',
        'Business Central implémentation France',
        'Microsoft Dynamics partenaire France',
        'Navision mise en œuvre entreprise France',
        'Business Central référence France',
    ],
    'IT': [
        'Navision case study Italia',
        'Dynamics NAV cliente Italia',
        'Business Central implementazione Italia',
        'Microsoft Dynamics partner Italia',
        'Navision azienda Italia',
    ],
    'ES': [
        'Navision estudio de caso España',
        'Dynamics NAV cliente España',
        'Business Central implementación España',
        'Microsoft Dynamics partner España',
        'Navision empresa España',
    ],
    'PL': [
        'Navision case study Polska',
        'Dynamics NAV klient Polska',
        'Business Central wdrożenie Polska',
        'Microsoft Dynamics partner Polska',
        'Navision firma Polska',
    ],
    'IN': [
        'Navision case study India',
        'Dynamics NAV customer India',
        'Business Central implementation India',
        'Microsoft Dynamics partner India',
        'Navision company India',
    ],
    'CA': [
        'Navision case study Canada',
        'Dynamics NAV customer Canada',
        'Business Central implementation Canada',
        'Microsoft Dynamics partner Canada',
        'Navision company Canada',
    ],
    'AU': [
        'Navision case study Australia',
        'Dynamics NAV customer Australia',
        'Business Central implementation Australia',
        'Microsoft Dynamics partner Australia',
        'Navision company Australia',
    ],
    'JP': [
        'Navision 事例 日本',
        'Dynamics NAV 顧客 日本',
        'Business Central 導入 日本',
        'Microsoft Dynamics パートナー 日本',
        'Navision 企業 日本',
    ],
    'BR': [
        'Navision estudo de caso Brasil',
        'Dynamics NAV cliente Brasil',
        'Business Central implementação Brasil',
        'Microsoft Dynamics partner Brasil',
        'Navision empresa Brasil',
    ],
    'MX': [
        'Navision estudio de caso México',
        'Dynamics NAV cliente México',
        'Business Central implementación México',
        'Microsoft Dynamics partner México',
        'Navision empresa México',
    ],
    'SG': [
        'Navision case study Singapore',
        'Dynamics NAV customer Singapore',
        'Business Central implementation Singapore',
        'Microsoft Dynamics partner Singapore',
        'Navision company Singapore',
    ],
    'AE': [
        'Navision case study UAE',
        'Dynamics NAV customer UAE',
        'Business Central implementation UAE',
        'Microsoft Dynamics partner UAE',
        'Navision company Dubai',
    ],
    'ZA': [
        'Navision case study South Africa',
        'Dynamics NAV customer South Africa',
        'Business Central implementation South Africa',
        'Microsoft Dynamics partner South Africa',
        'Navision company South Africa',
    ],
    'KR': [
        'Navision 사례 연구 한국',
        'Dynamics NAV 고객 한국',
        'Business Central 구현 한국',
        'Microsoft Dynamics 파트너 한국',
        'Navision 기업 한국',
    ],
    'CH': [
        'Navision Fallstudie Schweiz',
        'Dynamics NAV Kunde Schweiz',
        'Business Central Einführung Schweiz',
        'Microsoft Dynamics Partner Schweiz',
        'Navision Unternehmen Schweiz',
    ],
    'AT': [
        'Navision Fallstudie Österreich',
        'Dynamics NAV Kunde Österreich',
        'Business Central Einführung Österreich',
        'Microsoft Dynamics Partner Österreich',
        'Navision Unternehmen Österreich',
    ],
    'IE': [
        'Navision case study Ireland',
        'Dynamics NAV customer Ireland',
        'Business Central implementation Ireland',
        'Microsoft Dynamics partner Ireland',
        'Navision company Ireland',
    ],
    'NZ': [
        'Navision case study New Zealand',
        'Dynamics NAV customer New Zealand',
        'Business Central implementation New Zealand',
        'Microsoft Dynamics partner New Zealand',
        'Navision company New Zealand',
    ],
    'PT': [
        'Navision estudo de caso Portugal',
        'Dynamics NAV cliente Portugal',
        'Business Central implementação Portugal',
        'Microsoft Dynamics partner Portugal',
        'Navision empresa Portugal',
    ],
    'GR': [
        'Navision case study Greece',
        'Dynamics NAV customer Greece',
        'Business Central implementation Greece',
        'Microsoft Dynamics partner Greece',
        'Navision company Greece',
    ],
    'CZ': [
        'Navision case study Czech Republic',
        'Dynamics NAV customer Czech Republic',
        'Business Central implementation Czech Republic',
        'Microsoft Dynamics partner Czech Republic',
        'Navision company Czech Republic',
    ],
    'GLOBAL': [
        'Navision customer case study',
        'Dynamics NAV implementation success',
        'Business Central customer story',
        'Microsoft Dynamics NAV go-live',
        'Dynamics 365 Business Central success',
        'Navision ERP implementation',
        'Microsoft Dynamics partner customer',
        'Business Central transformation',
    ],
}

# Job boards to SKIP (we want actual companies)
JOB_BOARDS = [
    'linkedin.com/jobs', 'indeed.com', 'glassdoor.com', 'ziprecruiter.com',
    'jobindex.dk', 'jobbnorge.no', 'stepstone', 'monster', 'careerbuilder',
    'nigelfrank.com', 'computerpeople', 'it-jobbank', 'workium.dk',
]

# Generic content patterns to EXCLUDE (not real companies)
EXCLUDE_PATTERNS = [
    # List articles / directories
    'best 10', 'top 20', 'top 50', 'best places', 'near me', 'nearby',
    'directory', 'list of', 'liste over', 'verzeichnis',
    # Currency / calculators
    'currency', 'converter', 'exchange rate', 'valuta', 'usd to', 'eur to',
    'calculator', 'omregner', 'rechner',
    # Generic web pages
    'how to', 'how long', 'what is', 'guide to', 'tutorial', 'faq',
    'vs', 'versus', 'comparison', 'review', 'reddit', 'quora',
    # Non-company sites
    'wikipedia', 'youtube', 'facebook', 'twitter', 'instagram', 'tiktok',
    'pinterest', 'medium', 'substack', 'wordpress', 'blogspot',
    # Job/career generic
    'job opening', 'we are hiring', 'join our team', 'careers at',
    # Forum/discussion
    'forum', 'thread', 'discussion', 'comments', 'answers',
]

# Keywords that indicate a REAL company (at least one should be present)
COMPANY_INDICATORS = [
    'a/s', 'aps', 'ab', 'as', 'gmbh', 'ltd', 'llc', 'inc', 'corp', 'corporation',
    'group', 'holding', 'industries', 'solutions', 'technologies', 'systems',
    'services', 'consulting', 'consult', 'partners', 'international',
    'danmark', 'norge', 'sverige', 'deutschland', 'netherlands',
    'navision', 'dynamics', 'business central', 'erp', 'implementation',
    'case study', 'customer', 'reference', 'success story', 'go-live',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def scrape(country='GLOBAL'):
    """Find companies using Navision."""
    print(f"  📍 Searching for companies in {country}")
    
    companies = find_companies_via_searxng(country)
    
    if companies:
        print(f"  ✅ Found {len(companies)} companies")
        return companies
    
    print(f"  ⚠️  No companies found for {country}")
    return []

def find_companies_via_searxng(country='GLOBAL'):
    """
    Search SearXNG for companies using Navision.
    
    Returns list of company dictionaries.
    """
    companies = []
    seen = set()
    
    # Try main queries first, then additional queries, then fallback to GLOBAL
    if country in COMPANY_QUERIES:
        queries = COMPANY_QUERIES[country]
    elif country in ADDITIONAL_QUERIES:
        queries = ADDITIONAL_QUERIES[country]
    else:
        queries = COMPANY_QUERIES['GLOBAL']
    print(f"  🔍 Using {len(queries)} queries via SearXNG")
    
    for query in queries:
        try:
            url = f"{SEARXNG_URL}/search"
            params = {
                'q': query,
                'pageno': 1,
                'format': 'html',
            }
            
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('article', class_='result')
            
            for result in results[:15]:  # Max 15 per query
                try:
                    title_elem = result.find('h3').find('a') if result.find('h3') else None
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # Skip job boards
                    if any(job_board in url.lower() for job_board in JOB_BOARDS):
                        continue
                    
                    # Skip generic sites
                    if any(x in url.lower() for x in ['wikipedia', 'youtube', 'microsoft.com']):
                        continue
                    
                    # Extract company name
                    company = extract_company_from_result(title, url, result)
                    
                    if company and company.lower() not in seen:
                        # STRICT FILTERING - Only accept real companies
                        if not looks_like_company(company):
                            continue
                        
                        # Extra check: must have some company indicator in title or URL
                        if not has_company_indicator(title + ' ' + url):
                            # Allow if domain looks professional (not generic content site)
                            domain = extract_domain(url)
                            if not any(x in domain.lower() for x in ['.com', '.dk', '.de', '.se', '.no', '.nl', '.be']):
                                continue
                        
                        seen.add(company.lower())
                        companies.append({
                            'company_name': company,
                            'country': country if country != 'GLOBAL' else 'DK',
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
                        
                except Exception as e:
                    continue
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            continue
    
    return companies

def extract_company_from_result(title, url, result):
    """Extract company name from search result."""
    # Try from URL domain first
    domain = extract_domain(url)
    
    # If domain looks like a company (not generic)
    if domain and len(domain) > 3:
        if domain not in ['google', 'bing', 'yahoo', 'facebook', 'twitter']:
            # Try to get a better name from title
            # Pattern: "Company X - Navision Case Study" or "Company X implements Navision"
            if ' - ' in title:
                candidate = title.split(' - ')[0].strip()
                if len(candidate) > 2 and len(candidate) < 60:
                    return candidate
            
            # Use domain as company name
            return domain.replace('-', ' ').replace('.', ' ').title()
    
    # Try from title patterns
    patterns = [
        ' - ',  # "Company - Description"
        ' implements ',  # "Company implements Navision"
        ' uses ',  # "Company uses Navision"
        ' chose ',  # "Company chose Navision"
        ' customer ',  # "Company customer story"
    ]
    
    for pattern in patterns:
        if pattern in title.lower():
            parts = title.lower().split(pattern)
            if parts:
                candidate = parts[0].strip()
                if len(candidate) > 2 and len(candidate) < 60:
                    return candidate.title()
    
    return domain

def looks_like_company(name):
    """Check if string looks like a company name (not noise)."""
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
    
    # Skip "X Com" patterns (generic domain references like "Github Com", "Wise Com")
    if name_stripped.endswith('com') and len(name_stripped) < 15:
        # Allow if it has company indicators
        if not any(x in name_lower for x in ['group', 'inc', 'ltd', 'corporation', 'company', 'ab', 'as', 'aps', 'gmbh']):
            return False
    
    # Skip "X Org" patterns (generic domain references)
    if name_stripped.endswith('org'):
        # Allow proper org names like "Red Cross Org"
        if ' ' not in name_lower or len(name_stripped) < 20:
            return False
        # Still reject suspicious patterns
        if any(x in name_lower for x in ['secrets', 'best', 'top', 'guide']):
            return False
    
    # Check for EXCLUDE patterns (strong filter)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in name_lower:
            return False
    
    # Skip if starts with numbers (like "25 Best...")
    if name[0].isdigit():
        return False
    
    # Skip obvious non-companies
    if any(x in name_lower for x in ['salon', 'nail', 'spa', 'tattoo', 'restaurant', 'cafe']):
        # Unless it's a large chain with proper company structure
        if not any(x in name_lower for x in ['group', 'inc', 'ltd', 'corporation', 'international']):
            return False
    
    # Skip generic web references
    if any(x in name_lower for x in ['docs ', 'documentation', 'forum', 'blog', 'wiki']):
        return False
    
    return True


def has_company_indicator(text):
    """Check if text contains indicators of a real company."""
    text_lower = text.lower()
    for indicator in COMPANY_INDICATORS:
        if indicator in text_lower:
            return True
    return False

def extract_domain(url):
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('/')[0]
    except:
        return ''

if __name__ == '__main__':
    print("Testing company finder for DK...")
    result = scrape('DK')
    print(f"\nFound {len(result)} companies")
    for company in result[:15]:
        print(f"  - {company['company_name']}: {company['website']}")

# Additional country queries for expanded global coverage
ADDITIONAL_QUERIES = {
    'RU': [
        'Navision case study Russia',
        'Dynamics NAV клиент Россия',
        'Business Central внедрение Россия',
        'Microsoft Dynamics партнер Россия',
        'Navision компания Россия',
    ],
    'TR': [
        'Navision case study Turkey',
        'Dynamics NAV müşteri Türkiye',
        'Business Central uygulama Türkiye',
        'Microsoft Dynamics partner Türkiye',
        'Navision şirket Türkiye',
    ],
    'ID': [
        'Navision case study Indonesia',
        'Dynamics NAV customer Indonesia',
        'Business Central implementasi Indonesia',
        'Microsoft Dynamics partner Indonesia',
        'Navision perusahaan Indonesia',
    ],
    'TH': [
        'Navision case study Thailand',
        'Dynamics NAV customer Thailand',
        'Business Central implementasi Thailand',
        'Microsoft Dynamics partner Thailand',
        'Navision perusahaan Thailand',
    ],
    'MY': [
        'Navision case study Malaysia',
        'Dynamics NAV customer Malaysia',
        'Business Central implementasi Malaysia',
        'Microsoft Dynamics partner Malaysia',
        'Navision company Malaysia',
    ],
    'VN': [
        'Navision case study Vietnam',
        'Dynamics NAV khách hàng Việt Nam',
        'Business Central triển khai Việt Nam',
        'Microsoft Dynamics partner Việt Nam',
        'Navision công ty Việt Nam',
    ],
    'AR': [
        'Navision estudio de caso Argentina',
        'Dynamics NAV cliente Argentina',
        'Business Central implementación Argentina',
        'Microsoft Dynamics partner Argentina',
        'Navision empresa Argentina',
    ],
    'CL': [
        'Navision estudio de caso Chile',
        'Dynamics NAV cliente Chile',
        'Business Central implementación Chile',
        'Microsoft Dynamics partner Chile',
        'Navision empresa Chile',
    ],
    'CO': [
        'Navision estudio de caso Colombia',
        'Dynamics NAV cliente Colombia',
        'Business Central implementación Colombia',
        'Microsoft Dynamics partner Colombia',
        'Navision empresa Colombia',
    ],
    'PE': [
        'Navision estudio de caso Perú',
        'Dynamics NAV cliente Perú',
        'Business Central implementación Perú',
        'Microsoft Dynamics partner Perú',
        'Navision empresa Perú',
    ],
}
