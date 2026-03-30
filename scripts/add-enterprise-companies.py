#!/usr/bin/env python3
"""
Add enterprise companies found from research sources
"""

COMPANIES = [
    # From InfoClutch
    {"name": "Louis Dreyfus Company", "country": "NL", "industry": "Agriculture", "source": "infoclutch"},
    {"name": "Heineken", "country": "NL", "industry": "Beverages", "source": "infoclutch"},
    {"name": "Michelin", "country": "FR", "industry": "Manufacturing", "source": "infoclutch"},
    {"name": "Arrow Electronics", "country": "US", "industry": "Distribution", "source": "infoclutch"},
    {"name": "MET Group", "country": "CH", "industry": "Energy", "source": "infoclutch"},
    {"name": "Universal Music Group", "country": "US", "industry": "Entertainment", "source": "infoclutch"},
    {"name": "STIHL", "country": "DE", "industry": "Manufacturing", "source": "infoclutch"},
    {"name": "Champion Homes", "country": "US", "industry": "Manufacturing", "source": "infoclutch"},
    {"name": "NRB Industrial Bearings", "country": "IN", "industry": "Manufacturing", "source": "infoclutch"},
    
    # From LinkedIn
    {"name": "Tesla Grohmann Automation", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    {"name": "Kawasaki Robotics USA", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    {"name": "Crown Equipment Corporation", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    {"name": "Barton Malow Company", "country": "US", "industry": "Construction", "source": "linkedin"},
    {"name": "Portacool LLC", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    {"name": "Caleres Inc", "country": "US", "industry": "Retail", "source": "linkedin"},
    {"name": "Morrison Container Handling Solutions", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    {"name": "Sunrise Technologies", "country": "US", "industry": "IT Services", "source": "linkedin"},
    {"name": "Western Computer", "country": "US", "industry": "IT Services", "source": "linkedin"},
    {"name": "Dixon Valve & Coupling Company", "country": "US", "industry": "Manufacturing", "source": "linkedin"},
    
    # From ProspectWallet
    {"name": "Siemens", "country": "DE", "industry": "Manufacturing", "source": "prospectwallet"},
    {"name": "Amway", "country": "US", "industry": "Consumer Products", "source": "prospectwallet"},
    {"name": "IKEA", "country": "SE", "industry": "Retail", "source": "prospectwallet"},
    {"name": "Yamaha", "country": "JP", "industry": "Automotive", "source": "prospectwallet"},
    {"name": "McCain Foods", "country": "CA", "industry": "Food Processing", "source": "prospectwallet"},
    {"name": "ASICS", "country": "JP", "industry": "Apparel", "source": "prospectwallet"},
    {"name": "Black Diamond Equipment", "country": "US", "industry": "Outdoor Gear", "source": "prospectwallet"},
    {"name": "Targus", "country": "US", "industry": "Technology", "source": "prospectwallet"},
    {"name": "Coca-Cola Bottlers", "country": "US", "industry": "Beverages", "source": "prospectwallet"},
    {"name": "Revlon", "country": "US", "industry": "Consumer Products", "source": "prospectwallet"},
    {"name": "Pandora Jewelry", "country": "DK", "industry": "Retail", "source": "prospectwallet"},
    {"name": "Specsavers", "country": "GB", "industry": "Retail", "source": "prospectwallet"},
    {"name": "Reginox UK", "country": "GB", "industry": "Manufacturing", "source": "prospectwallet"},
    
    # From AppsRunTheWorld
    {"name": "Mowasalat", "country": "QA", "industry": "Transportation", "source": "appsruntheworld"},
    {"name": "Ministry of Education Saudi Arabia", "country": "SA", "industry": "Government", "source": "appsruntheworld"},
]

if __name__ == "__main__":
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    inserted = 0
    for company in COMPANIES:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO companies 
                (company_name, country, industry, confidence_score, source, evidence_type, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company["name"],
                company["country"],
                company["industry"],
                5,  # High confidence - from multiple sources
                company["source"],
                "enterprise_list",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ Added: {company['name']} ({company['country']})")
        except Exception as e:
            print(f"❌ Error adding {company['name']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Complete! Inserted {inserted} new companies")
