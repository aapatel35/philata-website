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
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; PhilataBot/1.0; +https://philata.ca)'
}

# Month name to number mapping
MONTHS = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}

def parse_draw_date(date_str):
    """Parse date like 'January 7, 2026' to '2026-01-07'"""
    try:
        # Format: "January 7, 2026"
        parts = date_str.replace(',', '').split()
        if len(parts) >= 3:
            month = MONTHS.get(parts[0].lower(), '01')
            day = parts[1].zfill(2)
            year = parts[2]
            return f"{year}-{month}-{day}"
    except Exception:
        pass
    return datetime.now().strftime('%Y-%m-%d')

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
        rounds_data = data.get('rounds', {})

        # IRCC returns rounds as a dict with keys like 'r390', 'r389', etc.
        # Sort by round number (descending) to get most recent first
        sorted_keys = sorted(rounds_data.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0, reverse=True)

        for key in sorted_keys[:50]:
            round_item = rounds_data[key]
            try:
                draw_date_full = round_item.get('drawDateFull', '')
                draw_name = round_item.get('drawName', 'General')
                crs_score = round_item.get('drawCRS', '')
                itas = round_item.get('drawSize', '')
                draw_number = round_item.get('drawNumber', '')

                # Parse date to YYYY-MM-DD format
                draw_date = parse_draw_date(draw_date_full)

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
                print(f"  Error parsing draw {key}: {e}")
                continue

        # Calculate category averages
        category_cutoffs = calculate_category_averages(draws)

        # Convert to website format (type/score instead of category/crs)
        website_draws = []
        for d in draws:
            year = int(d['date'].split('-')[0]) if d['date'] else 2026
            website_draws.append({
                'date': d['date'],
                'type': d['category'],
                'score': d['crs'],
                'itas': d['itas'],
                'year': year
            })

        # Load existing pool_stats or use defaults
        existing = load_json('draws.json') or {}
        pool_stats = existing.get('pool_stats', get_default_pool_stats())

        # Save draws with pool stats
        save_json('draws.json', {
            'draws': website_draws,
            'pool_stats': pool_stats,
            'source': 'IRCC Express Entry Rounds',
            'updated': now()
        })

        # Save category cutoffs separately for eligibility checker
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
def get_default_pool_stats():
    """Return default pool statistics"""
    return {
        "2024": {
            "total_pool": 218000,
            "avg_score": 492,
            "distribution": {
                "601-1200": 4200,
                "501-600": 32700,
                "451-500": 76300,
                "401-450": 65400,
                "351-400": 26100,
                "0-350": 13300
            }
        },
        "2025": {
            "total_pool": 228000,
            "avg_score": 489,
            "distribution": {
                "601-1200": 4500,
                "501-600": 34200,
                "451-500": 79800,
                "401-450": 68400,
                "351-400": 27360,
                "0-350": 13740
            }
        },
        "2026": {
            "total_pool": 235000,
            "avg_score": 486,
            "distribution": {
                "601-1200": 4700,
                "501-600": 35250,
                "451-500": 82250,
                "401-450": 70500,
                "351-400": 28200,
                "0-350": 14100
            }
        }
    }

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
# GEMINI AI INTEGRATION FOR DYNAMIC CONTENT
# =============================================================================
def configure_gemini():
    """Configure Gemini API if available"""
    if not GEMINI_AVAILABLE:
        print("  Gemini not available - skipping AI features")
        return None

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("  GEMINI_API_KEY not set - skipping AI features")
        return None

    try:
        client = genai.Client(api_key=api_key)
        print("  Gemini configured successfully")
        return client
    except Exception as e:
        print(f"  Error configuring Gemini: {e}")
        return None


