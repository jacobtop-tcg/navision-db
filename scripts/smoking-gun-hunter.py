#!/usr/bin/env python3
"""
SMOKING GUN HUNTER V2 - Detektiv Arbejde
==========================================
Finder KUN virksomheder med RIGTIGE beviser for Navision brug.

Smoking Gun Definition:
- Job posting FRA virksomheden selv (ikke konsulenthus)
- Kundecase SKREVET AF kunden (ikke partner)
- Go-live pressemeddelelse
- Konference oplæg AF kunden
- Tech stack der nævner NAV som deres system

IKKE smoking guns:
- Partner der nævner kunde (kan være gammelt)
- Job consultant der skal ud til kunde (usikkert)
- Generel omtale uden konkret brug
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from pathlib import Path
import re
import time
import random

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
STATE_DIR = SCRIPT_DIR.parent / 'state'

# SEARXNG URL
SEARXNG_URL = "http://127.0.0.1:8080"

# SMOKING GUN SEARCH QUERIES - Meget specifikke (undgå false positives)
SMOKING_GUN_QUERIES = {
    # 1. Job postings - virksomhed søger NAV folk (de bruger det!)
    'job_internal': [
        '"Dynamics NAV" developer "our company" site:linkedin.com/jobs',
        '"Business Central" developer "we are looking" site:linkedin.com/jobs',
        '"Microsoft Dynamics NAV" administrator "internal"',
        '"Microsoft Dynamics NAV" "in-house" developer',
        '"Dynamics NAV" udvikler "vores team" site:jobindex.dk',
        '"Dynamics NAV" "til vores" site:jobindex.dk',
        '"Business Central" "vores ERP" udvikler',
        '"Dynamics 365 Business Central" developer jobs',
    ],
    
    # 2. Kundecases - skrevet AF kunden selv
    'customer_case': [
        '"sådan bruger vi" "Dynamics NAV" site:.dk',
        '"how we use" "Microsoft Dynamics NAV" site:.com',
        '"our journey with" "Dynamics 365 Business Central"',
        '"vores rejse med" "Microsoft Dynamics"',
        '"gik live med" "Dynamics NAV" site:.dk',
        '"went live with" "Microsoft Dynamics NAV"',
        '"implementerede" "Dynamics NAV" case',
        '"customer story" "Business Central" manufacturing',
    ],
    
    # 3. Go-live pressemeddelelser
    'go_live': [
        '"går live med" "Dynamics NAV" site:.dk',
        '"go-live" "Microsoft Dynamics NAV" customer',
        '"implementerer" "Microsoft Dynamics NAV"',
        '"has implemented" "Microsoft Dynamics 365 Business Central"',
        '"Dynamics NAV" "go live" manufacturing',
        '"Business Central" "went live" retail',
    ],
    
    # 4. Konference oplæg (kunder der præsenterer)
    'conference': [
        '"Dynamics NAV" "customer story" site:community.dynamics.com',
        '"Business Central" "customer" site:community.dynamics.com',
        '"NAV" "user conference" customer presentation',
        '"Business Central" "customer success" site:microsoft.com',
        '"Dynamics 365" "customer case" site:youtube.com',
    ],
    
    # 5. Tech stack / ERP pages
    'tech_stack': [
        '"our ERP" "Microsoft Dynamics NAV"',
        '"vores ERP" "Dynamics NAV" site:.dk',
        '"technology stack" "Microsoft Dynamics"',
        '"systems we use" "Business Central"',
        '"Microsoft Dynamics NAV" "our finance system"',
    ],
    
    # 6. Partner customer lists (høj kvalitet)
    'partner_customers': [
        'site:9altitudes.com "kundereferencer"',
        'site:elbek-vejrup.dk "kunder"',
        'site:obtain.dk "customers"',
        'site:jcd.dk "cases"',
        'site:vektus.dk "kunder"',
        'site:dynamicsinspire.dk "referencer"',
        'site:appsruntheworld.com "Microsoft Dynamics NAV" customers',
    ],
}

# Evidence patterns der indikerer RIGTIG smoking gun
STRONG_EVIDENCE_PATTERNS = [
    r'(CEO|CFO|CTO|IT Director|IT Chef) .* (Dynamics NAV|Microsoft Dynamics|Navision|Business Central)',  # Executive quote
    r'(vi bruger|we use|our) (ERP|system) .* (Dynamics NAV|Microsoft Dynamics|Navision|Business Central)',  # Direct usage
    r'(gik live|went live|go-live) .* (Dynamics NAV|Microsoft Dynamics|Navision|Business Central)',  # Implementation
    r'(implementerede|implemented) .* (Dynamics NAV|Microsoft Dynamics|Business Central)',  # Implementation
    r'(succes|success|tilfreds|satisfied) .* (Dynamics NAV|Microsoft Dynamics|Navision|Business Central)',  # Success story
    r'(søger|hiring) .* (Dynamics NAV|Microsoft Dynamics|Navision|Business Central) .* (udvikler|developer|konsulent|consultant)',  # Hiring
]

def search_searxng(query, max_results=20):
    """Search via SearXNG"""
    try:
        url = f"{SEARXNG_URL}/search"
        params = {
            "q": query,
            "format": "json",
            "language": "all",
            "engines": "google,bing,duckduckgo"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('results', [])[:max_results]
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
    return []

def fetch_page_content(url):
    """Fetch and extract content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text = ' '.join(text.split())
            return text[:10000]  # Limit to 10k chars
    except Exception as e:
        pass
    return None

