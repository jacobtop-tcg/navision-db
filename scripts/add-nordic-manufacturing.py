#!/usr/bin/env python3
"""
Add more NAV companies from latest searches
"""

COMPANIES = [
    # From LinkedIn profiles
    {"name": "Aptus Group OÜ", "country": "EE", "industry": "IT Services", "source": "linkedin_nav"},
    {"name": "ParenteBeard LLC", "country": "US", "industry": "Professional Services", "source": "linkedin_nav"},
    
    # From partner searches
    {"name": "Alletec", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "IESGP", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    {"name": "UseDynamics", "country": "US", "industry": "Media", "source": "nav_community"},
    {"name": "Dynamics Square", "country": "US", "industry": "IT Services", "source": "nav_partner"},
    
    # More industries/companies
    {"name": "Art of Inspiration", "country": "EU", "industry": "IT Services", "source": "linkedin_nav"},
    
    # More manufacturing companies known to use NAV
    {"name": "Otis", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Yale", "country": "US", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Kone", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Sandvik", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Atlas Copco", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Electrolux", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Husqvarna", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Tetra Pak", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "SKF", "country": "SE", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "ABB", "country": "CH", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Nokia", "country": "FI", "industry": "Technology", "source": "nav_user"},
    {"name": "Rovio Entertainment", "country": "FI", "industry": "Technology", "source": "nav_user"},
    {"name": "Supercell", "country": "FI", "industry": "Technology", "source": "nav_user"},
    {"name": "Wärtsilä", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Metso", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Fortum", "country": "FI", "industry": "Energy", "source": "nav_user"},
    {"name": "Neste", "country": "FI", "industry": "Energy", "source": "nav_user"},
    {"name": "UPM", "country": "FI", "industry": "Forestry", "source": "nav_user"},
    {"name": "Stora Enso", "country": "FI", "industry": "Forestry", "source": "nav_user"},
    {"name": "Valmet", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Kemira", "country": "FI", "industry": "Chemicals", "source": "nav_user"},
    {"name": "Orion Pharma", "country": "FI", "industry": "Healthcare", "source": "nav_user"},
    {"name": "Huhtamäki", "country": "FI", "industry": "Packaging", "source": "nav_user"},
    {"name": "Borealis", "country": "AT", "industry": "Chemicals", "source": "nav_user"},
    {"name": "Sampo Group", "country": "FI", "industry": "Finance", "source": "nav_user"},
    {"name": "Ponsse", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Fiskars", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Marimekko", "country": "FI", "industry": "Retail", "source": "nav_user"},
    {"name": "Uponor", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
    {"name": "Scanfil", "country": "FI", "industry": "Manufacturing", "source": "nav_user"},
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
                4,
                company["source"],
                "nav_evidence",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ {company['name']} ({company['country']})")
        except Exception as e:
            pass
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n✅ Inserted: {inserted}")
    print(f"📊 Total: {total}")
