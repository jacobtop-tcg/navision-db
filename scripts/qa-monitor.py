#!/usr/bin/env python3
"""
Navision Data Quality Monitor
==============================
Continuous QA monitoring for company data quality.

Usage:
    python3 scripts/qa-monitor.py --check      # One-time quality check
    python3 scripts/qa-monitor.py --cleanup    # Remove identified noise
    python3 scripts/qa-monitor.py --report     # Generate quality report
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
LOG_PATH = SCRIPT_DIR.parent / 'logs' / 'qa-audit.log'

# Quality rules - patterns that indicate NOISE
NOISE_PATTERNS = [
    # List articles / directories
    r'^best\s*\d*', r'^top\s*\d*', r'^\d+\s*best', r'near\s*me', r'directory',
    # Currency / calculators
    r'currency', r'converter', r'exchange\s*rate', r'valuta', r'usd\s*to', r'eur\s*to',
    r'calculator', r'omregner', r'rechner', r'speed\s*test',
    # Generic content
    r'^how\s+(to|long|much)', r'^what\s+is', r'^guide\s+to', r'tutorial', r'faq',
    r'vs\b', r'versus', r'comparison', r'review\b', r'horoscope', r'zodiac',
    # Reddit / forums
    r'^r/', r'reddit', r'forum', r'thread', r'discussion', r'comments',
    # Generic web services
    r'^maps\s', r'google\s+maps', r'yahoo\s+search', r'login\b', r'sign\s+in',
    r'qr\s+code', r'password', r'email\s+recovery',
    # Adult / inappropriate
    r'xxx', r'porn', r'casino', r'betting',
    # Time / timezone
    r'time\s+in', r'timezone', r'clock\s+', r'live\s*$',
    # Clothing / retail (often wrong)
    r'clothing\s+online', r'boutique\s+', r'damen\s+', r'herren\s+',
]

# Patterns that indicate REAL companies
COMPANY_PATTERNS = [
    r'(a/s|aps|ab|as|gmbh|ltd|llc|inc|corp|corporation)',
    r'(group|holding|industries|solutions|technologies|systems)',
    r'(services|consulting|consult|partners|international)',
    r'(manufacturing|logistics|transport|energy)',
    r'(danmark|norge|sverige|deutschland|netherlands)',
]

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def log_audit(message, company_id=None, action=None):
    """Log QA actions to audit file"""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    log_entry = f"[{timestamp}] {message}"
    if company_id:
        log_entry += f" (ID: {company_id})"
    if action:
        log_entry += f" [{action}]"
    
    print(log_entry)
    
    with open(LOG_PATH, 'a') as f:
        f.write(log_entry + '\n')

def is_noise(company_name):
    """Check if company name matches noise patterns"""
    name_lower = company_name.lower()
    
    # Check noise patterns
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return True, f"matches pattern: {pattern}"
    
    # Check if starts with number
    if company_name[0].isdigit():
        return True, "starts with number"
    
    # Check if too short (likely generic term)
    if len(company_name) < 4 and ' ' not in company_name:
        return True, "too short"
    
    return False, None

def is_valid_company(company_name):
    """Check if company name looks like a real company"""
    name_lower = company_name.lower()
    
    # Must have at least one company indicator
    for pattern in COMPANY_PATTERNS:
        if re.search(pattern, name_lower):
            return True, f"has company pattern: {pattern}"
    
    # Or must be longer and not match noise
    if len(company_name) > 8:
        is_noisy, reason = is_noise(company_name)
        if not is_noisy:
            return True, "long name, no noise patterns"
    
    return False, "no company indicators"

def check_quality(sample_size=500):
    """Check quality of recent companies"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check last N companies
    cursor.execute('''
        SELECT id, company_name, country, source, confidence_score, created_at
        FROM companies
        ORDER BY created_at DESC
        LIMIT ?
    ''', (sample_size,))
    
    companies = cursor.fetchall()
    
    results = {
        'total': len(companies),
        'valid': 0,
        'noise': 0,
        'uncertain': 0,
        'noise_details': [],
        'by_source': {},
        'by_country': {},
    }
    
    for company in companies:
        name = company['company_name']
        source = company['source']
        country = company['country']
        
        # Track by source
        if source not in results['by_source']:
            results['by_source'][source] = {'valid': 0, 'noise': 0}
        
        # Track by country
        if country not in results['by_country']:
            results['by_country'][country] = {'valid': 0, 'noise': 0}
        
        # Check if noise
        is_noisy, reason = is_noise(name)
        
        if is_noisy:
            results['noise'] += 1
            results['by_source'][source]['noise'] += 1
            results['by_country'][country]['noise'] += 1
            results['noise_details'].append({
                'id': company['id'],
                'name': name,
                'country': country,
                'source': source,
                'reason': reason,
            })
        else:
            # Check if valid company
            is_valid, valid_reason = is_valid_company(name)
            if is_valid:
                results['valid'] += 1
                results['by_source'][source]['valid'] += 1
                results['by_country'][country]['valid'] += 1
            else:
                results['uncertain'] += 1
    
    conn.close()
    return results

