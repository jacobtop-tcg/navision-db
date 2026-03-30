#!/usr/bin/env python3
"""
FIND SMOKING GUNS - Rigtige beviser for Navision brug
Ikke bare lister - men FAKTISKE beviser!
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# SMOKING GUN PATTERNS - Dette er FAKTISKE beviser
SMOKING_GUNS = {
    # Job postings FRA virksomheden selv
    'job_internal': [
        r'vi\s+søger.*nav.*udvikler',
        r'hiring.*nav.*developer.*internal',
        r'erp.*ansvarlig.*til\s+vores',
        r'nav\s+administrator.*intern',
        r'dynamics\s+nav.*til\s+vores\s+team',
    ],
    
    # Case studies SKREVET AF kunder
    'customer_case_study': [
        r'sådan\s+bruger\s+vi.*navision',
        r'how\s+we\s+use.*dynamics\s+nav',
        r'vores\s+rejse\s+med.*navision',
        r'our\s+journey\s+with.*dynamics',
        r'gik\s+live\s+med.*nav',
        r'went\s+live\s+with.*navision',
    ],
    
    # Virksomhedswebsites der nævner Navision
    'company_website': [
        r'vores\s+erp.*navision',
        r'our\s+erp.*dynamics\s+nav',
        r'bruger.*microsoft\s+dynamics\s+nav',
        r'using.*microsoft\s+dynamics\s+nav',
        r'navision.*back.?office',
    ],
    
    # Konference oplæg / præsentationer
    'conference_talk': [
        r'oplæg.*navision\s+brugere',
        r'konference.*nav\s+erfaringer',
        r'user\s+conference.*navision\s+story',
        r'customer\s+story.*navision',
    ],
    
    # Pressemeddelelser om go-live
    'press_release': [
        r'går\s+live.*navision',
        r'go.?live.*dynamics\s+nav',
        r'implementerer.*navision',
        r'implementing.*microsoft\s+dynamics\s+nav',
    ],
}

def check_smoking_gun(text, url=''):
    """
    Tjek om text indeholder en SMOKING GUN
    Returnerer: (is_gun, gun_type, confidence)
    """
    text_lower = text.lower()
    url_lower = url.lower()
    
    guns_found = []
    
    for gun_type, patterns in SMOKING_GUNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                guns_found.append((gun_type, pattern))
    
    if guns_found:
        # Højere confidence hvis multiple guns
        if len(guns_found) >= 2:
            return True, guns_found, 'HIGH'
        else:
            return True, guns_found, 'MEDIUM'
    
    return False, [], 'NONE'

def fetch_and_verify(url, company_name):
    """
    Fetch URL og verificer om det er en smoking gun
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return False, [], 'URL_ERROR'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get main content
        text = soup.get_text(separator=' ', strip=True)
        
        # Check for smoking guns
        is_gun, guns, confidence = check_smoking_gun(text, url)
        
        return is_gun, guns, confidence
        
    except Exception as e:
        return False, [], f'ERROR: {e}'

def find_smoking_guns():
    """
    Find smoking guns i eksisterende data
    """
    print(f"[{datetime.utcnow().isoformat()}Z] Starter SMOKING GUN hunt...")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Hent alle companies med source_url
    cur.execute('''
        SELECT id, company_name, country, evidence_text, source_url, source
        FROM companies
        WHERE confidence_score >= 4
        AND source_url IS NOT NULL
        AND source_url != ''
        LIMIT 1000
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Tjekker {len(rows)} virksomheder med URLs...")
    print()
    
    smoking_guns = []
    verified = 0
    rejected = 0
    
    for i, row in enumerate(rows):
        company_name = row['company_name']
        url = row['source_url']
        evidence = row['evidence_text'] or ''
        
        # Tjek evidence først (hurtigt)
        is_gun, guns, confidence = check_smoking_gun(evidence, url)
        
        if is_gun and confidence == 'HIGH':
            smoking_guns.append({
                'name': company_name,
                'country': row['country'],
                'url': url,
                'guns': guns,
                'confidence': confidence,
                'source': 'evidence_text'
            })
            verified += 1
        elif is_gun:
            # Medium confidence - fetch og verificer
            is_verified, verified_guns, verif_conf = fetch_and_verify(url, company_name)
            
            if is_verified:
                smoking_guns.append({
                    'name': company_name,
                    'country': row['country'],
                    'url': url,
                    'guns': verified_guns,
                    'confidence': verif_conf,
                    'source': 'verified_url'
                })
                verified += 1
            else:
                rejected += 1
        else:
            rejected += 1
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  ⏳ {i+1}/{len(rows)} (smoking guns: {len(smoking_guns)}, rejected: {rejected})")
    
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ SMOKING GUNS FUNDET: {len(smoking_guns)}")
    print(f"❌ REJECTED: {rejected}")
    print()
    
    print("📋 TOP SMOKING GUNS:")
    for gun in smoking_guns[:20]:
        print(f"  ✅ {gun['name']} ({gun['country']})")
        print(f"     Type: {', '.join([g[0] for g in gun['guns']])}")
        print(f"     Confidence: {gun['confidence']}")
        print(f"     URL: {gun['url']}")
        print()
    
    return smoking_guns

if __name__ == '__main__':
    try:
        find_smoking_guns()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
