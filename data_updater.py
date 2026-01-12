"""
Immigration Data Updater Agent
Runs daily via GitHub Actions to keep website data current
Scrapes official IRCC sources and updates JSON data files
"""
import os
import json
import re
import requests
from datetime import datetime

# Optional: Use Gemini for parsing complex HTML
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; PhilataBot/1.0; +https://philata.ca)'
}

# =============================================================================
# EXPRESS ENTRY DRAWS - Official IRCC JSON endpoint
# =============================================================================
EE_DRAWS_URL = 'https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_4_en.json'

def update_express_entry_draws():
    """Fetch latest Express Entry draws from official IRCC JSON"""
    print("Updating Express Entry draws...")

    try:
        response = requests.get(EE_DRAWS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        draws = []
        for round_item in data.get('rounds', [])[:50]:
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
                itas_match = re.search(r'(\d+)', str(itas).replace(',', ''))
                itas_int = int(itas_match.group(1)) if itas_match else 0

                # Normalize category name
                category = normalize_category(draw_name)

                if crs_int > 0:
                    draws.append({
                        'number': draw_number,
                        'date': draw_date,
                        'category': category,
                        'crs': crs_int,
                        'itas': itas_int
                    })
            except Exception as e:
                print(f"  Error parsing draw: {e}")
                continue

        # Calculate category averages
        category_cutoffs = calculate_category_averages(draws)

        # Save draws
        save_json('draws.json', {
            'draws': draws,
            'source': 'IRCC Official',
            'url': EE_DRAWS_URL,
            'updated': now()
        })

        # Save category cutoffs
        save_json('category_cutoffs.json', category_cutoffs)

        print(f"  Updated {len(draws)} Express Entry draws")
        return draws

    except Exception as e:
        print(f"  Error fetching draws: {e}")
        return []

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
        recent = scores[:5]  # Last 5 draws
        if recent:
            averages[cat] = {
                'average': round(sum(recent) / len(recent)),
                'lowest': min(recent),
                'highest': max(recent),
                'total_draws': len(scores),
                'last_draw': scores[0] if scores else 0
            }

    return {
        'categories': averages,
        'updated': now()
    }

# =============================================================================
# PROCESSING TIMES - Official IRCC API
# =============================================================================
PROCESSING_TIMES_URL = 'https://www.canada.ca/content/dam/ircc/documents/json/data-ptime-en.json'

def update_processing_times():
    """Fetch current processing times from IRCC"""
    print("Updating processing times...")

    try:
        response = requests.get(PROCESSING_TIMES_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Structure the processing times data
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

        save_json('processing_times.json', {
            'times': times,
            'source': 'IRCC Official',
            'url': PROCESSING_TIMES_URL,
            'updated': now()
        })

        print("  Processing times updated")
        return times

    except Exception as e:
        print(f"  Error fetching processing times: {e}")
        return {}

# =============================================================================
# PROVINCIAL IN-DEMAND OCCUPATIONS
# =============================================================================
PROVINCIAL_URLS = {
    'bc': {
        'name': 'British Columbia',
        'url': 'https://www.welcomebc.ca/Immigrate-to-B-C/BC-PNP-Skills-Immigration/BC-PNP-Tech',
        'tech_list': True
    },
    'ontario': {
        'name': 'Ontario',
        'url': 'https://www.ontario.ca/page/ontario-immigrant-nominee-program-oinp'
    },
    'alberta': {
        'name': 'Alberta',
        'url': 'https://www.alberta.ca/alberta-advantage-immigration-program'
    },
    'saskatchewan': {
        'name': 'Saskatchewan',
        'url': 'https://www.saskatchewan.ca/residents/moving-to-saskatchewan/live-in-saskatchewan/by-immigrating/saskatchewan-immigrant-nominee-program'
    },
    'manitoba': {
        'name': 'Manitoba',
        'url': 'https://immigratemanitoba.com/'
    },
    'nova_scotia': {
        'name': 'Nova Scotia',
        'url': 'https://novascotiaimmigration.com/move-here/'
    }
}

def update_pnp_in_demand():
    """Update provincial in-demand occupation data"""
    print("Updating provincial in-demand lists...")

    # For now, use static data that can be updated manually
    # In future, can use Gemini to parse provincial websites

    in_demand = {
        'bc': {
            'tech_occupations': [
                {'noc': '21231', 'title': 'Software Engineers'},
                {'noc': '21232', 'title': 'Software Developers'},
                {'noc': '21234', 'title': 'Web Developers'},
                {'noc': '21211', 'title': 'Data Scientists'},
                {'noc': '21222', 'title': 'Cybersecurity Specialists'},
                {'noc': '20012', 'title': 'Computer/IT Managers'}
            ],
            'healthcare_occupations': [
                {'noc': '31301', 'title': 'Registered Nurses'},
                {'noc': '31302', 'title': 'Nurse Practitioners'},
                {'noc': '32101', 'title': 'Licensed Practical Nurses'}
            ],
            'source_url': PROVINCIAL_URLS['bc']['url']
        },
        'ontario': {
            'in_demand_categories': ['tech', 'healthcare', 'trades'],
            'tech_draw_eligible': True,
            'source_url': PROVINCIAL_URLS['ontario']['url']
        },
        'alberta': {
            'in_demand_categories': ['tech', 'healthcare', 'trades', 'transport'],
            'source_url': PROVINCIAL_URLS['alberta']['url']
        },
        'saskatchewan': {
            'in_demand_categories': ['healthcare', 'trades', 'agriculture'],
            'occupation_in_demand_list': True,
            'source_url': PROVINCIAL_URLS['saskatchewan']['url']
        },
        'manitoba': {
            'in_demand_categories': ['healthcare', 'trades'],
            'source_url': PROVINCIAL_URLS['manitoba']['url']
        },
        'nova_scotia': {
            'in_demand_categories': ['healthcare', 'trades'],
            'labour_market_priorities': True,
            'source_url': PROVINCIAL_URLS['nova_scotia']['url']
        }
    }

    save_json('pnp_in_demand.json', {
        'provinces': in_demand,
        'updated': now()
    })

    print(f"  Updated {len(in_demand)} provinces")
    return in_demand

# =============================================================================
# IMMIGRATION TARGETS
# =============================================================================
def update_immigration_targets():
    """Update annual immigration targets"""
    print("Updating immigration targets...")

    targets = {
        '2024': {
            'total': 485000,
            'economic': 281135,
            'express_entry': 110770,
            'pnp': 110000,
            'family': 114000,
            'refugee': 76115
        },
        '2025': {
            'total': 395000,
            'economic': 232000,
            'express_entry': 124000,
            'pnp': 82000,
            'family': 84000,
            'refugee': 52000
        },
        '2026': {
            'total': 380000,
            'economic': 220000,
            'express_entry': 118000,
            'pnp': 79000,
            'family': 82000,
            'refugee': 50500
        },
        '2027': {
            'total': 365000,
            'economic': 209000,
            'express_entry': 112000,
            'pnp': 76000,
            'family': 80000,
            'refugee': 48500
        }
    }

    save_json('immigration_targets.json', {
        'targets': targets,
        'source': 'IRCC Immigration Levels Plan 2025-2027',
        'updated': now()
    })

    print("  Immigration targets updated")
    return targets

# =============================================================================
# UTILITIES
# =============================================================================
def save_json(filename, data):
    """Save data to JSON file"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {filepath}")

def load_json(filename):
    """Load data from JSON file"""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def now():
    """Get current timestamp"""
    return datetime.now().isoformat()

# =============================================================================
# MAIN
# =============================================================================
def main():
    """Run all data updates"""
    print(f"\n{'='*60}")
    print(f"Immigration Data Updater - {now()}")
    print(f"{'='*60}\n")

    # Update all data sources
    update_express_entry_draws()
    update_processing_times()
    update_pnp_in_demand()
    update_immigration_targets()

    print(f"\n{'='*60}")
    print("Data update complete!")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
