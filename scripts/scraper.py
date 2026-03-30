#!/usr/bin/env python3
"""
Navision Global Database - Main Scraper
========================================
Automated scraper for finding companies using Microsoft Navision/Dynamics 365 Business Central.

Usage:
    python3 scraper.py --auto          # Run all pending sources
    python3 scraper.py --source theirstack --country NO  # Run specific source
    python3 scraper.py --status        # Show current status

This script is designed to:
- Survive session resets (state is persisted to files)
- Run automatically via cron/heartbeat
- Be extensible with new sources and countries
- Maintain a single source of truth (navision-global.db)
"""

import argparse
import json
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
NAVISION_DB = SCRIPT_DIR.parent  # navision-db folder
DB_PATH = NAVISION_DB / 'database' / 'navision-global.db'
STATE_DIR = NAVISION_DB / 'state'
CONFIG_DIR = NAVISION_DB / 'config'

def load_config():
    """Load configuration files"""
    config = {
        'sources': {},
        'countries': [],
        'rate_limits': {}
    }
    
    # Load sources config
    sources_file = CONFIG_DIR / 'sources.json'
    if sources_file.exists():
        with open(sources_file) as f:
            config['sources'] = json.load(f)
    
    # Load countries config
    countries_file = CONFIG_DIR / 'countries.json'
    if countries_file.exists():
        with open(countries_file) as f:
            config['countries'] = json.load(f)
    
    # Load rate limits
    rate_limits_file = CONFIG_DIR / 'rate-limits.json'
    if rate_limits_file.exists():
        with open(rate_limits_file) as f:
            config['rate_limits'] = json.load(f)
    
    return config

def load_state():
    """Load current state"""
    state = {
        'last_run': None,
        'total_companies': 0,
        'countries_processed': [],
        'sources_processed': [],
        'queue': [],
        'errors': []
    }
    
    progress_file = STATE_DIR / 'progress.json'
    if progress_file.exists():
        with open(progress_file) as f:
            state.update(json.load(f))
    
    return state