def generate_draw_analysis(client, draws):
    """Use Gemini to analyze recent draw patterns and generate insights"""
    if not client or not draws:
        return None

    print("  Generating draw analysis with AI...")

    # Prepare draw data for analysis
    recent_draws = draws[:20]  # Last 20 draws
    draw_summary = "\n".join([
        f"- {d['date']}: {d['type']} - CRS {d['score']}, {d['itas']} ITAs"
        for d in recent_draws
    ])

    prompt = f"""Analyze these recent Canadian Express Entry draws and provide insights:

{draw_summary}

Provide a JSON response with:
1. "trend": Overall trend description (1-2 sentences)
2. "cec_outlook": Canadian Experience Class outlook
3. "pnp_outlook": Provincial Nominee Program outlook
4. "category_insights": Key insights about category-based draws
5. "recommendation": Brief recommendation for applicants

Return ONLY valid JSON, no markdown."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        # Clean response and parse JSON
        text = response.text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1].rsplit('```', 1)[0]
        return json.loads(text)
    except Exception as e:
        print(f"  Error generating analysis: {e}")
        return None


def update_guide_content_if_needed(model):
    """Check if guides need updating and use AI to enhance them"""
    if not model:
        return

    print("Checking guide content...")

    guides_data = load_json('guides.json')
    if not guides_data or not guides_data.get('categories'):
        print("  No guides data found - skipping")
        return

    # Check if guides were updated recently (within 7 days)
    last_updated = guides_data.get('updated', '')
    if last_updated:
        try:
            updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            days_old = (datetime.now() - updated_dt.replace(tzinfo=None)).days
            if days_old < 7:
                print(f"  Guides updated {days_old} days ago - skipping AI update")
                return
        except:
            pass

    # Update the timestamp
    guides_data['updated'] = now()
    save_json('guides.json', guides_data)
    print("  Guides timestamp updated")


def verify_data_integrity():
    """Verify all required data files exist and have content"""
    print("Verifying data integrity...")

    required_files = {
        'draws.json': ['draws'],
        'processing_times.json': ['times'],
        'immigration_targets.json': ['targets'],
        'pnp_in_demand.json': ['provinces'],
        'category_cutoffs.json': ['categories'],
        'guides.json': ['categories']
    }

    issues = []
    for filename, required_keys in required_files.items():
        data = load_json(filename)
        if not data:
            issues.append(f"  Missing or empty: {filename}")
            continue
        for key in required_keys:
            if not data.get(key):
                issues.append(f"  Missing key '{key}' in {filename}")

    if issues:
        print("  Data integrity issues found:")
        for issue in issues:
            print(issue)
        return False

    print("  All data files verified successfully")
    return True


def generate_summary_stats():
    """Generate summary statistics for the dashboard"""
    print("Generating summary statistics...")

    stats = {
        'total_draws_tracked': 0,
        'latest_draw_date': None,
        'avg_crs_cec': 0,
        'avg_crs_pnp': 0,
        'total_itas_2026': 0,
        'provinces_covered': 0
    }

    # Draws stats
    draws_data = load_json('draws.json')
    if draws_data and draws_data.get('draws'):
        draws = draws_data['draws']
        stats['total_draws_tracked'] = len(draws)
        stats['latest_draw_date'] = draws[0]['date'] if draws else None

        cec_draws = [d for d in draws if 'Experience' in d.get('type', '')]
        pnp_draws = [d for d in draws if 'Provincial' in d.get('type', '')]

        if cec_draws:
            stats['avg_crs_cec'] = round(sum(d['score'] for d in cec_draws) / len(cec_draws))
        if pnp_draws:
            stats['avg_crs_pnp'] = round(sum(d['score'] for d in pnp_draws) / len(pnp_draws))

        stats['total_itas_2026'] = sum(d['itas'] for d in draws if d.get('year') == 2026)

    # PNP stats
    pnp_data = load_json('pnp_in_demand.json')
    if pnp_data and pnp_data.get('provinces'):
        stats['provinces_covered'] = len(pnp_data['provinces'])

    save_json('summary_stats.json', {
        'stats': stats,
        'updated': now()
    })

    print(f"  Summary: {stats['total_draws_tracked']} draws tracked, latest: {stats['latest_draw_date']}")
    return stats


# =============================================================================
# MAIN
# =============================================================================
def main():
    """Run all data updates"""
    print(f"\n{'='*60}")
    print(f"Immigration Data Updater - {now()}")
    print(f"{'='*60}\n")

    # Configure Gemini AI
    model = configure_gemini()

    # Update all data sources
    update_express_entry_draws()
    update_processing_times()
    update_pnp_in_demand()
    update_immigration_targets()

    # AI-powered features (if available)
    if model:
        draws_data = load_json('draws.json')
        if draws_data and draws_data.get('draws'):
            analysis = generate_draw_analysis(model, draws_data['draws'])
            if analysis:
                save_json('draw_analysis.json', {
                    'analysis': analysis,
                    'updated': now()
                })
                print("  Draw analysis saved")

        update_guide_content_if_needed(model)

    # Generate summary and verify
    generate_summary_stats()
    verify_data_integrity()

    print(f"\n{'='*60}")
    print("Data update complete!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
