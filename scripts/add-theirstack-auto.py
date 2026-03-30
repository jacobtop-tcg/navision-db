#!/usr/bin/env python3
"""
Auto-add TheirStack companies from web search results
"""

import sqlite3
from datetime import datetime

# Companies found from TheirStack web fetches
NEW_COMPANIES = {
    'NO': [
        {'name': 'DeepOcean', 'industry': 'Oil and Gas', 'employees': '1700'},
        {'name': 'Nav Oslo', 'industry': 'Government', 'employees': '212'},
        {'name': 'Oslo kommune', 'industry': 'Government', 'employees': '7500'},
        {'name': 'Tysvær kommune', 'industry': 'Government', 'employees': '255'},
        {'name': 'Bergen Kommune', 'industry': 'Government', 'employees': '16000'},
        {'name': 'Akershus Universitetssykehus', 'industry': 'Healthcare', 'employees': '9500'},
        {'name': 'Universitetssykehuset Nord-Norge', 'industry': 'Healthcare', 'employees': '839'},
        {'name': 'Helse Sør-Øst RHF', 'industry': 'Healthcare', 'employees': '23000'},
        {'name': 'Kirkens Bymisjon', 'industry': 'Non-profit', 'employees': '888'},
        {'name': 'Kristiansand kommune', 'industry': 'Government', 'employees': '2200'},
    ],
    'SE': [
        {'name': 'Intrum', 'industry': 'Financial Services', 'employees': '6500'},
        {'name': 'AddSecure', 'industry': 'IT Services', 'employees': '1000'},
        {'name': 'Anticimex', 'industry': 'Consumer Services', 'employees': '10000'},
        {'name': 'Grundéns', 'industry': 'Retail', 'employees': '65'},
        {'name': 'Sidec', 'industry': 'Research', 'employees': '93'},
        {'name': 'Hem', 'industry': 'Retail Furniture', 'employees': '177'},
        {'name': 'Region Västmanland', 'industry': 'Government', 'employees': '3600'},
        {'name': 'BHG Group', 'industry': 'Retail', 'employees': '161'},
        {'name': 'Hedin IT', 'industry': 'IT Services', 'employees': ''},
        {'name': 'Witre Manutan Sverige', 'industry': 'Retail', 'employees': '64'},
    ],
    'FI': [
        {'name': 'Greenstep', 'industry': 'Financial Services', 'employees': '723'},
        {'name': 'Tietoevry', 'industry': 'IT Services', 'employees': '15000'},
        {'name': 'Innofactor', 'industry': 'Software', 'employees': '531'},
        {'name': 'iLOQ', 'industry': 'Security', 'employees': '324'},
        {'name': 'YIT', 'industry': 'Construction', 'employees': '2800'},
        {'name': 'Rovio', 'industry': 'Gaming', 'employees': '610'},
        {'name': 'Teleste', 'industry': 'Telecommunications', 'employees': '526'},
        {'name': 'Delipap', 'industry': 'Manufacturing', 'employees': '40'},
        {'name': 'Temet', 'industry': 'Defense', 'employees': '62'},
    ],
}

# Connect to database
conn = sqlite3.connect('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')
cursor = conn.cursor()

inserted = 0
for country, companies in NEW_COMPANIES.items():
    for company in companies:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (company_name, country, industry, employees, evidence_type, evidence_text, 
             confidence_score, source, source_url, discovered_at, updated_at, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['name'],
                country,
                company.get('industry', ''),
                company.get('employees', ''),
                'theirstack',
                f'TheirStack technology detection - {company.get("employees", "")} employees',
                4,
                'TheirStack',
                f'https://theirstack.com/en/technology/navision/{country.lower()}',
                datetime.utcnow().isoformat() + 'Z',
                datetime.utcnow().isoformat() + 'Z',
                0
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"Error inserting {company['name']}: {e}")

conn.commit()

# Get new total
cursor.execute('SELECT COUNT(*) FROM companies')
total = cursor.fetchone()[0]

conn.close()

print(f"✅ Added {inserted} companies from TheirStack")
print(f"📊 Total companies: {total}")