def cleanup_noise(dry_run=True, limit=500):
    """Mark or remove noise companies"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent companies (most likely to have noise)
    cursor.execute('''
        SELECT id, company_name, country, source, confidence_score, created_at
        FROM companies
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    companies = cursor.fetchall()
    removed = 0
    marked = 0
    
    for company in companies:
        is_noisy, reason = is_noise(company['company_name'])
        
        if is_noisy:
            if dry_run:
                print(f"  WOULD REMOVE: {company['company_name']} ({company['country']}) - {reason}")
                removed += 1
            else:
                # Delete noise
                cursor.execute('DELETE FROM companies WHERE id = ?', (company['id'],))
                log_audit(f"Removed noise: {company['company_name']}", company['id'], 'DELETE')
                removed += 1
        elif company['confidence_score'] < 3:
            if dry_run:
                print(f"  WOULD MARK: {company['company_name']} ({company['country']}) - low confidence")
                marked += 1
            else:
                # Mark for review
                cursor.execute('''
                    UPDATE companies 
                    SET confidence_score = 1, updated_at = ?
                    WHERE id = ?
                ''', (datetime.utcnow().isoformat() + 'Z', company['id']))
                log_audit(f"Marked for review: {company['company_name']}", company['id'], 'MARK')
                marked += 1
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    return removed, marked

def generate_report():
    """Generate quality report"""
    results = check_quality(500)
    
    quality_pct = (results['valid'] / results['total'] * 100) if results['total'] > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 NAVISION DATA QUALITY REPORT")
    print("=" * 70)
    print(f"Sample size: {results['total']} companies (most recent)")
    print(f"Quality score: {quality_pct:.1f}% valid")
    print(f"  ✅ Valid: {results['valid']}")
    print(f"  ❌ Noise: {results['noise']}")
    print(f"  ❓ Uncertain: {results['uncertain']}")
    
    print("\n📈 BY SOURCE:")
    for source, stats in sorted(results['by_source'].items(), key=lambda x: -(x[1]['valid'] + x[1]['noise'])):
        total = stats['valid'] + stats['noise']
        if total > 0:
            pct = stats['valid'] / total * 100
            print(f"  {source:25} → {pct:5.1f}% valid ({stats['valid']}/{total})")
    
    print("\n🌍 BY COUNTRY:")
    for country, stats in sorted(results['by_country'].items(), key=lambda x: -(x[1]['valid'] + x[1]['noise']))[:15]:
        total = stats['valid'] + stats['noise']
        if total > 0:
            pct = stats['valid'] / total * 100
            print(f"  {country:4} → {pct:5.1f}% valid ({stats['valid']}/{total})")
    
    if results['noise_details']:
        print("\n❌ TOP NOISE EXAMPLES:")
        for item in results['noise_details'][:15]:
            print(f"  • {item['name'][:50]} ({item['country']}) - {item['reason']}")
    
    print("\n" + "=" * 70)
    
    # Alert if quality is low
    if quality_pct < 80:
        print("⚠️  ALERT: Quality below 80%! Review needed.")
    elif quality_pct < 90:
        print("⚠️  WARNING: Quality below 90%. Consider improvements.")
    else:
        print("✅ Quality is GOOD (>90%)")
    
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='QA Monitor for Navision Database')
    parser.add_argument('--check', action='store_true', help='Run quality check')
    parser.add_argument('--cleanup', action='store_true', help='Remove noise (use --dry-run first)')
    parser.add_argument('--report', action='store_true', help='Generate quality report')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed')
    
    args = parser.parse_args()
    
    if args.report or args.check:
        generate_report()
    
    if args.cleanup:
        print(f"\n🧹 CLEANUP {'(DRY RUN)' if args.dry_run else '(LIVE)'}:")
        removed, marked = cleanup_noise(dry_run=args.dry_run)
        print(f"\n{'Would remove' if args.dry_run else 'Removed'}: {removed} companies")
        print(f"{'Would mark' if args.dry_run else 'Marked'}: {marked} companies")
    
    if not any([args.check, args.cleanup, args.report]):
        # Default: quick check
        print("🔍 Quick quality check (last 100 companies):")
        results = check_quality(100)
        quality_pct = (results['valid'] / results['total'] * 100) if results['total'] > 0 else 0
        print(f"Quality: {quality_pct:.1f}% | Valid: {results['valid']} | Noise: {results['noise']}")
        
        if results['noise'] > 20:
            print("⚠️  High noise rate! Run --report for details.")
