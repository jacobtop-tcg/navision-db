#!/usr/bin/env python3
"""
MASSIVE AUTO-IMPORT - All TheirStack countries
"""

import sqlite3
from datetime import datetime

# All companies found from TheirStack web fetches
ALL_COMPANIES = {
    'DE': [
        {'name': 'Löwenstein Medical', 'industry': 'Pharmaceutical', 'employees': '430'},
        {'name': 'BayernInvest Kapitalverwaltungsgesellschaft mbH', 'industry': 'Financial Services', 'employees': '201'},
        {'name': 'Bechtle', 'industry': 'IT Services', 'employees': '10000'},
        {'name': 'Connamix GmbH & Co. KG', 'industry': 'IT Services', 'employees': '14'},
        {'name': 'anaptis GmbH', 'industry': 'IT Services', 'employees': '35'},
        {'name': 'Modepark Röther', 'industry': 'Retail', 'employees': '79'},
        {'name': 'TK Elevator', 'industry': 'Manufacturing', 'employees': '24000'},
        {'name': 'DIS AG', 'industry': 'HR Services', 'employees': '5000'},
        {'name': 'New Flag GmbH', 'industry': 'Manufacturing', 'employees': '215'},
        {'name': 'Marley Spoon', 'industry': 'Food & Beverage', 'employees': '1000'},
    ],
    'GB': [
        {'name': 'EY', 'industry': 'Professional Services', 'employees': '400000'},
        {'name': 'Rentokil Initial', 'industry': 'Environmental Services', 'employees': '12000'},
        {'name': 'HSBC', 'industry': 'Financial Services', 'employees': '195000'},
        {'name': 'Highlite', 'industry': 'Retail', 'employees': '8'},
        {'name': 'JTC Group', 'industry': 'Financial Services', 'employees': '2000'},
        {'name': 'Burgess Farms', 'industry': 'Food Manufacturing', 'employees': '501'},
        {'name': 'Selby Jennings', 'industry': 'Professional Services', 'employees': '994'},
        {'name': 'CDW UK', 'industry': 'IT Services', 'employees': '1300'},
        {'name': 'EnerMech', 'industry': 'Oil & Gas', 'employees': '2900'},
        {'name': 'PwC', 'industry': 'Professional Services', 'employees': '328000'},
    ],
    'NL': [
        {'name': 'IKEA', 'industry': 'Retail', 'employees': '94000'},
        {'name': 'Randstad', 'industry': 'HR Services', 'employees': '63000'},
        {'name': 'Bolder Group', 'industry': 'Financial Services', 'employees': '423'},
        {'name': 'The HEINEKEN Company', 'industry': 'Food & Beverage', 'employees': '43000'},
        {'name': 'Brand Masters BV', 'industry': 'Food & Beverage', 'employees': '110'},
        {'name': 'Koers', 'industry': 'Real Estate', 'employees': '84'},
        {'name': 'Nivel Groep', 'industry': 'Architecture', 'employees': '65'},
        {'name': 'Alphatron Marine', 'industry': 'Maritime', 'employees': '363'},
        {'name': 'Meraki', 'industry': 'Individual Services', 'employees': '2'},
        {'name': 'Feadship - Royal Dutch Shipyards', 'industry': 'Manufacturing', 'employees': '1000'},
    ],
    'BE': [
        {'name': 'BDO', 'industry': 'Accounting', 'employees': '62000'},
        {'name': 'Desotec', 'industry': 'Oil & Gas', 'employees': '201'},
        {'name': 'BESIX', 'industry': 'Construction', 'employees': '12000'},
        {'name': 'Beddeleem', 'industry': 'Construction', 'employees': '148'},
        {'name': 'Nikon Metrology', 'industry': 'Manufacturing', 'employees': '478'},
        {'name': 'Cegeka', 'industry': 'IT Services', 'employees': '5100'},
        {'name': 'Care BV', 'industry': 'Facilities Services', 'employees': '72'},
        {'name': 'Agrafresh', 'industry': 'Retail', 'employees': '47'},
        {'name': '9altitudes Belgium', 'industry': 'IT Services', 'employees': '132'},
        {'name': 'BESIX Unitec', 'industry': 'Construction', 'employees': '344'},
    ],
    'US': [
        {'name': 'State Street', 'industry': 'Financial Services', 'employees': '46000'},
        {'name': 'Citi', 'industry': 'Financial Services', 'employees': '200000'},
        {'name': 'BNY', 'industry': 'Financial Services', 'employees': '56000'},
        {'name': 'BNY Mellon', 'industry': 'Financial Services', 'employees': '54000'},
        {'name': 'JPMorgan Chase', 'industry': 'Financial Services', 'employees': '244000'},
        {'name': 'AMETEK', 'industry': 'Manufacturing', 'employees': '10000'},
        {'name': 'MUFG Investor Services', 'industry': 'Financial Services', 'employees': '2200'},
        {'name': 'LHH', 'industry': 'HR Services', 'employees': '24000'},
        {'name': 'Avanade', 'industry': 'IT Services', 'employees': '19000'},
        {'name': 'Morgan Stanley', 'industry': 'Financial Services', 'employees': '96000'},
    ],
}

# Connect to database
conn = sqlite3.connect('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')
cursor = conn.cursor()

inserted = 0
for country, companies in ALL_COMPANIES.items():
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

# Get count by country
cursor.execute('SELECT country, COUNT(*) FROM companies GROUP BY country ORDER BY COUNT(*) DESC')
by_country = cursor.fetchall()

conn.close()

print(f"✅ MASSIVE IMPORT COMPLETE!")
print(f"   Added {inserted} companies")
print(f"   Total: {total} companies")
print(f"\n📊 BY COUNTRY:")
for country, count in by_country:
    print(f"   {country}: {count}")