def is_smoking_gun(content, url):
    """
    Analyze content to determine if it's a REAL smoking gun
    Returns: (is_gun, confidence, company_name, evidence_text)
    """
    if not content:
        return False, 0, None, None
    
    content_lower = content.lower()
    url_lower = url.lower()
    
    # Filter out FALSE POSITIVES
    # nav.com = fintech company, NOT Microsoft Navision
    if 'nav.com' in url_lower and 'dynamics' not in content_lower and 'microsoft' not in content_lower:
        return False, 0, None, None
    
    # Must mention Microsoft/ERP context to avoid false positives
    if not any(kw in content_lower for kw in ['microsoft', 'erp', 'dynamics', 'navision', 'business central']):
        return False, 0, None, None
    
    # Check for strong evidence patterns
    evidence_found = []
    for pattern in STRONG_EVIDENCE_PATTERNS:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        if matches:
            # Handle tuple results from regex groups
            for match in matches[:2]:
                if isinstance(match, tuple):
                    # Join tuple elements into single string
                    evidence_found.append(' '.join(str(m) for m in match if m))
                else:
                    evidence_found.append(str(match))
    
    if not evidence_found:
        return False, 0, None, None
    
    # Try to extract company name
    company_name = extract_company_name(content, url)
    if not company_name:
        return False, 0, None, None
    
    # Filter out nav.com as company name
    if company_name.lower() == 'nav':
        return False, 0, None, None
    
    # Calculate confidence
    confidence = min(5, 3 + len(evidence_found))  # 3-5 based on evidence count
    
    # Must have company name AND evidence
    if company_name and len(company_name) > 2:
        evidence_text = ' | '.join(evidence_found[:3])
        return True, confidence, company_name, evidence_text
    
    return False, 0, None, None

