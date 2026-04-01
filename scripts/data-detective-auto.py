#!/usr/bin/env python3
"""
DATA DETECTIVE - Auto-Creative Source Explorer
===============================================
Kører automatisk eksperimenter med nye kilder og lærer hvad der virker.

Arkitektur:
1. CORE SOURCES - Altid kørende (TheirStack, jobs, etc.)
2. EXPERIMENT LAB - Roterende tests af nye kilder
3. AUTO-LEARNING - Måler succes, dropper dårlige, skalerer gode
4. CONTINUOUS IMPROVEMENT - Nye queries hver uge

Usage:
    python3 data-detective-auto.py --auto  # Kør som daemon
    python3 data-detective-auto.py --experiment  # Kør ét eksperiment
    python3 data-detective-auto.py --status  # Vis status
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

DB_PATH = Path(__file__).parent.parent / 'database' / 'navision-global.db'
STATE_DIR = Path(__file__).parent.parent / 'state'
EXPERIMENT_LOG = STATE_DIR / 'detective-experiments.json'
METRICS_FILE = STATE_DIR / 'detective-metrics.json'

# CORE SOURCES - Altid kørende
CORE_SOURCES = [
    {'name': 'theirstack', 'priority': 1, 'repeat': True},
    {'name': 'global_jobs', 'priority': 2, 'repeat': True},
    {'name': 'case_studies', 'priority': 3, 'repeat': True},
]

# EXPERIMENT LAB - Kilder der testes
EXPERIMENT_QUEUE = [
    {
        'id': 'exp_001',
        'name': 'github_c/al_repos',
        'description': 'Find GitHub repos med C/AL eller NAV kode',
        'query_template': 'site:github.com "C/AL" OR "Dynamics NAV" OR "Navision" {country}',
        'status': 'pending',  # pending, running, completed, failed
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
    {
        'id': 'exp_002',
        'name': 'conference_attendees',
        'description': 'NAV/BC konference deltagerlister',
        'query_template': 'NAVUG Summit attendees OR "Business Central" conference participants OR "Dynamics NAV" workshop {country}',
        'status': 'pending',
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
    {
        'id': 'exp_003',
        'name': 'public_procurement',
        'description': 'Offentlige udbud med Navision',
        'query_template': 'site:udbud.dk OR site:ted.europa.eu "Navision" OR "Dynamics NAV" {country}',
        'status': 'pending',
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
    {
        'id': 'exp_004',
        'name': 'isv_customers',
        'description': 'ISV partner kunder (Continia, Jet Reports, etc.)',
        'query_template': '"Continia" customer OR "Jet Reports" customer OR "autoinvoice" Navision {country}',
        'status': 'pending',
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
    {
        'id': 'exp_005',
        'name': 'annual_reports',
        'description': 'Årsrapporter der nævner NAV ERP',
        'query_template': 'site:cvr.dk OR site:virksomhed.dk "Microsoft Dynamics NAV" OR "Navision" årsrapport {country}',
        'status': 'pending',
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
    {
        'id': 'exp_006',
        'name': 'stackoverflow_nav',
        'description': 'StackOverflow NAV spørgsmål (virksomhedsdomæner)',
        'query_template': 'site:stackoverflow.com "Dynamics NAV" OR "Navision" OR "C/AL"',
        'status': 'pending',
        'success_rate': 0.0,
        'companies_found': 0,
        'last_run': None,
        'runs': 0,
    },
]

def load_state():
    """Load experiment state"""
    if EXPERIMENT_LOG.exists():
        with open(EXPERIMENT_LOG) as f:
            return json.load(f)
    return {'experiments': EXPERIMENT_QUEUE, 'last_updated': datetime.utcnow().isoformat() + 'Z'}

def save_state(state):
    """Save experiment state"""
    state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    with open(EXPERIMENT_LOG, 'w') as f:
        json.dump(state, f, indent=2)

def load_metrics():
    """Load success metrics"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {
        'sources': {},
        'weekly_experiments': 0,
        'total_experiments': 0,
        'successful_experiments': 0,
        'failed_experiments': 0,
    }

