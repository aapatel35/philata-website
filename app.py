"""
Philata.ca - Canadian Immigration Content Hub
Dashboard for viewing and approving generated content
Comprehensive Immigration Guides
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Post API URL for fetching results
POST_API_URL = os.environ.get('POST_API_URL', 'https://web-production-35219.up.railway.app')

# Data storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
APPROVED_FILE = os.path.join(DATA_DIR, 'approved.json')
GUIDES_FILE = os.path.join(DATA_DIR, 'guides.json')
ARTICLES_FILE = os.path.join(DATA_DIR, 'articles.json')

# Cloudinary settings for URL conversion
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dg7yw1j18')


def convert_image_url(image_url):
    """Convert Docker/localhost URLs to Post API URLs"""
    if not image_url:
        return ''

    # Already a proper URL (Cloudinary, Unsplash, or Post API)
    if 'cloudinary.com' in image_url or 'unsplash.com' in image_url or 'web-production' in image_url:
        return image_url

    # Convert Docker/localhost URLs to Post API server
    if 'docker' in image_url.lower() or 'localhost' in image_url.lower():
        filename = image_url.split('/')[-1]
        if filename:
            return f"{POST_API_URL}/images/{filename}"

    return image_url


# Multiple images per category for variety (Unsplash direct URLs - no API needed)
ARTICLE_IMAGES = {
    'express_entry': [
        {'url': 'https://images.unsplash.com/photo-1569974507005-6dc61f97fb5c?w=1200&q=80', 'credit': 'Ali Tawfiq', 'credit_link': 'https://unsplash.com/@alitwfiq'},
        {'url': 'https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1200&q=80', 'credit': 'Hermes Rivera', 'credit_link': 'https://unsplash.com/@hermez777'},
        {'url': 'https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=1200&q=80', 'credit': 'Jason Hafso', 'credit_link': 'https://unsplash.com/@jasonhafso'},
        {'url': 'https://images.unsplash.com/photo-1473163928189-364b2c4e1135?w=1200&q=80', 'credit': 'Meric Dagli', 'credit_link': 'https://unsplash.com/@meric'},
        {'url': 'https://images.unsplash.com/photo-1559311648-d5dad5deea1d?w=1200&q=80', 'credit': 'Erik Mclean', 'credit_link': 'https://unsplash.com/@introspectivedsgn'},
    ],
    'pnp': [
        {'url': 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=1200&q=80', 'credit': 'Scott Webb', 'credit_link': 'https://unsplash.com/@scottwebb'},
        {'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80', 'credit': 'Joseph Gonzalez', 'credit_link': 'https://unsplash.com/@miracletwentyone'},
        {'url': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1200&q=80', 'credit': 'Ben O\'Sullivan', 'credit_link': 'https://unsplash.com/@benjamino'},
        {'url': 'https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=1200&q=80', 'credit': 'Sam Poullain', 'credit_link': 'https://unsplash.com/@sampoullain'},
        {'url': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1200&q=80', 'credit': 'Chris Karidis', 'credit_link': 'https://unsplash.com/@chriskaridis'},
    ],
    'policy': [
        {'url': 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1200&q=80', 'credit': 'Jason Hafso', 'credit_link': 'https://unsplash.com/@jasonhafso'},
        {'url': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80', 'credit': 'Tingey Injury Law', 'credit_link': 'https://unsplash.com/@tingeyinjurylawfirm'},
        {'url': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80', 'credit': 'Scott Graham', 'credit_link': 'https://unsplash.com/@homajob'},
        {'url': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&q=80', 'credit': 'Iñaki del Olmo', 'credit_link': 'https://unsplash.com/@inakihxz'},
        {'url': 'https://images.unsplash.com/photo-1436450412740-6b988f486c6b?w=1200&q=80', 'credit': 'Helloquence', 'credit_link': 'https://unsplash.com/@helloquence'},
    ],
    'study_permit': [
        {'url': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&q=80', 'credit': 'Vasily Koloda', 'credit_link': 'https://unsplash.com/@napr0tiv'},
        {'url': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=1200&q=80', 'credit': 'Changbok Ko', 'credit_link': 'https://unsplash.com/@kochangbok'},
        {'url': 'https://images.unsplash.com/photo-1562774053-701939374585?w=1200&q=80', 'credit': 'Nathan Dumlao', 'credit_link': 'https://unsplash.com/@nate_dumlao'},
        {'url': 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=1200&q=80', 'credit': 'Tim Gouw', 'credit_link': 'https://unsplash.com/@punttim'},
        {'url': 'https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=1200&q=80', 'credit': 'Priscilla Du Preez', 'credit_link': 'https://unsplash.com/@priscilladupreez'},
    ],
    'work_permit': [
        {'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80', 'credit': 'Alex Kotliarskyi', 'credit_link': 'https://unsplash.com/@frantic'},
        {'url': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1200&q=80', 'credit': 'Annie Spratt', 'credit_link': 'https://unsplash.com/@anniespratt'},
        {'url': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&q=80', 'credit': 'You X Ventures', 'credit_link': 'https://unsplash.com/@youxventures'},
        {'url': 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1200&q=80', 'credit': 'Austin Distel', 'credit_link': 'https://unsplash.com/@austindistel'},
        {'url': 'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1200&q=80', 'credit': 'Campaign Creators', 'credit_link': 'https://unsplash.com/@campaign_creators'},
    ],
    'forms': [
        {'url': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80', 'credit': 'Scott Graham', 'credit_link': 'https://unsplash.com/@homajob'},
        {'url': 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1200&q=80', 'credit': 'Kelly Sikkema', 'credit_link': 'https://unsplash.com/@kellysikkema'},
        {'url': 'https://images.unsplash.com/photo-1568667256549-094345857637?w=1200&q=80', 'credit': 'Glenn Carstens-Peters', 'credit_link': 'https://unsplash.com/@glenncarstenspeters'},
        {'url': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80', 'credit': 'Helloquence', 'credit_link': 'https://unsplash.com/@helloquence'},
        {'url': 'https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?w=1200&q=80', 'credit': 'Kelly Sikkema', 'credit_link': 'https://unsplash.com/@kellysikkema'},
    ],
    'educational': [
        {'url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80', 'credit': 'Green Chameleon', 'credit_link': 'https://unsplash.com/@craftedbygc'},
        {'url': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1200&q=80', 'credit': 'Aaron Burden', 'credit_link': 'https://unsplash.com/@aaronburden'},
        {'url': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80', 'credit': 'Element5 Digital', 'credit_link': 'https://unsplash.com/@element5digital'},
        {'url': 'https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=1200&q=80', 'credit': 'Thought Catalog', 'credit_link': 'https://unsplash.com/@thoughtcatalog'},
        {'url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=1200&q=80', 'credit': 'Kimberly Farmer', 'credit_link': 'https://unsplash.com/@kimberlyfarmer'},
    ],
    'default': [
        {'url': 'https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=1200&q=80', 'credit': 'John Lee', 'credit_link': 'https://unsplash.com/@john_artifexfilms'},
        {'url': 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=1200&q=80', 'credit': 'Scott Webb', 'credit_link': 'https://unsplash.com/@scottwebb'},
        {'url': 'https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=1200&q=80', 'credit': 'Jason Hafso', 'credit_link': 'https://unsplash.com/@jasonhafso'},
        {'url': 'https://images.unsplash.com/photo-1508693926297-1d61ee3df82a?w=1200&q=80', 'credit': 'Mike Benna', 'credit_link': 'https://unsplash.com/@mbenna'},
        {'url': 'https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1200&q=80', 'credit': 'Marc-Olivier Jodoin', 'credit_link': 'https://unsplash.com/@marcojodoin'},
    ]
}

# Large pool of direct Unsplash photo IDs for unique images
UNSPLASH_PHOTO_IDS = [
    # Canada & Travel
    'photo-1503614472-8c93d56e92ce', 'photo-1517935706615-2717063c2225', 'photo-1551632436-cbf8dd35adfa',
    'photo-1508693926297-1d61ee3df82a', 'photo-1486325212027-8081e485255e', 'photo-1569974507005-6dc61f97fb5c',
    'photo-1526778548025-fa2f459cd5c1', 'photo-1473163928189-364b2c4e1135', 'photo-1559311648-d5dad5deea1d',
    # Cities & Skylines
    'photo-1480714378408-67cf0d13bc1b', 'photo-1474487548417-781cb71495f3', 'photo-1499856871958-5b9627545d1a',
    'photo-1507003211169-0a1dd7228f2d', 'photo-1477959858617-67f85cf4f1df', 'photo-1514565131-fce0801e5785',
    # Government & Law
    'photo-1505664194779-8beaceb93744', 'photo-1589829545856-d10d557cf95f', 'photo-1450101499163-c8848c66ca85',
    'photo-1521587760476-6c12a4b040da', 'photo-1436450412740-6b988f486c6b', 'photo-1575505586569-646b2ca898fc',
    # Education & Study
    'photo-1523050854058-8df90110c9f1', 'photo-1541339907198-e08756dedf3f', 'photo-1562774053-701939374585',
    'photo-1498243691581-b145c3f54a5a', 'photo-1517486808906-6ca8b3f04846', 'photo-1503676260728-1c00da094a0b',
    # Work & Office
    'photo-1497366216548-37526070297c', 'photo-1521737604893-d14cc237f11d', 'photo-1504384308090-c894fdcc538d',
    'photo-1556761175-5973dc0f32e7', 'photo-1542744173-8e7e53415bb0', 'photo-1497215842964-222b430dc094',
    # Documents & Forms
    'photo-1554224155-6726b3ff858f', 'photo-1586281380349-632531db7ed4', 'photo-1568667256549-094345857637',
    'photo-1507925921958-8a62f3d1a50d', 'photo-1450101499163-c8848c66ca85', 'photo-1456324504439-367cee3b3c32',
    # Learning & Books
    'photo-1434030216411-0b793f4b4173', 'photo-1456513080510-7bf3a84b82f8', 'photo-1488190211105-8b0e65b80b4e',
    'photo-1497633762265-9d179a990aa6', 'photo-1491841550275-ad7854e35ca6', 'photo-1524995997946-a1c2e315a42f',
    # Nature & Landscapes
    'photo-1464822759023-fed622ff2c3b', 'photo-1506905925346-21bda4d32df4', 'photo-1470071459604-3b5ec3a7fe05',
    'photo-1441974231531-c6227db76b6e', 'photo-1469474968028-56623f02e42e', 'photo-1447752875215-b2761acb3c5d',
    # More variety
    'photo-1454165804606-c3d57bc86b40', 'photo-1460925895917-afdab827c52f', 'photo-1553484771-047a44eee27b',
    'photo-1551836022-d5d88e9218df', 'photo-1517245386807-bb43f82c33c4', 'photo-1522202176988-66273c2fd55f',
    'photo-1531482615713-2afd69097998', 'photo-1519389950473-47ba0277781c', 'photo-1552664730-d307ca884978',
]

def get_unique_unsplash_image(article_id, category='default', title=''):
    """Get a unique Unsplash image for each article from the photo pool"""
    # Use combination of id and title for better distribution
    unique_key = f"{article_id}_{title}"
    index = abs(hash(unique_key)) % len(UNSPLASH_PHOTO_IDS)
    photo_id = UNSPLASH_PHOTO_IDS[index]

    # Unsplash direct image URL format
    base_url = f'https://images.unsplash.com/{photo_id}'
    return {
        'url': f'{base_url}?auto=format&fit=crop&w=1200&q=80',
        'thumb': f'{base_url}?auto=format&fit=crop&w=400&q=80',
        'credit': 'Unsplash',
        'credit_link': 'https://unsplash.com'
    }


def load_guides():
    """Load immigration guides data"""
    if os.path.exists(GUIDES_FILE):
        with open(GUIDES_FILE, 'r') as f:
            return json.load(f)
    return {"categories": {}}


def load_articles():
    """Load articles from Post API or local fallback"""
    raw_results = []

    # Try external API first
    try:
        response = requests.get(f"{POST_API_URL}/results/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            raw_results = data if isinstance(data, list) else data.get('results', [])
    except:
        pass

    # Fallback to local results.json
    if not raw_results:
        try:
            with open('data/results.json', 'r') as f:
                raw_results = json.load(f)
        except:
            pass

    if raw_results:
        # Filter only items with full_article content
        articles = []
        for r in raw_results:
            if r.get('full_article') and len(r.get('full_article', '')) > 200:
                category = r.get('category', '')
                # Use provided slug or generate from title
                slug = r.get('slug') or create_slug(r.get('title', ''))
                article = {
                    'id': r.get('id', ''),
                    'slug': slug,
                    'title': r.get('title', ''),
                    'track': r.get('track', 'regular'),
                    'category': category,
                    'created_at': r.get('timestamp', r.get('date', '')),
                    'full_article': r.get('full_article', ''),
                    'source': r.get('source', ''),
                    'source_url': r.get('source_url', ''),
                    'official_source_url': r.get('official_source_url', ''),
                    'reading_time': max(1, len(r.get('full_article', '').split()) // 200),
                    # Enhanced fields
                    'key_takeaways': r.get('key_takeaways', []),
                    'stat_cards': r.get('stat_cards', []),
                    'verification': r.get('verification', {}),
                    'sources': r.get('sources', {}),
                }
                articles.append(article)

        # Sort articles by date
        articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Assign unique images to each article based on its ID, category, and title
        # Only if article doesn't already have a valid image_url
        for article in articles:
            existing_image = article.get('image_url', '')
            # Skip if article already has a Cloudinary or valid image URL
            if existing_image and ('cloudinary.com' in existing_image or 'web-production' in existing_image):
                # Keep existing image, just add thumbnail
                article['image_thumb'] = existing_image.replace('/upload/', '/upload/w_400,h_300,c_fill/')
                article['image_credit'] = 'Philata'
                article['image_credit_link'] = 'https://philata.com'
            else:
                # Fall back to Unsplash for articles without custom images
                unsplash = get_unique_unsplash_image(article['id'], article['category'], article['title'])
                article['image_url'] = unsplash.get('url', '')
                article['image_thumb'] = unsplash.get('thumb', '')
                article['image_credit'] = unsplash.get('credit', '')
                article['image_credit_link'] = unsplash.get('credit_link', '')

        return articles

    return []


def create_slug(title):
    """Create URL-friendly slug from title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:80].strip('-')


