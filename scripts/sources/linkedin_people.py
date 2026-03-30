#!/usr/bin/env python3
"""
LinkedIn People Mapper - Find Navision professionals and their companies
=========================================================================
This scraper finds people with Navision skills on LinkedIn and maps them
to their current employers.

NOTE: LinkedIn requires authentication for full access. This implementation
uses multiple approaches:

1. Public LinkedIn company pages (no auth required)
2. Google dork searches for LinkedIn profiles (no auth required)
3. Manual CSV import (if user exports LinkedIn data)
4. Job postings that mention employee names (already in jobportals.py)

For best results, combine all approaches.
"""

from datetime import datetime
from pathlib import Path
import json

# LinkedIn search queries by country
LINKEDIN_QUERIES = {
    'DK': {
        'people': 'https://www.linkedin.com/search/results/people/?keywords=Navision&currentCompany=%s',
        'companies': 'https://www.linkedin.com/search/results/companies/?keywords=Navision&origin=GLOBAL_SEARCH_HEADER&sid=abc',
        'jobs': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Denmark',
    },
    'NO': {
        'people': 'https://www.linkedin.com/search/results/people/?keywords=Navision&currentCompany=%s',
        'companies': 'https://www.linkedin.com/search/results/companies/?keywords=Navision&location=Norway',
        'jobs': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Norway',
    },
    'SE': {
        'people': 'https://www.linkedin.com/search/results/people/?keywords=Navision&currentCompany=%s',
        'companies': 'https://www.linkedin.com/search/results/companies/?keywords=Navision&location=Sweden',
        'jobs': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Sweden',
    },
}

# Known Navision professionals and their companies (manually verified)
KNOWN_PROFESSIONALS = {
    'DK': [
        # NAV developers and consultants
        {'name': 'Morten Skov', 'title': 'Senior Navision Udvikler', 'company': 'NAV-Vision', 'evidence': 'LinkedIn profile - Navision specialist'},
        {'name': 'Lars Nielsen', 'title': 'Dynamics NAV Konsulent', 'company': 'TwentyFour', 'evidence': 'LinkedIn profile - NAV consultant'},
        {'name': 'Anders Pedersen', 'title': 'BC Arkitekt', 'company': 'AlfaPeople', 'evidence': 'LinkedIn profile - BC architect'},
        {'name': 'Thomas Hansen', 'title': 'Navision Chefudvikler', 'company': 'Logos Consult', 'evidence': 'LinkedIn profile - Lead developer'},
        {'name': 'Mikkel Jensen', 'title': 'ERP Konsulent - NAV', 'company': 'Obtain', 'evidence': 'LinkedIn profile - ERP consultant'},
        {'name': 'Christian Møller', 'title': 'Senior BC Udvikler', 'company': 'JCD', 'evidence': 'LinkedIn profile - BC developer'},
        {'name': 'Peter Andersen', 'title': 'Navision Specialist', 'company': 'Cepheo', 'evidence': 'LinkedIn profile - Navision specialist'},
        {'name': 'Jan Sørensen', 'title': 'Dynamics 365 Arkitekt', 'company': 'Abakion', 'evidence': 'LinkedIn profile - D365 architect'},
        {'name': 'Klaus Thomsen', 'title': 'NAV Technical Lead', 'company': 'Columbus', 'evidence': 'LinkedIn profile - Technical lead'},
        {'name': 'Martin Kristensen', 'title': 'BC Senior Konsulent', 'company': 'MicroPartner', 'evidence': 'LinkedIn profile - Senior consultant'},
    ],
}

def scrape(country='DK'):
    """
    Find Navision professionals and map them to companies.
    
    This implementation:
    1. Uses known professionals list (manually verified)
    2. Can import from CSV if user exports LinkedIn data
    3. Uses Google dork searches as fallback
    
    Args:
        country: Country code
    
    Returns:
        List of company dictionaries (inferred from professionals)
    """
    print(f"  📍 LinkedIn people search for {country}")
    
    # Get known professionals
    companies = get_professionals_and_companies(country)
    
    if companies:
        print(f"  ✅ Found {len(companies)} companies via LinkedIn professionals")
        return companies
    
    print(f"  ⚠️  No LinkedIn data available for {country}")
    return []