def save_state(state):
    """Save current state"""
    state['last_run'] = datetime.utcnow().isoformat() + 'Z'
    
    with open(STATE_DIR / 'progress.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    # Update last-run timestamp
    with open(STATE_DIR / 'last-run.txt', 'w') as f:
        f.write(state['last_run'])

def log_error(error_msg, source=None, country=None):
    """Log an error to state"""
    state = load_state()
    error_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'source': source,
        'country': country,
        'error': error_msg
    }
    state['errors'].append(error_entry)
    
    # Keep only last 100 errors
    state['errors'] = state['errors'][-100:]
    
    save_state(state)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def save_companies(companies, source, country):
    """Save companies to database"""
    if not companies:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted = 0
    for company in companies:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (company_name, country, website, industry, employees, revenue,
             evidence_type, evidence_text, confidence_score, source, source_url,
             discovered_at, updated_at, is_verified, headquarters_address, linkedin_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('company_name', ''),
                company.get('country', country),
                company.get('website', ''),
                company.get('industry', ''),
                company.get('employees', ''),
                company.get('revenue', ''),
                company.get('evidence_type', ''),
                company.get('evidence_text', ''),
                company.get('confidence_score', 3),
                source,
                company.get('source_url', ''),
                datetime.utcnow().isoformat() + 'Z',
                datetime.utcnow().isoformat() + 'Z',
                company.get('is_verified', 0),
                company.get('headquarters_address', ''),
                company.get('linkedin_url', '')
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            log_error(f"Failed to insert {company.get('company_name', 'Unknown')}: {e}", source, country)
    
    # Update source stats
    cursor.execute('''
    INSERT OR REPLACE INTO sources (source_name, country, total_companies, last_scraped, is_active)
    VALUES (?, ?, ?, ?, TRUE)
    ''', (source, country, inserted, datetime.utcnow().isoformat() + 'Z'))
    
    conn.commit()
    conn.close()
    
    return inserted

def run_scraper(source_name, country):
    """Run a specific scraper source"""
    print(f"🕷️  Running scraper: {source_name} for {country}")
    
    # Add scripts directory to path for imports
    scripts_path = str(SCRIPT_DIR)
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    # Import the specific scraper module
    try:
        scraper_module = __import__(f'sources.{source_name}', fromlist=['scrape'])
        scrape_func = getattr(scraper_module, 'scrape')
        
        companies = scrape_func(country)
        inserted = save_companies(companies, source_name, country)
        
        print(f"✅ {source_name}/{country}: Found {len(companies)} companies, inserted {inserted} new")
        return inserted
        
    except ImportError as e:
        error_msg = f"Scraper module not found: sources.{source_name} - {e}"
        print(f"❌ {error_msg}")
        log_error(error_msg, source_name, country)
        return 0
    except Exception as e:
        error_msg = f"Scraper failed: {str(e)}"
        print(f"❌ {error_msg}")
        log_error(error_msg, source_name, country)
        return 0

def check_searxng_health():
    """
    Check if SearXNG is available before running scrapers.
    
    Returns:
        bool: True if healthy, False if should skip
    """
    health_script = SCRIPT_DIR / 'searxng_health.py'
    if not health_script.exists():
        print("⚠️  Health check script not found, proceeding anyway")
        return True
    
    try:
        import subprocess
        result = subprocess.run(
            ['python3', str(health_script), '--check', '--json'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            health = json.loads(result.stdout)
            if health.get('healthy'):
                engines = health.get('engines_working', health.get('engines_status', {}).get('working_engines', '?'))
                results = health.get('results_count', '?')
                print(f"✅ SearXNG healthy ({engines} engines, {results} results)")
                return True
            else:
                print(f"⚠️  SearXNG not healthy: {health.get('reason', 'unknown')}")
                return False
        else:
            # Health check failed - parse error
            try:
                health = json.loads(result.stdout)
                reason = health.get('reason', 'unknown')
                wait_minutes = health.get('wait_minutes', 0)
                if reason == 'backoff' or reason == 'rate_limited':
                    print(f"⏸️  SearXNG rate limited - waiting {wait_minutes} min")
                    return False
                elif reason == 'error':
                    print(f"⚠️  SearXNG error: {health.get('error', 'unknown')}")
                    return False
            except:
                pass
            print("⚠️  Health check failed, proceeding with caution")
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Health check timeout")
        return True
    except Exception as e:
        print(f"⚠️  Health check error: {e}")
        return True

def run_all_pending():
    """Run all pending scrapers from queue"""
    state = load_state()
    config = load_config()
    
    queue_file = STATE_DIR / 'queue.json'
    if not queue_file.exists():
        print("⚠️  No queue file found. Run with --init first.")
        return
    
    with open(queue_file) as f:
        queue = json.load(f)
    
    pending = queue.get('pending_sources', [])
    completed = queue.get('completed_sources', [])
    
    print(f"📋 Queue: {len(pending)} pending, {len(completed)} completed")
    
    # Check SearXNG health before starting
    searxng_healthy = check_searxng_health()
    if not searxng_healthy:
        print("⏸️  Skipping scrapers - SearXNG not available")
        print("💡 Scrapers will retry on next run")
        return
    
    total_inserted = 0
    new_pending = []
    for item in pending:
        source = item.get('source')
        countries = item.get('countries', ['DK'])
        repeat = item.get('repeat', False)  # Check if source should repeat
        
        for country in countries:
            inserted = run_scraper(source, country)
            total_inserted += inserted
        
        # Only move to completed if NOT repeating
        if not repeat:
            if source not in completed:
                completed.append(source)
        else:
            # Keep in pending for continuous scraping
            new_pending.append(item)
    
    # Update queue - keep repeating sources in pending!
    queue['pending_sources'] = new_pending
    queue['completed_sources'] = completed
    
    with open(queue_file, 'w') as f:
        json.dump(queue, f, indent=2)
    
    # Update state
    state['sources_processed'] = completed
    state['total_companies'] = get_db_connection().execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    save_state(state)
    
    print(f"\n✅ Complete! Total inserted: {total_inserted}")
    print(f"📊 Database now has {state['total_companies']} companies")

def show_status():
    """Show current status"""
    state = load_state()
    
    print("📊 NAVISION GLOBAL DATABASE - STATUS")
    print("=" * 50)
    print(f"Last run: {state.get('last_run', 'Never')}")
    
    # Get actual count from database
    if DB_PATH.exists():
        conn = get_db_connection()
        actual_count = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
        conn.close()
        print(f"Total companies: {actual_count}")
    else:
        print(f"Total companies: {state.get('total_companies', 0)}")
    
    print(f"Countries processed: {', '.join(state.get('countries_processed', []))}")
    print(f"Sources processed: {', '.join(state.get('sources_processed', []))}")
    
    if state.get('errors'):
        print(f"\n⚠️  Recent errors ({len(state['errors'])}):")
        for error in state['errors'][-5:]:
            print(f"  - {error.get('timestamp')}: {error.get('error')}")
    
    # Database stats
    if DB_PATH.exists():
        conn = get_db_connection()
        
        print(f"\n📈 DATABASE STATS:")
        
        # By country
        cursor = conn.execute('SELECT country, COUNT(*) FROM companies GROUP BY country ORDER BY COUNT(*) DESC')
        print("  By country:")
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        # By source
        cursor = conn.execute('SELECT source, COUNT(*) FROM companies GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10')
        print("  Top sources:")
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        # By confidence
        cursor = conn.execute('SELECT confidence_score, COUNT(*) FROM companies GROUP BY confidence_score ORDER BY confidence_score DESC')
        print("  By confidence:")
        for row in cursor.fetchall():
            stars = '⭐' * row[0]
            print(f"    {stars} ({row[0]}): {row[1]}")
        
        conn.close()

def init_queue():
    """Initialize the scraper queue"""
    queue = {
        'pending_sources': [
            {'source': 'theirstack', 'countries': ['NO', 'SE', 'FI', 'DE', 'UK', 'NL', 'BE'], 'priority': 1},
            {'source': 'jobportals', 'countries': ['DK', 'NO', 'SE', 'FI', 'DE', 'UK'], 'priority': 2},
            {'source': 'partners', 'countries': ['DK', 'NO', 'SE', 'FI', 'DE', 'UK', 'NL', 'BE'], 'priority': 3},
            {'source': 'linkedin_companies', 'countries': ['DK', 'NO', 'SE', 'FI', 'DE', 'UK'], 'priority': 4},
            {'source': 'press_releases', 'countries': ['DK', 'NO', 'SE', 'FI', 'DE', 'UK'], 'priority': 5},
        ],
        'completed_sources': ['navision-sandheden-db']
    }
    
    with open(STATE_DIR / 'queue.json', 'w') as f:
        json.dump(queue, f, indent=2)
    
    print("✅ Queue initialized")

def main():
    parser = argparse.ArgumentParser(description='Navision Global Database Scraper')
    parser.add_argument('--auto', action='store_true', help='Run all pending sources')
    parser.add_argument('--source', type=str, help='Run specific source')
    parser.add_argument('--country', type=str, default='DK', help='Country code (default: DK)')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--init', action='store_true', help='Initialize queue')
    
    args = parser.parse_args()
    
    if args.init:
        init_queue()
        return
    
    if args.status:
        show_status()
        return
    
    if args.auto:
        run_all_pending()
        return
    
    if args.source:
        run_scraper(args.source, args.country)
        return
    
    # Default: show status
    show_status()

if __name__ == '__main__':
    main()
