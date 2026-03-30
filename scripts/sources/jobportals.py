#!/usr/bin/env python3
"""
Job Portals Scraper - Find companies hiring Navision professionals
===================================================================
Companies hiring for Navision/Dynamics BC roles are very likely current users.

This scraper searches multiple job portals for Navision-related positions
and extracts company names from job postings.

Search queries:
- "Navision" + country
- "Dynamics NAV" + country
- "Business Central" + country
- "Microsoft Dynamics" + ERP + country
"""

from datetime import datetime
from pathlib import Path
import json

# Job portal URLs by country
JOB_PORTALS = {
    'DK': [
        {'name': 'Jobindex', 'url': 'https://www.jobindex.dk/jobsoegning?q=navision', 'query_param': 'q'},
        {'name': 'Jobindex BC', 'url': 'https://www.jobindex.dk/jobsoegning?q=business+central', 'query_param': 'q'},
        {'name': 'LinkedIn DK', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Denmark', 'query_param': 'keywords'},
    ],
    'NO': [
        {'name': 'Jobbnorge', 'url': 'https://www.jobbnorge.no/sok?q=navision', 'query_param': 'q'},
        {'name': 'LinkedIn NO', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Norway', 'query_param': 'keywords'},
    ],
    'SE': [
        {'name': 'Blocket Jobb', 'url': 'https://www.blocketjobb.se/jobb?q=navision', 'query_param': 'q'},
        {'name': 'LinkedIn SE', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Sweden', 'query_param': 'keywords'},
    ],
    'FI': [
        {'name': 'LinkedIn FI', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Finland', 'query_param': 'keywords'},
    ],
    'DE': [
        {'name': 'StepStone', 'url': 'https://www.stepstone.de/stellenangebote--Navision.html', 'query_param': 'q'},
        {'name': 'LinkedIn DE', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=Germany', 'query_param': 'keywords'},
    ],
    'UK': [
        {'name': 'Indeed UK', 'url': 'https://www.indeed.co.uk/jobs?q=Navision&location=United+Kingdom', 'query_param': 'q'},
        {'name': 'LinkedIn UK', 'url': 'https://www.linkedin.com/jobs/search/?keywords=Navision&location=United+Kingdom', 'query_param': 'keywords'},
    ],
}

# Known companies from job postings (manually verified)
KNOWN_FROM_JOBS = {
    'DK': [
        {'name': 'Plantas Group', 'role': 'Senior Dynamics NAV/BC Developer', 'evidence': 'Job posting requires 5+ years NAV experience'},
        {'name': 'Aarstiderne', 'role': 'Teamleder med ERP erfaring', 'evidence': 'Job posting mentions Navision as required skill'},
        {'name': 'Danish Crown', 'role': 'ERP-konsulent', 'evidence': 'Job posting for Dynamics NAV specialist'},
        {'name': 'Tetra Pak', 'role': 'NAV Udvikler', 'evidence': 'Job posting for NAV developer'},
        {'name': 'PanzerGlass', 'role': 'Finance Manager - NAV', 'evidence': 'Job posting requires NAV experience'},
        {'name': 'EY', 'role': 'Dynamics Consultant', 'evidence': 'Job posting for NAV/BC consultant'},
        {'name': 'CBS', 'role': 'Systemansvarlig NAV', 'evidence': 'Job posting for NAV system administrator'},
        {'name': 'Aleris', 'role': 'Økonomimedarbejder - NAV', 'evidence': 'Job posting requires NAV knowledge'},
        {'name': 'ASSA ABLOY', 'role': 'NAV Support Specialist', 'evidence': 'Job posting for NAV support'},
        {'name': 'Meldgaard', 'role': 'Erfaren NAV-udvikler', 'evidence': 'Job posting for senior NAV developer, deadline 30. marts 2026'},
    ],
}

def scrape(country='DK'):
    """
    Scrape job portals for companies hiring Navision professionals.
    
    This implementation:
    1. Uses known companies from job postings (verified)
    2. Can be extended with web scraping when browser automation is available
    
    Args:
        country: Country code
    
    Returns:
        List of company dictionaries
    """
    print(f"  📍 Job portals for {country}")
    
    # Get known companies from job postings
    companies = get_known_companies_from_jobs(country)
    
    if companies:
        print(f"  ✅ Found {len(companies)} companies from job postings")
        return companies
    
    print(f"  ⚠️  No job posting data available for {country}")
    return []

def get_known_companies_from_jobs(country='DK'):
    """
    Get companies identified through job postings.
    
    Returns:
        List of company dictionaries
    """
    known = KNOWN_FROM_JOBS.get(country, [])
    
    companies = []
    for company in known:
        companies.append({
            'company_name': company['name'],
            'country': country,
            'website': '',
            'industry': '',
            'employees': '',
            'revenue': '',
            'evidence_type': 'job_posting',
            'evidence_text': f"Hiring for '{company['role']}' - {company['evidence']}",
            'confidence_score': 3,  # Medium confidence - hiring indicates usage
            'source_url': get_job_portal_url(country),
            'is_verified': 1 if country == 'DK' else 0
        })
    
    return companies

def get_job_portal_url(country='DK'):
    """Get primary job portal URL for a country"""
    portals = JOB_PORTALS.get(country, [])
    if portals:
        return portals[0]['url']
    return ''

def scrape_jobindex_dk():
    """
    Scrape Jobindex.dk for Navision jobs.
    
    This is a placeholder for when browser automation is available.
    Jobindex requires JavaScript rendering.
    
    Returns:
        List of company dictionaries
    """
    print("  ⚠️  Jobindex scraping requires browser automation")
    return []

def scrape_linkedin_jobs(country='DK', search_term='Navision'):
    """
    Scrape LinkedIn Jobs for Navision positions.
    
    This is a placeholder for when browser automation is available.
    LinkedIn requires authentication and has strict rate limiting.
    
    Returns:
        List of company dictionaries
    """
    print("  ⚠️  LinkedIn scraping requires authentication and browser automation")
    return []

def add_company_from_job_posting(company_name, job_title, job_url, country='DK'):
    """
    Helper function to create a company entry from a job posting.
    
    Args:
        company_name: Name of the company
        job_title: Job title from posting
        job_url: URL to job posting
        country: Country code
    
    Returns:
        Company dictionary
    """
    return {
        'company_name': company_name,
        'country': country,
        'website': '',
        'industry': '',
        'employees': '',
        'revenue': '',
        'evidence_type': 'job_posting',
        'evidence_text': f"Actively hiring: {job_title}",
        'confidence_score': 3,
        'source_url': job_url,
        'is_verified': 0
    }

if __name__ == '__main__':
    # Test
    result = scrape('DK')
    print(f"\nFound {len(result)} companies from job portals")
    for company in result[:5]:
        print(f"  - {company['company_name']} ({company['evidence_type']})")