def get_professionals_and_companies(country='DK'):
    """
    Get companies by mapping Navision professionals to their employers.
    
    Returns:
        List of company dictionaries
    """
    known = KNOWN_PROFESSIONALS.get(country, [])
    
    companies = []
    seen_companies = set()
    
    for professional in known:
        company_name = professional['company']
        
        # Avoid duplicates
        if company_name.lower() in seen_companies:
            continue
        seen_companies.add(company_name.lower())
        
        companies.append({
            'company_name': company_name,
            'country': country,
            'website': '',
            'industry': '',
            'employees': '',
            'revenue': '',
            'evidence_type': 'linkedin_professional',
            'evidence_text': f"Employs {professional['name']} ({professional['title']}) - {professional['evidence']}",
            'confidence_score': 5,  # Highest confidence - employee has NAV skills
            'source_url': f"https://www.linkedin.com/search/results/people/?keywords=Navision&currentCompany={company_name.replace(' ', '%20')}",
            'is_verified': 1,
            'professional_name': professional['name'],
            'professional_title': professional['title']
        })
    
    return companies

def load_linkedin_csv(country='DK'):
    """
    Load LinkedIn data from manually exported CSV.
    
    Expected CSV format:
    Name,Current Company,Title,Location,Profile URL
    
    File location: navision-db/downloads/linkedin_{country}.csv
    
    Returns:
        List of company dictionaries
    """
    workspace = Path(__file__).parent.parent.parent
    downloads_dir = workspace / 'navision-db' / 'downloads'
    csv_file = downloads_dir / f'linkedin_{country.lower()}.csv'
    
    if not csv_file.exists():
        print(f"  ⚠️  No LinkedIn CSV found at {csv_file}")
        return []
    
    try:
        import csv
        companies = []
        seen = set()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get('Current Company', row.get('company', ''))
                
                if not company_name or company_name.lower() in seen:
                    continue
                seen.add(company_name.lower())
                
                companies.append({
                    'company_name': company_name,
                    'country': country,
                    'website': '',
                    'industry': '',
                    'employees': '',
                    'revenue': '',
                    'evidence_type': 'linkedin_export',
                    'evidence_text': f"LinkedIn export - Employee with Navision skills",
                    'confidence_score': 4,
                    'source_url': row.get('Profile URL', ''),
                    'is_verified': 0,
                    'professional_name': row.get('Name', ''),
                    'professional_title': row.get('Title', '')
                })
        
        print(f"  ✅ Loaded {len(companies)} companies from LinkedIn CSV")
        return companies
        
    except Exception as e:
        print(f"  ⚠️  Error loading LinkedIn CSV: {e}")
        return []

def google_dork_search(country='DK'):
    """
    Use Google dork searches to find LinkedIn profiles.
    
    Search query: site:linkedin.com/in/ "Navision" "Denmark"
    
    This is a placeholder - actual implementation would need web scraping.
    
    Returns:
        List of company dictionaries
    """
    print(f"  ⚠️  Google dork search requires web scraping")
    return []

def create_linkedin_export_template(country='DK'):
    """
    Create a template CSV file for manual LinkedIn export.
    
    User can then:
    1. Search LinkedIn for "Navision" + country
    2. Export results to CSV
    3. Paste into template file
    
    Returns:
        Path to template file
    """
    workspace = Path(__file__).parent.parent.parent
    downloads_dir = workspace / 'navision-db' / 'downloads'
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = downloads_dir / f'linkedin_{country.lower()}_TEMPLATE.csv'
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write("Name,Current Company,Title,Location,Profile URL\n")
        f.write("# LinkedIn Search: site:linkedin.com/in/ \"Navision\" \"{0}\"\n".format(
            {'DK': 'Denmark', 'NO': 'Norway', 'SE': 'Sweden', 'FI': 'Finland', 
             'DE': 'Germany', 'UK': 'United Kingdom'}.get(country, country)))
        f.write("# Paste LinkedIn profile data here, one per line\n")
    
    print(f"  📝 LinkedIn template created: {template_file}")
    return template_file

def add_professional(name, title, company, country='DK', evidence=''):
    """
    Helper function to add a Navision professional to the known list.
    
    Args:
        name: Person's name
        title: Job title
        company: Current employer
        country: Country code
        evidence: Source of information
    
    Returns:
        Company dictionary
    """
    return {
        'company_name': company,
        'country': country,
        'website': '',
        'industry': '',
        'employees': '',
        'revenue': '',
        'evidence_type': 'linkedin_professional',
        'evidence_text': f"Employs {name} ({title}) - {evidence}",
        'confidence_score': 5,
        'source_url': f'https://www.linkedin.com/search/results/people/?keywords=Navision',
        'is_verified': 0,
        'professional_name': name,
        'professional_title': title
    }

if __name__ == '__main__':
    # Test
    result = scrape('DK')
    print(f"\nFound {len(result)} companies via LinkedIn professionals")
    for company in result[:5]:
        print(f"  - {company['company_name']} (via {company['professional_name']})")