def save_metrics(metrics):
    """Save metrics"""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def run_experiment(experiment: Dict, country: str = 'DK') -> Dict:
    """
    Kør ét eksperiment og returner resultat
    """
    print(f"  🧪 EKSPERIMENT: {experiment['name']}")
    print(f"     {experiment['description']}")
    
    # Her ville vi kalde SearXNG med query_template
    # For nu simulerer vi resultatet
    
    result = {
        'experiment_id': experiment['id'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'country': country,
        'companies_found': random.randint(0, 50),  # SIMULERET - skal erstattes med rigtig scraping
        'cdqo_approved': 0,
        'success': False,
        'notes': '',
    }
    
    # Simuler CDQO godkendelse rate
    if result['companies_found'] > 10:
        result['cdqo_approved'] = int(result['companies_found'] * random.uniform(0.1, 0.6))
        result['success'] = result['cdqo_approved'] >= 5
        result['notes'] = f"{result['cdqo_approved']}/{result['companies_found']} godkendt af CDQO"
    else:
        result['notes'] = 'For få resultater'
    
    print(f"     Resultat: {result['companies_found']} fundet, {result['cdqo_approved']} godkendt")
    print(f"     Success: {result['success']}")
    
    return result

def select_next_experiment(state: Dict) -> Optional[Dict]:
    """
    Vælg næste eksperiment baseret på:
    - Pending eksperimenter først
    - Derefter eksperimenter med høj success rate
    - Undgå eksperimenter der kørte for nylig (< 7 dage)
    """
    experiments = state.get('experiments', [])
    
    # Find pending eksperimenter
    pending = [e for e in experiments if e['status'] == 'pending']
    if pending:
        return random.choice(pending)
    
    # Find eksperimenter der ikke er kørt for nylig
    now = datetime.utcnow()
    eligible = []
    for e in experiments:
        if e['status'] in ['completed', 'failed']:
            last_run = e.get('last_run')
            if last_run:
                last_run_dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                if (now - last_run_dt).days >= 7:
                    eligible.append(e)
            else:
                eligible.append(e)
    
    if eligible:
        # Vælg baseret på success rate
        eligible.sort(key=lambda x: x.get('success_rate', 0), reverse=True)
        return eligible[0]
    
    return None

def update_experiment_state(state: Dict, experiment_id: str, result: Dict):
    """Opdater eksperiment state med resultat"""
    for exp in state['experiments']:
        if exp['id'] == experiment_id:
            exp['last_run'] = result['timestamp']
            exp['runs'] = exp.get('runs', 0) + 1
            exp['companies_found'] = exp.get('companies_found', 0) + result['companies_found']
            
            # Opdater success rate (gennemsnit)
            if result['success']:
                exp['success_rate'] = (exp['success_rate'] * (exp['runs'] - 1) + 1) / exp['runs']
            else:
                exp['success_rate'] = (exp['success_rate'] * (exp['runs'] - 1)) / exp['runs']
            
            # Opdater status
            if exp['runs'] >= 3:
                if exp['success_rate'] >= 0.5:
                    exp['status'] = 'promoted'  # Ryk til core sources
                elif exp['success_rate'] <= 0.1:
                    exp['status'] = 'dropped'  # Drop denne kilde
                else:
                    exp['status'] = 'active'  # Fortsæt eksperimenter
            
            break
    
    return state

def main():
    """Main loop"""
    print("=" * 80)
    print("🕵️ DATA DETECTIVE - AUTO-CREATIVE")
    print("=" * 80)
    
    state = load_state()
    metrics = load_metrics()
    
    # Vælg næste eksperiment
    experiment = select_next_experiment(state)
    
    if not experiment:
        print("✅ Alle eksperimenter kørt eller venter på gen-test")
        print("💡 Tilføj nye eksperimenter til queue")
        return
    
    # Kør eksperiment
    result = run_experiment(experiment, country='DK')
    
    # Opdater state
    state = update_experiment_state(state, experiment['id'], result)
    
    # Opdater metrics
    metrics['total_experiments'] = metrics.get('total_experiments', 0) + 1
    if result['success']:
        metrics['successful_experiments'] = metrics.get('successful_experiments', 0) + 1
    else:
        metrics['failed_experiments'] = metrics.get('failed_experiments', 0) + 1
    
    # Gem
    save_state(state)
    save_metrics(metrics)
    
    print("\n" + "=" * 80)
    print("📊 STATUS:")
    print(f"   Totale eksperimenter: {metrics['total_experiments']}")
    print(f"   Succes: {metrics['successful_experiments']}")
    print(f"   Fejlet: {metrics['failed_experiments']}")
    print("=" * 80)

if __name__ == '__main__':
    main()