def load_results():
    """Load all results from local file"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_results(results):
    """Save results"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)


def load_approved():
    """Load approved content"""
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, 'r') as f:
            return json.load(f)
    return []


def save_approved(approved):
    """Save approved content"""
    with open(APPROVED_FILE, 'w') as f:
        json.dump(approved, f, indent=2)


# =============================================================================
# PUBLIC PAGES
# =============================================================================

@app.route('/')
def home():
    """Landing page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')


@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


# =============================================================================
# LEGAL PAGES
# =============================================================================

@app.route('/terms')
def terms():
    """Terms & Conditions page"""
    return render_template('terms.html')


@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy.html')


@app.route('/cookie-policy')
def cookie_policy():
    """Cookie Policy page"""
    return render_template('cookies.html')


@app.route('/refund-policy')
def refund_policy():
    """Refund Policy page"""
    return render_template('refund.html')


@app.route('/disclaimer')
def disclaimer():
    """Disclaimer page"""
    return render_template('disclaimer.html')


@app.route('/tools/crs-calculator')
def crs_calculator():
    """CRS Score Calculator"""
    return render_template('crs_calculator.html')


@app.route('/learn')
def learning_hub():
    """Learning Hub - Immigration Education Center"""
    return render_template('learning_hub.html')


@app.route('/practice-tests')
def practice_tests():
    """Practice Tests for Language Exams"""
    return render_template('practice_tests.html')


@app.route('/dashboard')
def dashboard():
    """Content dashboard"""
    results = load_results()
    return render_template('dashboard.html', results=results)


# =============================================================================
# ARTICLES SECTION
# =============================================================================

# =============================================================================
# BROWSE BY CATEGORY
# =============================================================================

# Province keywords for PNP filtering
PROVINCE_KEYWORDS = {
    'ontario': ['ontario', 'oinp', 'toronto', 'ottawa'],
    'british_columbia': ['british columbia', 'bc', 'bc pnp', 'vancouver', 'victoria'],
    'alberta': ['alberta', 'ainp', 'aaip', 'calgary', 'edmonton'],
    'saskatchewan': ['saskatchewan', 'sinp', 'saskatoon', 'regina'],
    'manitoba': ['manitoba', 'mpnp', 'winnipeg'],
    'nova_scotia': ['nova scotia', 'nsnp', 'halifax'],
    'new_brunswick': ['new brunswick', 'nbpnp', 'fredericton', 'moncton'],
    'pei': ['prince edward island', 'pei', 'pei pnp', 'charlottetown'],
    'newfoundland': ['newfoundland', 'labrador', 'nlpnp', "st. john's"],
    'yukon': ['yukon', 'ynp', 'whitehorse'],
    'nwt': ['northwest territories', 'nwt', 'yellowknife'],
    'nunavut': ['nunavut', 'iqaluit'],
}

def detect_province(title):
    """Detect province from article title"""
    title_lower = title.lower()
    for province, keywords in PROVINCE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return province
    return None


@app.route('/browse')
def browse_categories():
    """Browse articles by category with subcategories"""
    all_articles = load_articles()
    all_content = load_results()

    # Define category structure with filters
    categories = {
        'news': {
            'name': 'News & Updates',
            'icon': 'bi-newspaper',
            'description': 'Latest immigration news and policy updates',
            'color': '#EF4444',
            'subcategories': [
                {'id': 'breaking', 'name': 'Breaking News', 'icon': 'bi-lightning-charge'},
                {'id': 'policy', 'name': 'Policy Updates', 'icon': 'bi-file-earmark-text'},
                {'id': 'program', 'name': 'Program Updates', 'icon': 'bi-megaphone'},
            ]
        },
        'express_entry': {
            'name': 'Express Entry',
            'icon': 'bi-lightning',
            'description': 'Federal skilled worker and CRS updates',
            'color': '#14B8A6',
            'subcategories': [
                {'id': 'draw_results', 'name': 'Draw Results', 'icon': 'bi-trophy'},
                {'id': 'crs_updates', 'name': 'CRS Updates', 'icon': 'bi-graph-up'},
                {'id': 'fsw', 'name': 'Federal Skilled Worker', 'icon': 'bi-briefcase'},
            ]
        },
        'pnp': {
            'name': 'Provincial Programs (PNP)',
            'icon': 'bi-map',
            'description': 'Provincial Nominee Programs by province',
            'color': '#8B5CF6',
            'subcategories': [
                {'id': 'ontario', 'name': 'Ontario (OINP)', 'icon': 'bi-geo-alt'},
                {'id': 'british_columbia', 'name': 'British Columbia', 'icon': 'bi-geo-alt'},
                {'id': 'alberta', 'name': 'Alberta (AAIP)', 'icon': 'bi-geo-alt'},
                {'id': 'saskatchewan', 'name': 'Saskatchewan (SINP)', 'icon': 'bi-geo-alt'},
                {'id': 'manitoba', 'name': 'Manitoba (MPNP)', 'icon': 'bi-geo-alt'},
                {'id': 'nova_scotia', 'name': 'Nova Scotia', 'icon': 'bi-geo-alt'},
                {'id': 'new_brunswick', 'name': 'New Brunswick', 'icon': 'bi-geo-alt'},
                {'id': 'pei', 'name': 'Prince Edward Island', 'icon': 'bi-geo-alt'},
                {'id': 'newfoundland', 'name': 'Newfoundland', 'icon': 'bi-geo-alt'},
                {'id': 'territories', 'name': 'Territories (YT/NWT/NU)', 'icon': 'bi-geo-alt'},
            ]
        },
        'educational': {
            'name': 'Educational',
            'icon': 'bi-book',
            'description': 'Guides and tutorials for immigration process',
            'color': '#3B82F6',
            'subcategories': [
                {'id': 'application_process', 'name': 'Application Process', 'icon': 'bi-clipboard-check'},
                {'id': 'language_tests', 'name': 'Language Tests', 'icon': 'bi-translate'},
                {'id': 'crs_optimization', 'name': 'CRS Optimization', 'icon': 'bi-sliders'},
                {'id': 'settlement', 'name': 'Settlement Tips', 'icon': 'bi-house-heart'},
            ]
        },
        'forms': {
            'name': 'Forms & Guides',
            'icon': 'bi-file-earmark-ruled',
            'description': 'Official forms and how to fill them',
            'color': '#F59E0B',
            'subcategories': [
                {'id': 'express_entry_forms', 'name': 'Express Entry Forms', 'icon': 'bi-file-text'},
                {'id': 'pnp_forms', 'name': 'PNP Forms', 'icon': 'bi-file-text'},
                {'id': 'study_forms', 'name': 'Study Permit Forms', 'icon': 'bi-file-text'},
                {'id': 'work_forms', 'name': 'Work Permit Forms', 'icon': 'bi-file-text'},
            ]
        },
        'permits': {
            'name': 'Permits',
            'icon': 'bi-card-checklist',
            'description': 'Study and work permit information',
            'color': '#22C55E',
            'subcategories': [
                {'id': 'study_permit', 'name': 'Study Permits', 'icon': 'bi-mortarboard'},
                {'id': 'work_permit', 'name': 'Work Permits', 'icon': 'bi-briefcase'},
                {'id': 'pgwp', 'name': 'PGWP', 'icon': 'bi-award'},
            ]
        },
    }

    # Count articles per category and subcategory
    for cat_id, cat in categories.items():
        cat['total_count'] = 0
        for sub in cat['subcategories']:
            sub_id = sub['id']
            count = 0

            # Filter logic based on category and subcategory
            for article in all_articles:
                article_cat = article.get('category', '')
                article_track = article.get('track', '')
                article_title = article.get('title', '')

                matches = False

                # News category
                if cat_id == 'news':
                    if sub_id == 'breaking' and article_track == 'breaking':
                        matches = True
                    elif sub_id == 'policy' and article_cat == 'policy':
                        matches = True
                    elif sub_id == 'program' and article_cat in ['program', 'general']:
                        matches = True

                # Express Entry
                elif cat_id == 'express_entry':
                    if article_cat == 'express_entry':
                        if sub_id == 'draw_results' and ('draw' in article_title.lower() or 'ita' in article_title.lower()):
                            matches = True
                        elif sub_id == 'crs_updates' and 'crs' in article_title.lower():
                            matches = True
                        elif sub_id == 'fsw':
                            matches = True

                # PNP by province
                elif cat_id == 'pnp':
                    if article_cat == 'pnp':
                        province = detect_province(article_title)
                        if sub_id == 'territories' and province in ['yukon', 'nwt', 'nunavut']:
                            matches = True
                        elif province == sub_id:
                            matches = True

                # Educational
                elif cat_id == 'educational':
                    if article_cat == 'educational':
                        title_lower = article_title.lower()
                        if sub_id == 'application_process' and any(kw in title_lower for kw in ['application', 'process', 'submit', 'apply']):
                            matches = True
                        elif sub_id == 'language_tests' and any(kw in title_lower for kw in ['ielts', 'celpip', 'tef', 'language', 'english', 'french']):
                            matches = True
                        elif sub_id == 'crs_optimization' and any(kw in title_lower for kw in ['crs', 'score', 'points', 'boost', 'improve']):
                            matches = True
                        elif sub_id == 'settlement' and any(kw in title_lower for kw in ['settle', 'housing', 'bank', 'job search']):
                            matches = True
                        else:
                            matches = True  # Default educational

                # Forms
                elif cat_id == 'forms':
                    if article_cat == 'forms':
                        title_lower = article_title.lower()
                        if sub_id == 'express_entry_forms' and any(kw in title_lower for kw in ['imm 0008', 'ee', 'express entry']):
                            matches = True
                        elif sub_id == 'pnp_forms' and 'pnp' in title_lower:
                            matches = True
                        elif sub_id == 'study_forms' and any(kw in title_lower for kw in ['study', 'student', 'imm 1294']):
                            matches = True
                        elif sub_id == 'work_forms' and any(kw in title_lower for kw in ['work', 'lmia', 'imm 1295']):
                            matches = True
                        else:
                            matches = True  # Default forms

                # Permits
                elif cat_id == 'permits':
                    if sub_id == 'study_permit' and article_cat == 'study_permit':
                        matches = True
                    elif sub_id == 'work_permit' and article_cat == 'work_permit':
                        matches = True
                    elif sub_id == 'pgwp' and 'pgwp' in article_title.lower():
                        matches = True

                if matches:
                    count += 1

            sub['count'] = count
            cat['total_count'] += count

        # Get latest articles for this category
        cat_articles = [a for a in all_articles if a.get('category') == cat_id or
                       (cat_id == 'news' and a.get('track') == 'breaking') or
                       (cat_id == 'pnp' and a.get('category') == 'pnp')]
        cat['latest'] = cat_articles[:3]

    return render_template('browse.html', categories=categories)


@app.route('/browse/<category>')
def browse_category(category):
    """Browse articles in a specific category"""
    all_articles = load_articles()
    subcategory = request.args.get('sub')

    filtered_articles = []
    category_name = category.replace('_', ' ').title()
    subcategory_name = None

    for article in all_articles:
        article_cat = article.get('category', '')
        article_track = article.get('track', '')
        article_title = article.get('title', '')

        matches = False

        # Filter by main category
        if category == 'news':
            if subcategory == 'breaking' and article_track == 'breaking':
                matches = True
                subcategory_name = 'Breaking News'
            elif subcategory == 'policy' and article_cat == 'policy':
                matches = True
                subcategory_name = 'Policy Updates'
            elif subcategory == 'program' and article_cat in ['program', 'general']:
                matches = True
                subcategory_name = 'Program Updates'
            elif not subcategory and (article_track == 'breaking' or article_cat in ['policy', 'program', 'general']):
                matches = True

        elif category == 'express_entry':
            if article_cat == 'express_entry':
                if subcategory == 'draw_results' and ('draw' in article_title.lower() or 'ita' in article_title.lower()):
                    matches = True
                    subcategory_name = 'Draw Results'
                elif subcategory == 'crs_updates' and 'crs' in article_title.lower():
                    matches = True
                    subcategory_name = 'CRS Updates'
                elif not subcategory:
                    matches = True

        elif category == 'pnp':
            if article_cat == 'pnp':
                province = detect_province(article_title)
                if subcategory and province == subcategory:
                    matches = True
                    subcategory_name = subcategory.replace('_', ' ').title()
                elif subcategory == 'territories' and province in ['yukon', 'nwt', 'nunavut']:
                    matches = True
                    subcategory_name = 'Territories'
                elif not subcategory:
                    matches = True

        elif category == 'educational':
            if article_cat == 'educational':
                if subcategory:
                    subcategory_name = subcategory.replace('_', ' ').title()
                matches = True

        elif category == 'forms':
            if article_cat == 'forms':
                if subcategory:
                    subcategory_name = subcategory.replace('_', ' ').title()
                matches = True

        elif category == 'permits':
            if subcategory == 'study_permit' and article_cat == 'study_permit':
                matches = True
                subcategory_name = 'Study Permits'
            elif subcategory == 'work_permit' and article_cat == 'work_permit':
                matches = True
                subcategory_name = 'Work Permits'
            elif not subcategory and article_cat in ['study_permit', 'work_permit']:
                matches = True

        if matches:
            filtered_articles.append(article)

    return render_template('browse_category.html',
                          articles=filtered_articles,
                          category=category,
                          category_name=category_name,
                          subcategory=subcategory,
                          subcategory_name=subcategory_name)


@app.route('/articles')
def articles():
    """Articles listing page"""
    all_articles = load_articles()
    category = request.args.get('category')

    if category:
        all_articles = [a for a in all_articles if a.get('category') == category]

    return render_template('articles.html', articles=all_articles, category=category)


def generate_short_id(title):
    """Generate short ID from title (matching n8n workflow)"""
    if not title:
        return 'news'
    hash_val = 0
    for char in title:
        hash_val = ((hash_val << 5) - hash_val) + ord(char)
        hash_val = hash_val & 0xFFFFFFFF  # Keep as 32-bit
    # Convert to base36 and take first 6 chars
    import string
    chars = string.digits + string.ascii_lowercase
    result = ''
    val = abs(hash_val)
    while val > 0:
        result = chars[val % 36] + result
        val //= 36
    return result[:6] if result else 'news'


@app.route('/a/<short_id>')
def short_url_redirect(short_id):
    """Short URL redirect - finds article by short_id and redirects to full URL"""
    all_articles = load_articles()

    # Find article by matching short_id
    for article in all_articles:
        if generate_short_id(article.get('title', '')) == short_id:
            slug = article.get('slug') or create_slug(article.get('title', ''))
            return redirect(f'/articles/{slug}', code=301)

    # If not found, redirect to articles listing
    return redirect('/articles', code=302)


@app.route('/articles/<slug>')
def article_detail(slug):
    """Individual article page"""
    all_articles = load_articles()

    # Find article by slug or ID
    article = None
    for a in all_articles:
        if a.get('slug') == slug or a.get('id') == slug:
            article = a
            break

    if not article:
        return "Article not found", 404

    # Get related articles (same category)
    related = [a for a in all_articles if a.get('category') == article.get('category') and a.get('id') != article.get('id')][:3]

    return render_template('article_detail.html', article=article, related=related)


# =============================================================================
# GUIDES SECTION
# =============================================================================

@app.route('/guides')
def guides():
    """Immigration guides main page"""
    guides_data = load_guides()
    return render_template('guides.html', categories=guides_data.get('categories', {}))


@app.route('/guides/<category_id>')
def guides_category(category_id):
    """Guide category page"""
    guides_data = load_guides()
    categories = guides_data.get('categories', {})

    # Find the category
    category = None
    for cat_key, cat_data in categories.items():
        if cat_data.get('id') == category_id:
            category = cat_data
            break

    if not category:
        return "Category not found", 404

    return render_template('guides.html', categories=categories, selected_category=category)


@app.route('/guides/<category_id>/<guide_id>')
def guide_detail(category_id, guide_id):
    """Individual guide detail page"""
    guides_data = load_guides()
    categories = guides_data.get('categories', {})

    # Find the category and guide
    category = None
    guide = None

    for cat_key, cat_data in categories.items():
        if cat_data.get('id') == category_id:
            category = cat_data
            # Search in guides list
            if 'guides' in cat_data:
                for g in cat_data['guides']:
                    if g.get('id') == guide_id:
                        guide = g
                        break
            break

    if not category or not guide:
        return "Guide not found", 404

    return render_template('guide_detail.html', category=category, guide=guide)


@app.route('/guides/pnp/<province_id>')
def province_detail(province_id):
    """Province PNP detail page"""
    guides_data = load_guides()
    categories = guides_data.get('categories', {})

    # Find the province
    province = None
    pnp_category = categories.get('provincial_programs', {})

    if 'provinces' in pnp_category:
        for p in pnp_category['provinces']:
            if p.get('id') == province_id:
                province = p
                break

    if not province:
        return "Province not found", 404

    # Define color based on province
    colors = {
        'ontario': '#E31837',
        'british-columbia': '#0EA5E9',
        'alberta': '#F59E0B',
        'saskatchewan': '#10B981',
        'manitoba': '#6366F1',
        'nova-scotia': '#8B5CF6',
        'new-brunswick': '#EC4899',
        'pei': '#14B8A6',
        'newfoundland': '#F97316'
    }
    color = colors.get(province_id, '#E31837')

    return render_template('province_detail.html', province=province, color=color)


@app.route('/content/<content_id>')
def view_content(content_id):
    """View single content item"""
    results = load_results()
    content = next((r for r in results if r.get('id') == content_id), None)
    if content:
        return render_template('content_detail.html', content=content)
    return "Content not found", 404


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "Philata Content Hub",
        "version": "1.1",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get all results"""
    results = load_results()
    track = request.args.get('track')
    status = request.args.get('status')

    if track:
        results = [r for r in results if r.get('track') == track]
    if status:
        results = [r for r in results if r.get('status') == status]

    # Convert Docker/localhost URLs to Cloudinary URLs
    for r in results:
        if 'image_url' in r:
            r['image_url'] = convert_image_url(r.get('image_url', ''))

    return jsonify({
        "count": len(results),
        "results": results
    })


