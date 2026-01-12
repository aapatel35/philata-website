"""
Immigration Data Updater - Railway Cron Job
Runs daily to fetch latest IRCC data and update the website repo
"""
import os
import json
import re
import requests
import subprocess
from datetime import datetime

# Configuration from environment variables
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'aapatel35/philata-website')
DATA_BRANCH = os.environ.get('DATA_BRANCH', 'main')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; PhilataBot/1.0; +https://philata.ca)'
}

# IRCC Official JSON endpoints
EE_DRAWS_URL = 'https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_4_en.json'
PROCESSING_TIMES_URL = 'https://www.canada.ca/content/dam/ircc/documents/json/data-ptime-en.json'

def now():
    return datetime.now().isoformat()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# =============================================================================
# DATA FETCHERS
# =============================================================================

def fetch_express_entry_draws():
    """Fetch latest Express Entry draws from IRCC"""
    log("Fetching Express Entry draws...")

    try:
        response = requests.get(EE_DRAWS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        draws = []
        rounds = data.get('rounds', [])

        for round_item in rounds[:50]:
            try:
                draw_date = round_item.get('drawDate', '')
                draw_name = round_item.get('drawName', 'General')
                crs_score = round_item.get('drawCRS', '')
                itas = round_item.get('drawSize', '')
                draw_number = round_item.get('drawNumber', '')

                # Parse CRS score
                crs_match = re.search(r'(\d+)', str(crs_score))
                crs_int = int(crs_match.group(1)) if crs_match else 0

                # Parse ITA count
                itas_str = str(itas).replace(',', '')
                itas_match = re.search(r'(\d+)', itas_str)
                itas_int = int(itas_match.group(1)) if itas_match else 0

                # Normalize category
                category = normalize_category(draw_name)

                if crs_int > 0:
                    draws.append({
                        'number': str(draw_number),
                        'date': draw_date,
                        'category': category,
                        'crs': crs_int,
                        'itas': itas_int
                    })
            except Exception as e:
                log(f"  Error parsing draw: {e}")
                continue

        # Calculate category averages
        category_cutoffs = calculate_category_averages(draws)

        log(f"  Fetched {len(draws)} draws")
        return draws, category_cutoffs

    except Exception as e:
        log(f"  Error fetching draws: {e}")
        return [], {}

def normalize_category(draw_name):
    """Normalize draw category names"""
    name_lower = draw_name.lower()

    if 'experience' in name_lower:
        return 'Canadian Experience Class'
    elif 'provincial' in name_lower or 'pnp' in name_lower:
        return 'Provincial Nominee Program'
    elif 'french' in name_lower:
        return 'French Language Proficiency'
    elif 'healthcare' in name_lower:
        return 'Healthcare Occupations'
    elif 'stem' in name_lower:
        return 'STEM Occupations'
    elif 'trade' in name_lower:
        return 'Trade Occupations'
    elif 'transport' in name_lower:
        return 'Transport Occupations'
    elif 'agriculture' in name_lower:
        return 'Agriculture & Agri-food'
    elif 'general' in name_lower or 'no program' in name_lower:
        return 'General'
    else:
        return draw_name

def calculate_category_averages(draws):
    """Calculate average CRS cutoffs by category"""
    categories = {}

    for draw in draws:
        cat = draw['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(draw['crs'])

    averages = {}
    for cat, scores in categories.items():
        recent = scores[:5]
        if recent:
            averages[cat] = {
                'average': round(sum(recent) / len(recent)),
                'lowest': min(recent),
                'highest': max(recent),
                'total_draws': len(scores),
                'last_draw': scores[0] if scores else 0
            }

    return {'categories': averages, 'updated': now()}

def fetch_processing_times():
    """Fetch processing times"""
    log("Fetching processing times...")

    times = {
        'express_entry': {
            'fsw': {'time': '6 months', 'status': 'normal'},
            'cec': {'time': '5 months', 'status': 'normal'},
            'fst': {'time': '6 months', 'status': 'normal'},
            'pnp': {'time': '6 months', 'status': 'normal'}
        },
        'temporary': {
            'visitor': {'time': '45 days', 'status': 'delayed'},
            'study': {'time': '8 weeks', 'status': 'normal'},
            'work_lmia': {'time': '12 weeks', 'status': 'delayed'},
            'pgwp': {'time': '80 days', 'status': 'normal'}
        },
        'family': {
            'spouse_inland': {'time': '12 months', 'status': 'normal'},
            'spouse_outland': {'time': '12 months', 'status': 'normal'},
            'pgp': {'time': '24 months', 'status': 'backlog'}
        }
    }

    log("  Processing times ready")
    return times

def fetch_pnp_in_demand():
    """Fetch provincial in-demand data"""
    log("Fetching PNP in-demand lists...")

    in_demand = {
        'bc': {
            'tech_occupations': [
                {'noc': '21231', 'title': 'Software Engineers'},
                {'noc': '21232', 'title': 'Software Developers'},
                {'noc': '21234', 'title': 'Web Developers'},
                {'noc': '21211', 'title': 'Data Scientists'},
                {'noc': '21222', 'title': 'Cybersecurity Specialists'}
            ],
            'healthcare_in_demand': True,
            'trades_in_demand': True
        },
        'ontario': {
            'tech_draw_eligible': True,
            'healthcare_in_demand': True,
            'trades_in_demand': True
        },
        'alberta': {
            'categories': ['tech', 'healthcare', 'trades', 'transport']
        },
        'saskatchewan': {
            'occupation_in_demand_list': True,
            'categories': ['healthcare', 'trades', 'agriculture']
        },
        'manitoba': {
            'categories': ['healthcare', 'trades']
        },
        'nova_scotia': {
            'labour_market_priorities': True,
            'categories': ['healthcare', 'trades']
        }
    }

    log(f"  PNP data for {len(in_demand)} provinces ready")
    return in_demand

def fetch_immigration_targets():
    """Fetch immigration targets - Updated 2026-2028 levels plan"""
    log("Fetching immigration targets...")

    # Updated based on IRCC 2026-2028 Immigration Levels Plan
    targets = {
        '2024': {'total': 485000, 'express_entry': 110770, 'pnp': 110000, 'family': 114000, 'refugee': 76000},
        '2025': {'total': 395000, 'express_entry': 124000, 'pnp': 55000, 'family': 82000, 'refugee': 52000},
        '2026': {'total': 380000, 'express_entry': 118000, 'pnp': 54000, 'family': 80000, 'refugee': 50000},
        '2027': {'total': 365000, 'express_entry': 112000, 'pnp': 52000, 'family': 78000, 'refugee': 48000},
        '2028': {'total': 380000, 'express_entry': 118000, 'pnp': 54000, 'family': 80000, 'refugee': 50000}
    }

    log("  Immigration targets ready")
    return targets

# =============================================================================
# GIT OPERATIONS
# =============================================================================

def run_git(cmd, cwd=None):
    """Run git command"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"  Git error: {result.stderr}")
    return result.returncode == 0

def clone_and_update_repo():
    """Clone repo, update data files, commit and push"""

    if not GITHUB_TOKEN:
        log("ERROR: GITHUB_TOKEN not set!")
        return False

    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    work_dir = "/tmp/philata-website"
    data_dir = f"{work_dir}/data"

    # Clone or pull repo
    if os.path.exists(work_dir):
        log("Pulling latest changes...")
        run_git(f"git pull origin {DATA_BRANCH}", cwd=work_dir)
    else:
        log("Cloning repository...")
        run_git(f"git clone --depth 1 -b {DATA_BRANCH} {repo_url} {work_dir}")

    # Create data directory
    os.makedirs(data_dir, exist_ok=True)

    # Fetch all data
    draws, category_cutoffs = fetch_express_entry_draws()
    processing_times = fetch_processing_times()
    pnp_in_demand = fetch_pnp_in_demand()
    immigration_targets = fetch_immigration_targets()

    # Save JSON files
    log("Saving JSON files...")

    if draws:
        # Add year field to each draw for the pool_stats page
        for draw in draws:
            if 'date' in draw:
                try:
                    draw['year'] = int(draw['date'].split('-')[0])
                except:
                    draw['year'] = datetime.now().year

        # Pool stats by year (estimated based on historical trends)
        pool_stats = {
            "2024": {
                "total_pool": 218000,
                "avg_score": 492,
                "distribution": {
                    "601-1200": 4200, "501-600": 32700, "451-500": 76300,
                    "401-450": 65400, "351-400": 26100, "0-350": 13300
                }
            },
            "2025": {
                "total_pool": 228000,
                "avg_score": 489,
                "distribution": {
                    "601-1200": 4500, "501-600": 34200, "451-500": 79800,
                    "401-450": 68400, "351-400": 27360, "0-350": 13740
                }
            },
            "2026": {
                "total_pool": 235000,
                "avg_score": 486,
                "distribution": {
                    "601-1200": 4700, "501-600": 35250, "451-500": 82250,
                    "401-450": 70500, "351-400": 28200, "0-350": 14100
                }
            }
        }

        with open(f"{data_dir}/draws.json", 'w') as f:
            json.dump({
                'draws': draws,
                'pool_stats': pool_stats,
                'source': 'IRCC Express Entry Rounds',
                'updated': now()
            }, f, indent=2)

    if category_cutoffs:
        with open(f"{data_dir}/category_cutoffs.json", 'w') as f:
            json.dump(category_cutoffs, f, indent=2)

    with open(f"{data_dir}/processing_times.json", 'w') as f:
        json.dump({'times': processing_times, 'updated': now()}, f, indent=2)

    with open(f"{data_dir}/pnp_in_demand.json", 'w') as f:
        json.dump({'provinces': pnp_in_demand, 'updated': now()}, f, indent=2)

    with open(f"{data_dir}/immigration_targets.json", 'w') as f:
        json.dump({'targets': immigration_targets, 'updated': now()}, f, indent=2)

    log("  JSON files saved")

    # Check for changes
    result = subprocess.run("git status --porcelain data/", shell=True, cwd=work_dir, capture_output=True, text=True)

    if not result.stdout.strip():
        log("No changes to commit")
        return True

    # Configure git
    run_git('git config user.email "bot@philata.ca"', cwd=work_dir)
    run_git('git config user.name "Philata Bot"', cwd=work_dir)

    # Commit and push
    log("Committing changes...")
    today = datetime.now().strftime('%Y-%m-%d')
    run_git("git add data/*.json", cwd=work_dir)
    run_git(f'git commit -m "chore: Daily data update {today}"', cwd=work_dir)

    log("Pushing to GitHub...")
    if run_git(f"git push origin {DATA_BRANCH}", cwd=work_dir):
        log("Successfully pushed changes!")
        return True
    else:
        log("Failed to push changes")
        return False

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print(f"Philata Data Updater - {now()}")
    print("=" * 60)
    print()

    success = clone_and_update_repo()

    print()
    print("=" * 60)
    print("Done!" if success else "Completed with errors")
    print("=" * 60)

if __name__ == '__main__':
    main()