def extract_company_name(content, url):
    """Extract company name from content or URL"""
    # Try URL first (often cleaner)
    if 'linkedin.com/company/' in url:
        match = re.search(r'linkedin\.com/company/([^/]+)', url)
        if match:
            return match.group(1).replace('-', ' ').title()
    
    if 'site:.dk' in url or '.dk/' in url:
        match = re.search(r'//(?:www\.)?([^/]+)\.dk', url)
        if match:
            return match.group(1).replace('-', ' ').title()
    
    # Try to find in content (look for company indicators)
    patterns = [
        r'(?:virksomhed|company|kunde|customer)[:\s]+([A-Z][^\n\.]{2,50})',
        r'([A-Z][a-z]+ (?:A/S|ApS|AS|AB|Ltd|GmbH|Inc|LLC))',
        r'Vi i ([A-Z][^\n\.]{2,40}) bruger',
        r'Her hos ([A-Z][^\n\.]{2,40})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if len(name) > 2 and len(name) < 60:
                return name
    
    return None

def add_to_database(company_name, country, evidence_type, evidence_text, 
                   confidence, source_url, gun_category):
    """Add smoking gun to database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        
        # Check if exists
        cur.execute('SELECT id FROM companies WHERE company_name = ? AND source_url = ?', 
                  (company_name, source_url[:500]))
        if cur.fetchone():
            conn.close()
            return False
        
        # Determine country from URL
        if not country or country == 'XX':
            if '.dk' in source_url:
                country = 'DK'
            elif '.de' in source_url:
                country = 'DE'
            elif '.uk' in source_url or '.co.uk' in source_url:
                country = 'UK'
            elif '.se' in source_url:
                country = 'SE'
            elif '.no' in source_url:
                country = 'NO'
            elif '.nl' in source_url:
                country = 'NL'
            elif '.fr' in source_url:
                country = 'FR'
            elif '.com' in source_url:
                country = 'US'
            else:
                country = 'XX'
        
        # Insert
        cur.execute('''
            INSERT INTO companies 
            (company_name, country, evidence_type, evidence_text, 
             confidence_score, source, source_url, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name,
            country,
            f'smoking_gun_{gun_category}',
            evidence_text[:500],
            confidence,
            'smoking_gun_hunter_v2',
            source_url[:500],
            datetime.utcnow().isoformat() + 'Z'
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ DB error: {e}")
        return False

def hunt_smoking_guns():
    """Main hunting loop"""
    print("=" * 80)
    print("🔍 SMOKING GUN HUNTER V2 - Detektiv Arbejde")
    print("=" * 80)
    print()
    
    total_found = 0
    total_added = 0
    total_searched = 0
    
    for category, queries in SMOKING_GUN_QUERIES.items():
        print(f"\n📍 Kategori: {category.upper()}")
        print("-" * 60)
        
        for query in queries:
            print(f"  🔎 {query[:60]}...")
            
            results = search_searxng(query, max_results=15)
            total_searched += 1
            
            for result in results[:10]:
                url = result.get('url', '')
                title = result.get('title', '')
                snippet = result.get('content', '')
                
                # Quick filter - must have NAV/Dynamics keywords
                if not any(kw in (title + snippet).lower() for kw in ['nav', 'dynamics', 'navision', 'business central']):
                    continue
                
                # Fetch full content for deep analysis
                content = fetch_page_content(url)
                if not content:
                    continue
                
                # Analyze for smoking gun
                is_gun, confidence, company, evidence = is_smoking_gun(content, url)
                
                if is_gun and confidence >= 4:
                    total_found += 1
                    
                    # Add to database
                    if add_to_database(company, 'XX', 'smoking_gun', evidence, 
                                      confidence, url, category):
                        total_added += 1
                        print(f"    ✅ SMOKING GUN: {company} (⭐{confidence})")
                        print(f"       {evidence[:80]}")
                        print(f"       {url}")
                        print()
                
                # Rate limiting
                time.sleep(random.uniform(1.0, 2.0))
            
            # Between queries
            time.sleep(random.uniform(2.0, 4.0))
        
        print(f"\n  ⏳ Pause mellem kategorier...")
        time.sleep(5)
    
    print()
    print("=" * 80)
    print(f"📊 RESULTATER:")
    print(f"   Queries kørt: {total_searched}")
    print(f"   Smoking guns fundet: {total_found}")
    print(f"   Tilføjet til DB: {total_added}")
    print("=" * 80)
    
    return total_added

if __name__ == '__main__':
    try:
        # Create state directory if needed
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        
        hunt_smoking_guns()
    except KeyboardInterrupt:
        print("\n\n⚠️  Afbrudt af bruger")
        exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