@app.route('/api/articles', methods=['POST'])
def add_article():
    """
    Add a new article from n8n workflow (enhanced endpoint).
    Supports: slug, charts, verification, sources, SEO metadata.
    """
    try:
        data = request.get_json()
        results = load_results()

        # Use provided slug or generate from title
        slug = data.get('slug') or create_slug(data.get('title', ''))

        # Generate unique ID
        content_id = f"{data.get('track', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(results)}"

        # Build article URL
        article_url = data.get('article_url') or f"https://www.philata.com/articles/{slug}"

        article = {
            "id": content_id,
            "slug": slug,
            "article_url": article_url,

            # Content
            "title": data.get('title', ''),
            "subheadline": data.get('subheadline', data.get('subtitle', '')),
            "hook": data.get('hook', ''),
            "full_article": data.get('full_article') or data.get('content_html', ''),
            "key_takeaways": data.get('key_takeaways', []),
            "reading_time": data.get('reading_time', '3 min read'),

            # Visualizations
            "charts": data.get('charts', []),
            "stat_cards": data.get('stat_cards', []),
            "comparison_tables": data.get('comparison_tables', []),

            # Image
            "image_url": convert_image_url(data.get('image_url', '')),
            "filename": data.get('filename', ''),
            "image_credit": data.get('image_credit'),

            # Social media captions
            "captions": data.get('captions', {}),

            # Verification
            "verification": data.get('verification', {
                "status": "unverified",
                "confidence": 0,
                "reasoning": ""
            }),

            # Sources
            "sources": data.get('sources', {
                "official": [],
                "secondary": [],
                "verified_facts": []
            }),
            "disclaimer": data.get('disclaimer'),

            # SEO
            "seo": data.get('seo', {}),

            # Metadata
            "track": data.get('track', 'regular'),
            "category": data.get('category', 'general'),
            "content_type": data.get('content_type', 'news'),
            "is_breaking": data.get('is_breaking', False),

            # Legacy fields (backward compatibility)
            "source": data.get('source', ''),
            "source_url": data.get('source_url', ''),
            "official_source_url": data.get('official_source_url') or (
                data.get('sources', {}).get('official', [{}])[0].get('url') if data.get('sources', {}).get('official') else None
            ),

            # Status
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
            "posted_at": None
        }

        results.insert(0, article)
        save_results(results)

        # Also send to Post API so it appears in /articles/ listing
        try:
            post_api_payload = {
                "id": content_id,
                "title": article.get('title', ''),
                "track": article.get('track', 'regular'),
                "category": article.get('category', 'general'),
                "full_article": article.get('full_article', ''),
                "source": article.get('source', ''),
                "source_url": article.get('source_url', ''),
                "official_source_url": article.get('official_source_url', ''),
                "image_url": article.get('image_url', ''),
                "filename": article.get('filename', ''),
                "captions": article.get('captions', {}),
                "verified": article.get('verification', {}).get('status') == 'verified',
                # Enhanced fields
                "slug": slug,
                "key_takeaways": article.get('key_takeaways', []),
                "stat_cards": article.get('stat_cards', []),
                "verification": article.get('verification', {}),
                "sources": article.get('sources', {}),
            }
            post_response = requests.post(
                f"{POST_API_URL}/results/log",
                json=post_api_payload,
                timeout=10
            )
            print(f"   Post API response: {post_response.status_code}")
        except Exception as post_err:
            print(f"   ⚠️ Post API sync failed: {post_err}")

        print(f"✅ Article created: {slug}")
        print(f"   URL: {article_url}")
        print(f"   Verification: {article.get('verification', {}).get('confidence', 0)}%")

        return jsonify({
            "success": True,
            "id": content_id,
            "slug": slug,
            "article_url": article_url,
            "message": "Article created successfully"
        })
    except Exception as e:
        print(f"❌ Article creation failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/results', methods=['POST'])
def add_result():
    """Add a new result from n8n workflow (legacy endpoint)"""
    try:
        data = request.get_json()
        results = load_results()

        # Generate unique ID
        content_id = f"{data.get('track', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(results)}"

        result = {
            "id": content_id,
            "title": data.get('title', ''),
            "track": data.get('track', 'unknown'),
            "category": data.get('category', ''),
            "content_type": data.get('content_type', 'news'),
            "image_url": convert_image_url(data.get('image_url', '')),
            "filename": data.get('filename', ''),
            "captions": data.get('captions', {}),
            "full_article": data.get('full_article', ''),
            "source": data.get('source', ''),
            "source_url": data.get('source_url', ''),
            "official_source_url": data.get('official_source_url'),
            "status": "pending",  # pending, approved, rejected, posted
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
            "posted_at": None
        }

        results.insert(0, result)  # Add to beginning
        save_results(results)

        return jsonify({
            "success": True,
            "id": content_id,
            "message": "Content added successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/results/<content_id>/approve', methods=['POST'])
def approve_content(content_id):
    """Approve content for posting"""
    try:
        results = load_results()
        approved = load_approved()

        for result in results:
            if result.get('id') == content_id:
                result['status'] = 'approved'
                result['approved_at'] = datetime.now().isoformat()
                approved.append(result)
                break

        save_results(results)
        save_approved(approved)

        return jsonify({"success": True, "message": "Content approved"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/results/<content_id>/reject', methods=['POST'])
def reject_content(content_id):
    """Reject content"""
    try:
        results = load_results()

        for result in results:
            if result.get('id') == content_id:
                result['status'] = 'rejected'
                break

        save_results(results)
        return jsonify({"success": True, "message": "Content rejected"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/results/<content_id>/posted', methods=['POST'])
def mark_posted(content_id):
    """Mark content as posted"""
    try:
        results = load_results()

        for result in results:
            if result.get('id') == content_id:
                result['status'] = 'posted'
                result['posted_at'] = datetime.now().isoformat()
                break

        save_results(results)
        return jsonify({"success": True, "message": "Content marked as posted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get content statistics"""
    results = load_results()

    stats = {
        "total": len(results),
        "pending": len([r for r in results if r.get('status') == 'pending']),
        "approved": len([r for r in results if r.get('status') == 'approved']),
        "rejected": len([r for r in results if r.get('status') == 'rejected']),
        "posted": len([r for r in results if r.get('status') == 'posted']),
        "by_track": {},
        "today": len([r for r in results if r.get('created_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
    }

    for result in results:
        track = result.get('track', 'unknown')
        if track not in stats['by_track']:
            stats['by_track'][track] = 0
        stats['by_track'][track] += 1

    return jsonify(stats)


@app.route('/api/results/clear', methods=['POST'])
def clear_results():
    """Clear all results data"""
    try:
        save_results([])
        save_approved([])
        return jsonify({"success": True, "message": "All results cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/approved', methods=['GET'])
def get_approved():
    """Get approved content ready for posting"""
    approved = load_approved()
    return jsonify({
        "count": len(approved),
        "content": approved
    })


# =============================================================================
# IMAGE HANDLING
# =============================================================================

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload image from n8n"""
    try:
        if 'image' in request.files:
            image = request.files['image']
            filename = f"philata_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
            filepath = os.path.join(IMAGES_DIR, filename)
            image.save(filepath)
            return jsonify({
                "success": True,
                "filename": filename,
                "url": f"/static/images/{filename}"
            })

        # Handle base64 image
        data = request.get_json()
        if data and 'image_base64' in data:
            import base64
            image_data = base64.b64decode(data['image_base64'])
            filename = data.get('filename', f"philata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            filepath = os.path.join(IMAGES_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return jsonify({
                "success": True,
                "filename": filename,
                "url": f"/static/images/{filename}"
            })

        return jsonify({"success": False, "error": "No image provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images"""
    return send_from_directory(IMAGES_DIR, filename)


# =============================================================================
# SOCIAL MEDIA IMAGE GENERATION
# =============================================================================

IMAGE_SIZES = {
    'universal': (1080, 1080),
    'instagram_square': (1080, 1080),
    'instagram_story': (1080, 1920),
    'facebook': (1200, 630),
    'twitter': (1200, 675),
    'linkedin': (1200, 627)
}

THEME_COLORS = {
    'express_entry': {'badge': '#14B8A6', 'accent': '#F97316'},
    'pnp': {'badge': '#14B8A6', 'accent': '#F97316'},
    'policy': {'badge': '#6366F1', 'accent': '#6366F1'},
    'breaking': {'badge': '#EF4444', 'accent': '#EF4444'},
    'educational': {'badge': '#8B5CF6', 'accent': '#8B5CF6'},
    'study_permit': {'badge': '#3B82F6', 'accent': '#3B82F6'},
    'work_permit': {'badge': '#22C55E', 'accent': '#22C55E'},
    'news': {'badge': '#0EA5E9', 'accent': '#0EA5E9'},
    'default': {'badge': '#14B8A6', 'accent': '#F97316'}
}


def generate_social_image_html(image_data: dict, size: str = 'universal') -> str:
    """Generate HTML for social media image with modern design"""
    headline = image_data.get('headline', 'Immigration Update')
    subtext = image_data.get('subtext', '')
    category = image_data.get('category', 'news')
    stats = image_data.get('stats', [])

    width, height = IMAGE_SIZES.get(size, (1080, 1080))
    is_landscape = width > height
    colors = THEME_COLORS.get(category, THEME_COLORS['default'])

    # Calculate headline font size based on length
    headline_len = len(headline)
    if is_landscape:
        if headline_len <= 40: font_size = "36px"
        elif headline_len <= 60: font_size = "32px"
        elif headline_len <= 80: font_size = "28px"
        else: font_size = "24px"
    else:
        if headline_len <= 40: font_size = "52px"
        elif headline_len <= 60: font_size = "46px"
        elif headline_len <= 80: font_size = "40px"
        elif headline_len <= 100: font_size = "36px"
        else: font_size = "32px"

    # Stats HTML
    stats_html = ''
    if stats and len(stats) > 0:
        stats_cards = ''.join([
            f'''<div class="stat-card">
                <div class="stat-value">{s.get('value', '')}</div>
                <div class="stat-label">{s.get('label', '')}</div>
            </div>''' for s in stats[:3]
        ])
        stats_html = f'<div class="stats-row">{stats_cards}</div>'

    badge_text = category.replace('_', ' ').upper()
    subtext_html = f'<div class="divider"></div><p class="subtext">{subtext}</p>' if subtext else ''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={width}, height={height}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {width}px;
            height: {height}px;
            font-family: 'Inter', -apple-system, sans-serif;
            overflow: hidden;
            background: linear-gradient(180deg, #FAFAFA 0%, #F5F5F7 100%);
            position: relative;
        }}
        .orb {{
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.6;
        }}
        .orb-pink {{
            width: {'300px' if is_landscape else '400px'};
            height: {'300px' if is_landscape else '400px'};
            background: radial-gradient(circle, rgba(255, 182, 193, 0.8) 0%, transparent 70%);
            top: -100px;
            left: -100px;
        }}
        .orb-teal {{
            width: {'280px' if is_landscape else '350px'};
            height: {'280px' if is_landscape else '350px'};
            background: radial-gradient(circle, rgba(144, 224, 239, 0.7) 0%, transparent 70%);
            top: -50px;
            right: -80px;
        }}
        .orb-purple {{
            width: {'300px' if is_landscape else '380px'};
            height: {'300px' if is_landscape else '380px'};
            background: radial-gradient(circle, rgba(196, 181, 253, 0.7) 0%, transparent 70%);
            bottom: -80px;
            left: -80px;
        }}
        .orb-orange {{
            width: {'280px' if is_landscape else '350px'};
            height: {'280px' if is_landscape else '350px'};
            background: radial-gradient(circle, rgba(254, 215, 170, 0.8) 0%, transparent 70%);
            bottom: -60px;
            right: -60px;
        }}
        .slide {{
            width: 100%;
            height: 100%;
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            padding: 40px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
            padding-top: {'20px' if is_landscape else '30px'};
        }}
        .logo {{
            font-size: {'22px' if is_landscape else '28px'};
            font-weight: 800;
            color: #F97316;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: {colors['badge']};
            color: white;
            padding: {'14px 28px' if is_landscape else '20px 40px'};
            border-radius: 50px;
            font-size: {'20px' if is_landscape else '32px'};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            box-shadow: 0 6px 30px {colors['badge']}50;
            margin: {'20px auto 0' if is_landscape else '30px auto'};
        }}
        .content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 20px 15px;
        }}
        .headline {{
            font-size: {font_size};
            font-weight: 800;
            color: #1F2937;
            line-height: 1.2;
            max-width: {'95%' if is_landscape else '98%'};
            margin-bottom: {'15px' if is_landscape else '25px'};
            word-wrap: break-word;
            overflow-wrap: break-word;
            display: -webkit-box;
            -webkit-line-clamp: {'4' if is_landscape else '6'};
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .divider {{
            width: 100px;
            height: 4px;
            background: {colors['badge']};
            border-radius: 2px;
            margin: 20px 0;
        }}
        .subtext {{
            font-size: 26px;
            font-weight: 500;
            color: #6B7280;
        }}
        .stats-row {{
            display: flex;
            gap: {'15px' if is_landscape else '20px'};
            margin-top: {'15px' if is_landscape else '20px'};
            width: 100%;
            max-width: {'600px' if is_landscape else '800px'};
        }}
        .stat-card {{
            flex: 1;
            background: white;
            border-radius: {'16px' if is_landscape else '20px'};
            padding: {'15px' if is_landscape else '20px'};
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        .stat-value {{
            font-size: {'32px' if is_landscape else '38px'};
            font-weight: 800;
            color: {colors['accent']};
        }}
        .stat-label {{
            font-size: {'13px' if is_landscape else '15px'};
            color: #6B7280;
            margin-top: 5px;
        }}
        .footer {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 15px;
            margin-top: auto;
        }}
        .handle-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .handle-line {{
            width: 60px;
            height: 2px;
            background: #D1D5DB;
        }}
        .handle {{
            color: #374151;
            font-size: 24px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="orb orb-pink"></div>
    <div class="orb orb-teal"></div>
    <div class="orb orb-purple"></div>
    <div class="orb orb-orange"></div>
    <div class="slide">
        <div class="header">
            <span class="logo">Philata</span>
        </div>
        <div class="badge">{badge_text}</div>
        <div class="content">
            <h1 class="headline">{headline}</h1>
            {stats_html}
            {subtext_html}
        </div>
        <div class="footer">
            <div class="handle-container">
                <span class="handle-line"></span>
                <span class="handle">philata.com</span>
                <span class="handle-line"></span>
            </div>
        </div>
    </div>
</body>
</html>'''
    return html


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    Generate social media image HTML from article data.

    Request body:
    {
        "headline": "CRS Optimization 2026",
        "subtext": "Beat 534 Cutoffs",
        "category": "educational",
        "stats": [{"value": "534", "label": "CRS Cutoff"}],
        "size": "universal"
    }

    Returns HTML that can be rendered to an image.
    """
    try:
        data = request.get_json()

        image_data = {
            'headline': data.get('headline', data.get('image_text', {}).get('headline', 'Immigration Update')),
            'subtext': data.get('subtext', data.get('image_text', {}).get('subtext', '')),
            'category': data.get('category', 'news'),
            'stats': data.get('stats', data.get('stat_cards', []))
        }

        size = data.get('size', 'universal')
        html = generate_social_image_html(image_data, size)

        return jsonify({
            "success": True,
            "html": html,
            "size": IMAGE_SIZES.get(size, (1080, 1080)),
            "message": "Image HTML generated successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/render-image', methods=['POST'])
def render_image():
    """
    Render social media image and return as base64 PNG.
    Requires Playwright to be installed.

    Request body: Same as /api/generate-image
    Returns: {"success": true, "image_base64": "...", "url": "/images/..."}
    """
    try:
        # Check if Playwright is available
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return jsonify({
                "success": False,
                "error": "Playwright not installed. Use /api/generate-image for HTML output.",
                "fallback": "/api/generate-image"
            }), 501

        data = request.get_json()

        image_data = {
            'headline': data.get('headline', data.get('image_text', {}).get('headline', 'Immigration Update')),
            'subtext': data.get('subtext', data.get('image_text', {}).get('subtext', '')),
            'category': data.get('category', 'news'),
            'stats': data.get('stats', data.get('stat_cards', []))
        }

        size = data.get('size', 'universal')
        width, height = IMAGE_SIZES.get(size, (1080, 1080))
        html = generate_social_image_html(image_data, size)

        # Generate unique filename
        import base64
        import hashlib
        content_hash = hashlib.md5(html.encode()).hexdigest()[:8]
        filename = f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_hash}.png"
        filepath = os.path.join(IMAGES_DIR, filename)

        # Render HTML to PNG using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html)
            page.wait_for_load_state('networkidle')
            page.screenshot(path=filepath, type='png')
            browser.close()

        # Read image as base64
        with open(filepath, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            "success": True,
            "filename": filename,
            "url": f"/images/{filename}",
            "image_base64": image_base64,
            "size": [width, height],
            "message": "Image rendered successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# RUN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
