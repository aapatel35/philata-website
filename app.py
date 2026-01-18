"""
Philata.ca - Canadian Immigration Content Hub
Dashboard for viewing and approving generated content
Comprehensive Immigration Guides
Deploy trigger: 2026-01-14 - Clear all data
"""

# Load environment variables first (before other imports)
from dotenv import load_dotenv
load_dotenv()

import os
import json
import requests
import threading
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, flash
from functools import wraps

# Eastern timezone (EST = UTC-5, Railway server runs in UTC)
EST = timezone(timedelta(hours=-5))

def eastern_now():
    """Get current time in Eastern timezone for user-facing timestamps"""
    return datetime.now(EST)
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
# CORS: Only allow requests from Philata domains
CORS(app, origins=[
    'https://www.philata.com',
    'https://philata.com',
    'https://philata-website-production.up.railway.app',
    'http://localhost:5000'  # Development
])

# Secret key for sessions (CHANGE IN PRODUCTION)
app.secret_key = os.environ.get('SECRET_KEY', 'philata-dev-secret-key-change-in-production')

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after app is created
from models import User, save_user_score, get_user_scores, get_latest_user_score
from models import save_user_checklist, get_user_checklist, get_all_user_checklists
from models import save_article, unsave_article, get_saved_articles, is_article_saved
from models import AdminUser
from database import is_connected as db_is_connected, get_articles_collection, get_database
from database import get_users_collection, get_user_scores_collection, get_saved_articles_collection
from bson import ObjectId

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login - handles both regular users and admin users"""
    if user_id and user_id.startswith('admin_'):
        # Admin user
        admin_id = user_id[6:]  # Remove 'admin_' prefix
        return AdminUser.get_by_id(admin_id)
    return User.get_by_id(user_id)

# Ensure default admin exists on startup
try:
    AdminUser.ensure_default_admin()
except Exception as e:
    print(f"Could not create default admin: {e}")

# Post API URL for fetching results
POST_API_URL = os.environ.get('POST_API_URL', 'https://web-production-35219.up.railway.app')

# In-memory cache to prevent data loss during runtime
# Data persists in memory until container restarts
# Cache cleared on Jan 16, 2026 - anti-fabrication system deployed
_memory_cache = {
    'articles': [],
    'results': [],
    'last_fetch': None,
    'cache_ttl': timedelta(minutes=2)  # Re-fetch from API every 2 minutes (reduced for faster updates)
}
_cache_lock = threading.Lock()

# Data storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
APPROVED_FILE = os.path.join(DATA_DIR, 'approved.json')
GUIDES_FILE = os.path.join(DATA_DIR, 'guides.json')
ARTICLES_FILE = os.path.join(DATA_DIR, 'articles.json')
LOGS_FILE = os.path.join(DATA_DIR, 'n8n_logs.json')
AI_DECISIONS_FILE = os.path.join(DATA_DIR, 'ai_decisions.json')

# Admin settings
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'philata2025')

# Cloudinary settings for URL conversion
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dg7yw1j18')

# =============================================================================
# SECURITY: Rate Limiting & Input Validation
# =============================================================================

# Simple in-memory rate limiter (per IP, resets on restart)
_rate_limit_store = {}
_rate_limit_lock = threading.Lock()

def rate_limit(max_requests=30, window_seconds=60):
    """
    Simple rate limiting decorator.
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()  # Get first IP if multiple

            key = f"{f.__name__}:{client_ip}"
            now = datetime.now()

            with _rate_limit_lock:
                if key not in _rate_limit_store:
                    _rate_limit_store[key] = {'count': 0, 'window_start': now}

                entry = _rate_limit_store[key]

                # Reset window if expired
                if (now - entry['window_start']).total_seconds() > window_seconds:
                    entry['count'] = 0
                    entry['window_start'] = now

                # Check rate limit
                if entry['count'] >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': window_seconds - int((now - entry['window_start']).total_seconds())
                    }), 429

                entry['count'] += 1

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_article_data(data):
    """
    Validate article data from POST requests.
    Returns (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"

    # Required fields
    required = ['title']
    for field in required:
        if not data.get(field):
            return False, f"Missing required field: {field}"

    # Title length check
    if len(data.get('title', '')) > 500:
        return False, "Title too long (max 500 characters)"

    # Content length check (if provided)
    if data.get('full_article') and len(data.get('full_article', '')) > 100000:
        return False, "Article content too long (max 100,000 characters)"

    # Sanitize URLs - ensure they're not malicious
    url_fields = ['image_url', 'featured_image', 'source_url', 'official_source_url']
    for field in url_fields:
        url = data.get(field, '')
        if url and not url.startswith(('http://', 'https://', 'data:image')):
            if url and url != '':  # Only reject if actually provided
                return False, f"Invalid URL format in {field}"

    return True, None


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
    """Load articles from MongoDB (primary) with memory cache fallback"""
    global _memory_cache

    raw_results = []

    # Check memory cache first (prevents repeated DB queries)
    with _cache_lock:
        now = datetime.now()
        cache_valid = (_memory_cache.get('last_fetch') and
                      now - _memory_cache['last_fetch'] < _memory_cache['cache_ttl'])

        if cache_valid and _memory_cache.get('results'):
            raw_results = _memory_cache['results']

    # Load from MongoDB (primary source - where agent posts articles)
    if not raw_results:
        try:
            articles_col = get_articles_collection()
            if articles_col is not None:
                mongo_articles = list(articles_col.find({}).sort('created_at', -1).limit(500))
                if mongo_articles:
                    raw_results = []
                    for doc in mongo_articles:
                        doc['_id'] = str(doc['_id'])
                        raw_results.append(doc)
                    print(f"Loaded {len(raw_results)} articles from MongoDB")
                    # Update memory cache
                    with _cache_lock:
                        _memory_cache['results'] = raw_results
                        _memory_cache['last_fetch'] = datetime.now()
        except Exception as e:
            print(f"Error loading from MongoDB: {e}")

    # Fallback to local file if MongoDB empty/unavailable
    if not raw_results:
        try:
            with open(RESULTS_FILE, 'r') as f:
                local_data = json.load(f)
                if local_data:
                    raw_results = local_data
                    print(f"Loaded {len(raw_results)} articles from local file")
        except Exception as e:
            print(f"Error loading local results: {e}")

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
                    # Image - preserve Cloudinary URLs from n8n pipeline
                    'image_url': r.get('image_url', ''),
                    # Featured image - raw Gemini AI image for article hero (no overlay)
                    'featured_image': r.get('featured_image', ''),
                    # Enhanced fields
                    'key_takeaways': r.get('key_takeaways', []),
                    'stat_cards': r.get('stat_cards', []),
                    'charts': r.get('charts', []),
                    'verification': r.get('verification', {}),
                    'sources': r.get('sources', {}),
                    # Social media captions - normalize both nested and flat formats
                    'captions': r.get('captions', {}) if r.get('captions') else {
                        'instagram': r.get('caption_instagram', ''),
                        'facebook': r.get('caption_facebook', ''),
                        'linkedin': r.get('caption_linkedin', ''),
                        'twitter': r.get('caption_twitter', ''),
                    },
                }
                articles.append(article)

        # Sort articles by date
        articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Assign unique images to each article based on its ID, category, and title
        # Only if article doesn't already have a valid image_url
        for article in articles:
            existing_image = article.get('image_url', '')
            # Skip if article already has a valid image (Cloudinary, Railway, or base64 Gemini)
            has_valid_image = existing_image and (
                'cloudinary.com' in existing_image or
                'web-production' in existing_image or
                existing_image.startswith('data:image')  # Base64 Gemini-generated images
            )
            if has_valid_image:
                # Keep existing image, just add thumbnail
                if existing_image.startswith('data:image'):
                    # For base64 images, use the same image as thumbnail
                    article['image_thumb'] = existing_image
                else:
                    article['image_thumb'] = existing_image.replace('/upload/', '/upload/w_400,h_300,c_fill/')
                article['image_credit'] = 'Philata AI'
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


def load_articles_fresh():
    """Load articles directly from MongoDB, bypassing cache - for admin use"""
    raw_results = []

    # Load directly from MongoDB
    try:
        articles_col = get_articles_collection()
        if articles_col is not None:
            mongo_articles = list(articles_col.find({}).sort('created_at', -1).limit(500))
            if mongo_articles:
                for doc in mongo_articles:
                    doc['_id'] = str(doc['_id'])
                    raw_results.append(doc)
                print(f"[Admin] Loaded {len(raw_results)} articles fresh from MongoDB")
    except Exception as e:
        print(f"[Admin] Error loading from MongoDB: {e}")

    # Fallback to local file
    if not raw_results:
        try:
            with open(RESULTS_FILE, 'r') as f:
                local_data = json.load(f)
                if local_data:
                    raw_results = local_data
                    print(f"[Admin] Loaded {len(raw_results)} articles from local file")
        except Exception as e:
            print(f"[Admin] Error loading local results: {e}")

    # Process articles (same as load_articles but without cache and without filtering)
    if raw_results:
        articles = []
        for r in raw_results:
            # Include all articles for admin visibility
            category = r.get('category', '')
            slug = r.get('slug') or create_slug(r.get('title', ''))
            article = {
                'id': r.get('id', str(r.get('_id', ''))),
                '_id': r.get('_id', ''),
                'slug': slug,
                'title': r.get('title', ''),
                'track': r.get('track', 'regular'),
                'category': category,
                'created_at': r.get('created_at', r.get('timestamp', r.get('date', ''))),
                'full_article': r.get('full_article', ''),
                'source': r.get('source', ''),
                'source_url': r.get('source_url', ''),
                'reading_time': max(1, len(r.get('full_article', '').split()) // 200),
                'image_url': r.get('image_url', ''),
                'featured_image': r.get('featured_image', ''),
                'status': r.get('status', 'published'),
            }
            articles.append(article)
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
    """Load all results from MongoDB (primary) or local file (fallback)"""
    # Try MongoDB first (where agent posts articles)
    try:
        articles_col = get_articles_collection()
        if articles_col is not None:
            mongo_articles = list(articles_col.find({}).sort('created_at', -1).limit(500))
            if mongo_articles:
                results = []
                for doc in mongo_articles:
                    doc['_id'] = str(doc['_id'])
                    results.append(doc)
                return results
    except Exception as e:
        print(f"Error loading from MongoDB: {e}")

    # Fallback to local file
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_results(results):
    """Save results to file and memory cache"""
    global _memory_cache
    # Save to file
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    # Update memory cache
    with _cache_lock:
        _memory_cache['results'] = results
        _memory_cache['last_fetch'] = datetime.now()


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


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()

        # Validation
        errors = []
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', email=email, name=name)

        # Check if database is connected
        if not db_is_connected():
            flash('Registration is temporarily unavailable. Please try again later.', 'error')
            return render_template('auth/register.html', email=email, name=name)

        # Create user
        user, error = User.create(email, password, name)
        if error:
            flash(error, 'error')
            return render_template('auth/register.html', email=email, name=name)

        # Log in the user
        login_user(user)
        flash('Welcome to Philata! Your account has been created.', 'success')
        return redirect(url_for('profile'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Please enter your email and password', 'error')
            return render_template('auth/login.html', email=email)

        # Check if database is connected
        if not db_is_connected():
            flash('Login is temporarily unavailable. Please try again later.', 'error')
            return render_template('auth/login.html', email=email)

        # Authenticate user
        user, error = User.authenticate(email, password)
        if error:
            flash(error, 'error')
            return render_template('auth/login.html', email=email)

        # Log in the user
        login_user(user, remember=bool(remember))
        flash('Welcome back!', 'success')

        # Redirect to next page or profile
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('profile'))

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user's latest CRS score
    latest_score = get_latest_user_score(current_user.id)

    # Get user's score history
    score_history = get_user_scores(current_user.id, limit=10)

    # Get user's saved articles
    saved = get_saved_articles(current_user.id)

    # Get user's checklists
    checklists = get_all_user_checklists(current_user.id)

    return render_template('auth/profile.html',
                         latest_score=latest_score,
                         score_history=score_history,
                         saved_articles=saved,
                         checklists=checklists)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    name = request.form.get('name', '').strip()
    target_program = request.form.get('target_program', '')
    target_province = request.form.get('target_province', '')
    immigration_stage = request.form.get('immigration_stage', '')

    profile_data = {
        'target_program': target_program or None,
        'target_province': target_province or None,
        'immigration_stage': immigration_stage or 'researching',
        'crs_score': current_user.profile.get('crs_score')
    }

    if User.update_profile(current_user.id, profile_data):
        flash('Profile updated successfully!', 'success')
    else:
        flash('Failed to update profile. Please try again.', 'error')

    return redirect(url_for('profile'))


@app.route('/api/user/save-score', methods=['POST'])
@login_required
def api_save_score():
    """Save user's CRS score calculation"""
    try:
        data = request.get_json()
        score_id = save_user_score(current_user.id, data)

        if score_id:
            # Also update profile with latest score
            profile = current_user.profile.copy()
            profile['crs_score'] = data.get('total', 0)
            User.update_profile(current_user.id, profile)

            return jsonify({'success': True, 'score_id': score_id})

        return jsonify({'success': False, 'error': 'Failed to save score'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/scores')
@login_required
def api_get_scores():
    """Get user's CRS score history"""
    try:
        scores = get_user_scores(current_user.id)
        # Convert ObjectId to string for JSON serialization
        for score in scores:
            score['_id'] = str(score['_id'])
        return jsonify({'success': True, 'scores': scores})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/save-article', methods=['POST'])
@login_required
def api_save_article():
    """Save an article for the user"""
    try:
        data = request.get_json()
        article_id = data.get('article_id')

        if not article_id:
            return jsonify({'success': False, 'error': 'Article ID required'}), 400

        success = save_article(current_user.id, article_id, data)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/unsave-article', methods=['POST'])
@login_required
def api_unsave_article():
    """Remove a saved article"""
    try:
        data = request.get_json()
        article_id = data.get('article_id')

        if not article_id:
            return jsonify({'success': False, 'error': 'Article ID required'}), 400

        success = unsave_article(current_user.id, article_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/checklist', methods=['POST'])
@login_required
def api_save_checklist():
    """Save user's checklist progress"""
    try:
        data = request.get_json()
        program = data.get('program')
        items = data.get('items', [])

        if not program:
            return jsonify({'success': False, 'error': 'Program required'}), 400

        success = save_user_checklist(current_user.id, program, {'items': items})
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/checklist/<program>')
@login_required
def api_get_checklist(program):
    """Get user's checklist for a program"""
    try:
        checklist = get_user_checklist(current_user.id, program)
        if checklist:
            checklist['_id'] = str(checklist['_id'])
            return jsonify({'success': True, 'checklist': checklist})
        return jsonify({'success': True, 'checklist': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# TOOLS
# =============================================================================

@app.route('/tools/crs-calculator')
def crs_calculator():
    """CRS Score Calculator"""
    return render_template('crs_calculator.html')


@app.route('/tools/processing-times')
def processing_times():
    """Processing Times page with live IRCC data"""
    try:
        from ircc_scraper import get_cached_processing_times
        data = get_cached_processing_times()
    except Exception as e:
        print(f"Error fetching processing times: {e}")
        data = None
    return render_template('processing_times.html', data=data)


@app.route('/tools/crs-prediction')
def crs_prediction():
    """CRS Score Prediction page"""
    try:
        # Load draws from auto-updated JSON file
        draws_file = os.path.join(os.path.dirname(__file__), 'data', 'draws.json')
        if os.path.exists(draws_file):
            with open(draws_file, 'r') as f:
                data = json.load(f)
            draws = data.get('draws', [])
            # Calculate average CRS from recent draws
            crs_scores = [d.get('score', 0) for d in draws[:10] if d.get('score', 0) < 700]
            avg_crs = round(sum(crs_scores) / len(crs_scores)) if crs_scores else 520
        else:
            draws = []
            avg_crs = 520
    except Exception as e:
        print(f"Error fetching draws: {e}")
        draws = []
        avg_crs = 520
    return render_template('crs_prediction.html', draws=draws, avg_crs=avg_crs)


# =============================================================================
# CRS PREDICTION - 3-LAYER ARCHITECTURE
# Layer 1: Official Data Collection (Facts)
# Layer 2: Statistical Analysis (Computed Metrics)
# Layer 3: Predictive Model with Gemini (Evidence-Based Forecasting)
# =============================================================================

def load_official_data():
    """
    LAYER 1: Load official IRCC data from draws.json
    Returns facts only - no predictions
    """
    draws_file = os.path.join(os.path.dirname(__file__), 'data', 'draws.json')

    if not os.path.exists(draws_file):
        return None

    with open(draws_file, 'r') as f:
        data = json.load(f)

    draws = data.get('draws', [])
    pool_stats = data.get('pool_stats', {})

    # Get latest pool statistics
    latest_year = max(pool_stats.keys()) if pool_stats else '2026'
    latest_pool = pool_stats.get(latest_year, {})

    # Pool distribution (official IRCC data)
    pool_distribution = latest_pool.get('distribution', {
        '601-1200': 559,
        '501-600': 21013,
        '451-500': 70523,
        '401-450': 65120,
        '351-400': 52469,
        '301-350': 18745,
        '0-300': 8125
    })

    total_pool = latest_pool.get('total_pool', 236554)

    return {
        'draws': draws[:20],  # Last 20 draws
        'pool_distribution': pool_distribution,
        'total_pool_size': total_pool,
        'last_updated': data.get('updated', datetime.now().isoformat()),
        'annual_targets': {
            'express_entry_2026': 109000,
            'pnp_2026': 120000
        }
    }


def calculate_crs_trend(crs_scores):
    """
    Calculate CRS trend using linear regression
    Returns: 'declining', 'stable', or 'rising' with slope value
    """
    if len(crs_scores) < 3:
        return 'stable', 0

    n = len(crs_scores)
    x = list(range(n))

    # Simple linear regression
    x_mean = sum(x) / n
    y_mean = sum(crs_scores) / n

    numerator = sum((x[i] - x_mean) * (crs_scores[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0

    if slope < -2:
        return 'declining', round(slope, 2)
    elif slope > 2:
        return 'rising', round(slope, 2)
    else:
        return 'stable', round(slope, 2)


def calculate_statistics(official_data):
    """
    LAYER 2: Compute metrics from official data
    All calculations based on real data - no guessing
    """
    draws = official_data['draws']
    pool_dist = official_data['pool_distribution']
    total_pool = official_data['total_pool_size']

    # Categorize draws by type
    cec_draws = [d for d in draws if 'experience' in d.get('type', '').lower()]
    pnp_draws = [d for d in draws if 'provincial' in d.get('type', '').lower() or 'pnp' in d.get('type', '').lower()]
    french_draws = [d for d in draws if 'french' in d.get('type', '').lower()]
    healthcare_draws = [d for d in draws if 'health' in d.get('type', '').lower()]
    trade_draws = [d for d in draws if 'trade' in d.get('type', '').lower()]

    # General draws (exclude PNP which has 600+ boost)
    general_draws = [d for d in draws if d.get('score', 0) < 700]

    # Calculate averages by category (last 5 of each)
    def avg_score(draw_list, count=5):
        scores = [d.get('score', 0) for d in draw_list[:count] if d.get('score', 0) > 0]
        return round(sum(scores) / len(scores)) if scores else 0

    def avg_itas(draw_list, count=5):
        itas = [d.get('itas', 0) for d in draw_list[:count] if d.get('itas', 0) > 0]
        return round(sum(itas) / len(itas)) if itas else 0

    # CRS trend calculation (last 10 general draws)
    general_crs = [d.get('score', 0) for d in general_draws[:10] if d.get('score', 0) > 0]
    trend, slope = calculate_crs_trend(general_crs)

    # Pool pressure: % of candidates above typical cutoff (500)
    candidates_above_500 = pool_dist.get('501-600', 0) + pool_dist.get('601-1200', 0)
    pool_pressure = round((candidates_above_500 / total_pool) * 100, 1) if total_pool > 0 else 0

    # Draw frequency (percentage of each type in last 20 draws)
    total_draws = len(draws)

    # Calculate confidence based on data quality
    def calculate_confidence(draw_count, pool_pressure, trend):
        base = min(draw_count * 15, 60)  # More draws = more confidence
        if pool_pressure < 10:
            base += 15  # Low pressure = more predictable
        if trend == 'stable':
            base += 10
        return min(base, 95)  # Cap at 95%

    return {
        'averages': {
            'cec': {'crs': avg_score(cec_draws), 'itas': avg_itas(cec_draws), 'count': len(cec_draws)},
            'pnp': {'crs': avg_score(pnp_draws), 'itas': avg_itas(pnp_draws), 'count': len(pnp_draws)},
            'french': {'crs': avg_score(french_draws), 'itas': avg_itas(french_draws), 'count': len(french_draws)},
            'healthcare': {'crs': avg_score(healthcare_draws), 'itas': avg_itas(healthcare_draws), 'count': len(healthcare_draws)},
            'trade': {'crs': avg_score(trade_draws), 'itas': avg_itas(trade_draws), 'count': len(trade_draws)},
            'general': {'crs': avg_score(general_draws), 'itas': avg_itas(general_draws), 'count': len(general_draws)}
        },
        'trend': {
            'direction': trend,
            'slope': slope
        },
        'pool_analysis': {
            'total_candidates': total_pool,
            'above_500': candidates_above_500,
            'pressure_percent': pool_pressure,
            'pressure_level': 'Low' if pool_pressure < 10 else 'Medium' if pool_pressure < 15 else 'High'
        },
        'draw_frequency': {
            'cec': round((len(cec_draws) / total_draws) * 100) if total_draws > 0 else 0,
            'pnp': round((len(pnp_draws) / total_draws) * 100) if total_draws > 0 else 0,
            'french': round((len(french_draws) / total_draws) * 100) if total_draws > 0 else 0,
            'healthcare': round((len(healthcare_draws) / total_draws) * 100) if total_draws > 0 else 0
        },
        'confidence': {
            'cec': calculate_confidence(len(cec_draws), pool_pressure, trend),
            'pnp': calculate_confidence(len(pnp_draws), pool_pressure, trend),
            'french': calculate_confidence(len(french_draws), pool_pressure, trend),
            'healthcare': calculate_confidence(len(healthcare_draws), pool_pressure, trend)
        },
        'bounds': {
            'highest_recent': max([d.get('score', 0) for d in draws[:10]]) if draws else 0,
            'lowest_recent': min([d.get('score', 0) for d in general_draws[:10]]) if general_draws else 0
        }
    }


def build_gemini_prompt(official_data, statistics):
    """
    LAYER 3: Build structured prompt for Gemini with all computed data
    """
    today = datetime.now().strftime('%B %d, %Y')

    # Format recent draws
    draws_text = "\n".join([
        f"  - {d.get('date')}: {d.get('type')} | CRS: {d.get('score')} | ITAs: {d.get('itas')}"
        for d in official_data['draws'][:10]
    ])

    # Format pool distribution
    pool_dist = official_data['pool_distribution']
    pool_text = "\n".join([f"  - {k} CRS: {v:,} candidates" for k, v in pool_dist.items()])

    stats = statistics

    return f"""You are an expert Canadian immigration analyst. Today is {today}.

=== LAYER 1: OFFICIAL IRCC DATA (FACTS) ===
Last Updated: {official_data['last_updated']}
Total Pool Size: {official_data['total_pool_size']:,} candidates

Pool Distribution:
{pool_text}

Recent Draws (Last 10):
{draws_text}

2026 Targets:
  - Express Entry: {official_data['annual_targets']['express_entry_2026']:,} ITAs
  - PNP: {official_data['annual_targets']['pnp_2026']:,} nominations

=== LAYER 2: COMPUTED STATISTICS ===
CRS Averages (Last 5 draws each):
  - CEC: {stats['averages']['cec']['crs']} CRS (from {stats['averages']['cec']['count']} draws)
  - PNP: {stats['averages']['pnp']['crs']} CRS (from {stats['averages']['pnp']['count']} draws)
  - French: {stats['averages']['french']['crs']} CRS (from {stats['averages']['french']['count']} draws)
  - Healthcare: {stats['averages']['healthcare']['crs']} CRS (from {stats['averages']['healthcare']['count']} draws)

CRS Trend: {stats['trend']['direction'].upper()} (slope: {stats['trend']['slope']})
Pool Pressure: {stats['pool_analysis']['pressure_percent']}% above 500 CRS ({stats['pool_analysis']['pressure_level']})
Candidates above 500: {stats['pool_analysis']['above_500']:,}

Draw Frequency (last 20 draws):
  - CEC: {stats['draw_frequency']['cec']}%
  - PNP: {stats['draw_frequency']['pnp']}%
  - French: {stats['draw_frequency']['french']}%
  - Healthcare: {stats['draw_frequency']['healthcare']}%

Bounds: Highest {stats['bounds']['highest_recent']}, Lowest {stats['bounds']['lowest_recent']} (excl. PNP)

=== YOUR TASK ===
Based ONLY on the data above, provide predictions. Return valid JSON:

{{
  "predictions": {{
    "CEC": {{
      "cutoff_low": <number based on trend>,
      "cutoff_high": <number based on trend>,
      "confidence": {stats['confidence']['cec']},
      "next_expected": "<days estimate>",
      "ita_estimate": {stats['averages']['cec']['itas']},
      "reasoning": "<1 sentence based on data>"
    }},
    "PNP": {{
      "cutoff_low": 700,
      "cutoff_high": 750,
      "confidence": {stats['confidence']['pnp']},
      "next_expected": "3-5 days",
      "ita_estimate": {stats['averages']['pnp']['itas']},
      "reasoning": "PNP always requires nomination (+600 CRS boost)"
    }},
    "French": {{
      "cutoff_low": <number>,
      "cutoff_high": <number>,
      "confidence": {stats['confidence']['french']},
      "next_expected": "<estimate>",
      "ita_estimate": {stats['averages']['french']['itas']},
      "reasoning": "<based on data>"
    }},
    "Healthcare": {{
      "cutoff_low": <number>,
      "cutoff_high": <number>,
      "confidence": {stats['confidence']['healthcare']},
      "next_expected": "<estimate>",
      "ita_estimate": {stats['averages']['healthcare']['itas']},
      "reasoning": "<based on data>"
    }}
  }},
  "trend_analysis": "<2-3 sentences explaining the {stats['trend']['direction']} trend>",
  "user_guidance": {{
    "520_plus": "Excellent chances - likely ITA in next CEC draw",
    "500_519": "Good chances - within typical CEC range",
    "450_499": "Consider French test or category-based eligibility",
    "below_450": "Focus on PNP nomination or improving CRS"
  }}
}}

RULES:
1. Use ONLY the statistics provided - do not invent numbers
2. Confidence scores are pre-calculated - use them as given
3. Base cutoff predictions on averages +/- 10 points based on trend
4. If trend is 'declining', predict lower end; if 'rising', predict higher end"""


@app.route('/api/crs-prediction', methods=['POST'])
def api_crs_prediction():
    """
    CRS Prediction API - 3-Layer Architecture
    Layer 1: Official Data -> Layer 2: Statistics -> Layer 3: Gemini Analysis
    """
    try:
        # LAYER 1: Load official IRCC data
        official_data = load_official_data()
        if not official_data:
            return jsonify({"success": False, "error": "Could not load draw data"}), 500

        # LAYER 2: Calculate statistics
        statistics = calculate_statistics(official_data)

        # LAYER 3: Get Gemini predictions (if API key available)
        gemini_predictions = None
        if GEMINI_API_KEY:
            try:
                prompt = build_gemini_prompt(official_data, statistics)

                gemini_url = f"{GEMINI_URL}/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {'temperature': 0.2, 'maxOutputTokens': 2000}
                }

                response = requests.post(gemini_url, json=payload, timeout=60)
                if response.ok:
                    result = response.json()
                    content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

                    # Parse JSON from Gemini response
                    content = content.replace('```json', '').replace('```', '').strip()
                    import re
                    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)

                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start >= 0 and end > start:
                        gemini_predictions = json.loads(content[start:end])
            except Exception as e:
                print(f"Gemini API error (using fallback): {e}")

        # Build final response - combining all layers
        avg = statistics['averages']
        trend = statistics['trend']

        # Fallback predictions if Gemini fails
        trend_adjust = -5 if trend['direction'] == 'declining' else (5 if trend['direction'] == 'rising' else 0)

        fallback_predictions = {
            'CEC': {
                'cutoff_low': avg['cec']['crs'] - 10 + trend_adjust,
                'cutoff_high': avg['cec']['crs'] + 5 + trend_adjust,
                'confidence': statistics['confidence']['cec'],
                'next_expected': '3-7 days',
                'ita_estimate': avg['cec']['itas'],
                'reasoning': f"Based on {avg['cec']['count']} recent CEC draws averaging {avg['cec']['crs']} CRS"
            },
            'PNP': {
                'cutoff_low': 700,
                'cutoff_high': 750,
                'confidence': statistics['confidence']['pnp'],
                'next_expected': '3-5 days',
                'ita_estimate': avg['pnp']['itas'],
                'reasoning': 'PNP requires provincial nomination (+600 CRS boost)'
            },
            'French': {
                'cutoff_low': max(365, avg['french']['crs'] - 20) if avg['french']['crs'] > 0 else 380,
                'cutoff_high': avg['french']['crs'] + 20 if avg['french']['crs'] > 0 else 420,
                'confidence': statistics['confidence']['french'],
                'next_expected': '1-2 weeks',
                'ita_estimate': avg['french']['itas'] or 5000,
                'reasoning': f"Based on {avg['french']['count']} French draws in recent history"
            },
            'Healthcare': {
                'cutoff_low': avg['healthcare']['crs'] - 15 if avg['healthcare']['crs'] > 0 else 460,
                'cutoff_high': avg['healthcare']['crs'] + 15 if avg['healthcare']['crs'] > 0 else 490,
                'confidence': statistics['confidence']['healthcare'],
                'next_expected': '1-3 weeks',
                'ita_estimate': avg['healthcare']['itas'] or 1500,
                'reasoning': f"Based on {avg['healthcare']['count']} Healthcare draws"
            }
        }

        # Use Gemini predictions if available, otherwise fallback
        predictions = gemini_predictions.get('predictions', fallback_predictions) if gemini_predictions else fallback_predictions

        final_response = {
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'data_source': 'IRCC Official',

            # FACTS (Layer 1)
            'current_conditions': {
                'pool_size': official_data['total_pool_size'],
                'pool_last_updated': official_data['last_updated'][:10],
                'candidates_above_500': statistics['pool_analysis']['above_500'],
                'pool_pressure': f"{statistics['pool_analysis']['pressure_level']} ({statistics['pool_analysis']['pressure_percent']}%)",
                'trend': statistics['trend']['direction'],
                'trend_slope': statistics['trend']['slope']
            },

            # STATISTICS (Layer 2)
            'statistics': {
                'averages': statistics['averages'],
                'bounds': statistics['bounds'],
                'draw_frequency': statistics['draw_frequency']
            },

            # PREDICTIONS (Layer 3)
            'predictions': predictions,

            # Analysis from Gemini or fallback
            'trend_analysis': gemini_predictions.get('trend_analysis',
                f"CRS scores are {trend['direction']} with a slope of {trend['slope']}. "
                f"Pool pressure is {statistics['pool_analysis']['pressure_level'].lower()} at {statistics['pool_analysis']['pressure_percent']}%.") if gemini_predictions else f"CRS trend is {trend['direction']}. Pool pressure: {statistics['pool_analysis']['pressure_level']}.",

            'user_guidance': gemini_predictions.get('user_guidance', {
                '520_plus': 'Excellent chances - likely ITA in next CEC draw',
                '500_519': 'Good chances - within typical CEC range',
                '450_499': 'Consider French test or category-based eligibility',
                'below_450': 'Focus on PNP nomination or improving CRS'
            }) if gemini_predictions else {
                '520_plus': 'Excellent chances - likely ITA in next CEC draw',
                '500_519': 'Good chances - within typical CEC range',
                '450_499': 'Consider French test or category-based eligibility',
                'below_450': 'Focus on PNP nomination or improving CRS'
            },

            # Recent draws for display
            'recent_draws': official_data['draws'][:5]
        }

        return jsonify(final_response)

    except Exception as e:
        print(f"CRS prediction API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tools/immigration-targets')
def immigration_targets():
    """Immigration Targets page - Levels Plan data"""
    return render_template('immigration_targets.html')


@app.route('/tools/noc-finder')
def noc_finder():
    """NOC Code Finder - Search occupation codes"""
    return render_template('noc_finder.html')


@app.route('/tools/language-converter')
def language_converter():
    """Language Score Converter - IELTS/CELPIP/TEF to CLB"""
    return render_template('language_converter.html')


@app.route('/tools/points-simulator')
def points_simulator():
    """Points Improvement Simulator"""
    return render_template('points_simulator.html')


@app.route('/tools/eligibility-checker')
def eligibility_checker():
    """Eligibility Checker for immigration programs"""
    return render_template('eligibility_checker.html')


@app.route('/tools/document-checklist')
def document_checklist():
    """Document Checklist Generator"""
    return render_template('document_checklist.html')


@app.route('/tools/cost-calculator')
def cost_calculator():
    """Immigration Cost Calculator"""
    return render_template('cost_calculator.html')


@app.route('/tools/cost-of-living')
def cost_of_living():
    """Cost of Living Comparison by City"""
    return render_template('cost_of_living.html')


@app.route('/tools/pool-stats')
def pool_stats():
    """Express Entry Pool Statistics"""
    return render_template('pool_stats.html')


@app.route('/api/draws')
def api_draws():
    """API endpoint for Express Entry draws data"""
    try:
        draws_file = os.path.join(os.path.dirname(__file__), 'data', 'draws.json')
        if os.path.exists(draws_file):
            with open(draws_file, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        return jsonify({"draws": [], "pool_stats": {}, "error": "No data available"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tools/pnp-calculator')
@app.route('/tools/pnp-calculator/<province_id>')
def pnp_calculator(province_id=None):
    """Provincial Nominee Program Calculator - Points & Eligibility"""
    return render_template('pnp_calculator.html', initial_province=province_id)


@app.route('/tools/lico-calculator')
def lico_calculator():
    """LICO Calculator - Income requirements for PGP sponsorship"""
    return render_template('lico_calculator.html')


@app.route('/tools/physical-presence-calculator')
def physical_presence_calculator():
    """Physical Presence Calculator - Citizenship requirements"""
    return render_template('physical_presence_calculator.html')


@app.route('/tools/student-solvency')
def student_solvency():
    """Student Solvency Validator - Study permit financial requirements"""
    return render_template('student_solvency.html')


@app.route('/tools/dli-search')
def dli_search():
    """DLI Search - Find PGWP-eligible schools"""
    return render_template('dli_search.html')


@app.route('/api/processing-times')
def api_processing_times():
    """API endpoint for processing times data"""
    try:
        from ircc_scraper import get_cached_processing_times
        data = get_cached_processing_times()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/express-entry-draws')
def api_express_entry_draws():
    """API endpoint for Express Entry draws"""
    try:
        from ircc_scraper import get_cached_processing_times
        data = get_cached_processing_times()
        return jsonify({
            'draws': data.get('express_entry', {}).get('draws', []),
            'average_crs': data.get('express_entry', {}).get('average_crs', 520),
            'predicted_cutoff': data.get('express_entry', {}).get('predicted_next_cutoff', 520),
            'last_updated': data.get('last_updated')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    # Normalize caption formats for dashboard display
    for r in results:
        if not r.get('captions'):
            r['captions'] = {
                'instagram': r.get('caption_instagram', ''),
                'facebook': r.get('caption_facebook', ''),
                'linkedin': r.get('caption_linkedin', ''),
                'twitter': r.get('caption_twitter', ''),
            }
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
    sort = request.args.get('sort', 'newest')

    if category:
        all_articles = [a for a in all_articles if a.get('category') == category]

    # Sort by date
    if sort == 'oldest':
        all_articles = sorted(all_articles, key=lambda x: x.get('created_at', ''), reverse=False)
    else:  # newest first (default)
        all_articles = sorted(all_articles, key=lambda x: x.get('created_at', ''), reverse=True)

    return render_template('articles.html', articles=all_articles, category=category, sort=sort)


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
    import time

    # Try up to 2 times to load articles (in case of cold start/race condition)
    for attempt in range(2):
        all_articles = load_articles()

        # Find article by slug or ID
        article = None
        for a in all_articles:
            if a.get('slug') == slug or a.get('id') == slug:
                article = a
                break

        if article:
            break

        # If not found on first attempt, wait briefly and retry (cold start scenario)
        if attempt == 0 and not all_articles:
            time.sleep(0.5)  # Brief wait for API response

    if not article:
        # Return a proper 404 page instead of plain text
        return render_template('404.html', message=f"Article '{slug}' not found"), 404

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
    # Check MongoDB connection and article count
    mongodb_status = "disconnected"
    mongodb_articles = 0
    try:
        articles_col = get_articles_collection()
        if articles_col is not None:
            mongodb_articles = articles_col.count_documents({})
            mongodb_status = "connected"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "service": "Philata Content Hub",
        "version": "1.2",
        "timestamp": datetime.now().isoformat(),
        "mongodb": {
            "status": mongodb_status,
            "articles_count": mongodb_articles
        }
    })


@app.route('/api/migrate-to-mongodb', methods=['POST'])
def migrate_to_mongodb():
    """One-time migration: Copy existing articles from POST API to MongoDB"""
    data = request.get_json() or {}
    password = data.get('password', request.args.get('p', ''))

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        articles_col = get_articles_collection()
        if articles_col is None:
            return jsonify({'error': 'MongoDB not connected'}), 500

        # Fetch from POST API
        response = requests.get(f"{POST_API_URL}/results/list", timeout=30)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch from POST API'}), 500

        data = response.json()
        raw_results = data if isinstance(data, list) else data.get('results', [])

        migrated = 0
        skipped = 0
        for article in raw_results:
            if not article.get('full_article') or len(article.get('full_article', '')) < 200:
                skipped += 1
                continue

            slug = article.get('slug') or create_slug(article.get('title', ''))
            article['slug'] = slug

            # Upsert to MongoDB
            result = articles_col.update_one(
                {'slug': slug},
                {'$set': article},
                upsert=True
            )
            if result.upserted_id or result.modified_count:
                migrated += 1
            else:
                skipped += 1

        return jsonify({
            'success': True,
            'migrated': migrated,
            'skipped': skipped,
            'total_in_api': len(raw_results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
@rate_limit(max_requests=60, window_seconds=60)  # 60 requests per minute
def add_article():
    """
    Add a new article from n8n workflow (enhanced endpoint).
    Supports: slug, charts, verification, sources, SEO metadata.
    """
    try:
        data = request.get_json()

        # Input validation
        is_valid, error = validate_article_data(data)
        if not is_valid:
            return jsonify({'error': error}), 400

        results = load_results()

        # Use provided slug or generate from title
        slug = data.get('slug') or create_slug(data.get('title', ''))

        # Generate unique ID - use track, fallback to category, then 'content'
        track = data.get('track') or data.get('category') or 'content'
        content_id = f"{track}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(results)}"

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
            "image_url": convert_image_url(data.get('image_url', '')),  # Branded image for social media
            "featured_image": convert_image_url(data.get('featured_image', '')),  # Raw AI image for article hero
            "filename": data.get('filename', ''),
            "image_credit": data.get('image_credit'),

            # Social media captions - normalize both nested and flat formats
            "captions": data.get('captions', {}) if data.get('captions') else {
                'instagram': data.get('caption_instagram', ''),
                'facebook': data.get('caption_facebook', ''),
                'linkedin': data.get('caption_linkedin', ''),
                'twitter': data.get('caption_twitter', ''),
            },

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
            "created_at": eastern_now().strftime('%Y-%m-%dT%H:%M:%S'),
            "approved_at": None,
            "posted_at": None
        }

        results.insert(0, article)
        save_results(results)

        # Save to MongoDB for persistent storage
        try:
            articles_col = get_articles_collection()
            if articles_col is not None:
                # Use upsert to avoid duplicates (by slug)
                articles_col.update_one(
                    {'slug': slug},
                    {'$set': article},
                    upsert=True
                )
                print(f"   MongoDB: Article saved with slug '{slug}'")
        except Exception as mongo_err:
            print(f"   ⚠️ MongoDB save failed: {mongo_err}")

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
                "featured_image": article.get('featured_image', ''),
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


@app.route('/api/articles/update-image', methods=['POST'])
def update_article_image():
    """Update an existing article's image_url"""
    try:
        data = request.get_json()
        slug = data.get('slug', '')
        image_url = data.get('image_url', '')

        if not slug or not image_url:
            return jsonify({"success": False, "error": "slug and image_url required"}), 400

        results = load_results()
        updated = False

        for i, article in enumerate(results):
            if article.get('slug') == slug:
                results[i]['image_url'] = image_url
                updated = True
                print(f"✅ Updated image for article: {slug}")
                break

        if updated:
            save_results(results)
            # Also update in MongoDB
            try:
                articles_col = get_articles_collection()
                if articles_col is not None:
                    articles_col.update_one(
                        {'slug': slug},
                        {'$set': {'image_url': image_url}}
                    )
                    print(f"   MongoDB: Updated image for '{slug}'")
            except Exception as mongo_err:
                print(f"   ⚠️ MongoDB update failed: {mongo_err}")
            return jsonify({"success": True, "slug": slug, "image_url": image_url})
        else:
            return jsonify({"success": False, "error": "Article not found"}), 404

    except Exception as e:
        print(f"❌ Update image failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/articles/check', methods=['POST'])
def check_article_duplicate():
    """
    Comprehensive duplicate check using:
    - Exact slug match
    - Source URL match
    - Key numbers extraction (CRS, ITAs, dates, amounts)
    - Stat cards comparison
    - Content fingerprinting
    """
    import re
    from datetime import datetime, timedelta

    def extract_numbers(text):
        """Extract all significant numbers from text (CRS scores, ITA counts, dates, etc.)"""
        if not text:
            return set()
        # Find numbers with context (e.g., "500 CRS", "5,000 ITAs", "January 15")
        patterns = [
            r'\b(\d{3})\s*(?:CRS|points?|score)',  # CRS scores (3 digits)
            r'\b(\d{1,3}(?:,\d{3})+|\d{4,})\s*(?:ITAs?|invitations?|applicants?|people|candidates?)',  # Large numbers
            r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December))',  # Dates
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}',  # Dates alt
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Dollar amounts
            r'\b(\d+(?:\.\d+)?)\s*(?:percent|%)',  # Percentages
            r'#\s*(\d+)',  # Draw numbers
            r'\b(\d{4})\b',  # Years
        ]
        numbers = set()
        text_lower = text.lower()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for m in matches:
                # Normalize: remove commas, lowercase
                normalized = str(m).replace(',', '').lower().strip()
                if normalized and len(normalized) >= 2:
                    numbers.add(normalized)
        return numbers

    def extract_stat_values(stat_cards):
        """Extract values from stat cards"""
        if not stat_cards:
            return set()
        values = set()
        for card in stat_cards:
            val = str(card.get('value', '')).replace(',', '').lower().strip()
            if val:
                values.add(val)
        return values

    def normalize_url(url):
        """Normalize URL for comparison"""
        if not url:
            return ''
        url = url.lower().strip()
        # Remove protocol, www, trailing slashes
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        return url

    def is_generic_index_url(url):
        """Check if URL is a generic index/listing page that shouldn't be used for duplicate matching"""
        if not url:
            return True
        url_lower = url.lower()
        # Generic patterns that indicate index/listing pages
        generic_patterns = [
            '/index.aspx', '/index.html', '/index.php', '/index.htm',
            '/pages/index', '/decisions/pages/', '/newsroom', '/news-releases',
            '/media-room', '/press-releases', '/announcements',
            'canada.ca/en/immigration', 'canada.ca/fr/immigration',  # Generic IRCC pages
            '/search?', '/results?', '/list?',  # Search/list pages
        ]
        for pattern in generic_patterns:
            if pattern in url_lower:
                return True
        # Also check if URL ends with just a domain or section (no specific article ID)
        if url_lower.endswith(('.gc.ca', '.ca/en', '.ca/fr', '/en', '/fr')):
            return True
        return False

    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        slug = data.get('slug', '')
        source_url = data.get('source_url', '')
        full_article = data.get('full_article', '')
        stat_cards = data.get('stat_cards', [])
        summary = data.get('summary', '')

        if not title:
            return jsonify({"exists": False, "reason": "No title provided"})

        results = load_results()

        # Extract key data from new article
        new_numbers = extract_numbers(title + ' ' + summary + ' ' + full_article)
        new_stats = extract_stat_values(stat_cards)
        new_source = normalize_url(source_url)
        new_all_numbers = new_numbers | new_stats

        print(f"🔍 Checking duplicate for: {title[:50]}...")
        print(f"   Key numbers: {new_all_numbers}")

        for article in results:
            existing_id = article.get('id', '')
            existing_title = article.get('title', '')
            existing_slug = article.get('slug', '')
            existing_source = normalize_url(article.get('source_url', ''))
            existing_article = article.get('full_article', '')
            existing_stats = article.get('stat_cards', [])
            existing_summary = article.get('summary', '')

            # 1. Exact slug match
            if slug and existing_slug == slug:
                return jsonify({
                    "exists": True,
                    "reason": "slug_match",
                    "existing_id": existing_id,
                    "existing_title": existing_title,
                    "created_at": article.get('created_at')
                })

            # 2. Same source URL (same news article) - but skip generic index pages
            if new_source and existing_source and new_source == existing_source:
                # Don't match on generic index/listing pages
                if not is_generic_index_url(source_url):
                    return jsonify({
                        "exists": True,
                        "reason": "source_url_match",
                        "existing_id": existing_id,
                        "existing_title": existing_title,
                        "created_at": article.get('created_at')
                    })

            # 3. Extract numbers from existing article
            existing_numbers = extract_numbers(existing_title + ' ' + existing_summary + ' ' + existing_article)
            existing_stat_values = extract_stat_values(existing_stats)
            existing_all_numbers = existing_numbers | existing_stat_values

            # Determine if this is a cross-pipeline check (media vs news)
            new_pipeline = data.get('pipeline', data.get('category', ''))
            existing_pipeline = article.get('pipeline', article.get('category', ''))

            # News and media pipelines cover the same stories from different sources
            news_types = {'news', 'breaking', 'breaking_news'}
            media_types = {'media', 'magazine'}
            is_cross_pipeline = (
                (new_pipeline in news_types and existing_pipeline in media_types) or
                (new_pipeline in media_types and existing_pipeline in news_types)
            )

            # 4. Key numbers match - MORE AGGRESSIVE for cross-pipeline
            if len(new_all_numbers) >= 2 and len(existing_all_numbers) >= 2:
                matching_numbers = new_all_numbers & existing_all_numbers
                # Filter to only meaningful matches (exclude common years)
                meaningful_matches = {n for n in matching_numbers if not (n.isdigit() and len(n) == 4 and 2020 <= int(n) <= 2030)}

                # Lower threshold for cross-pipeline (media reporting on same news)
                # 2 matching numbers for cross-pipeline, 3 for same pipeline
                min_matches = 2 if is_cross_pipeline else 3

                if len(meaningful_matches) >= min_matches:
                    return jsonify({
                        "exists": True,
                        "reason": "cross_pipeline_match" if is_cross_pipeline else "key_numbers_match",
                        "matching_numbers": list(meaningful_matches)[:5],
                        "existing_id": existing_id,
                        "existing_title": existing_title,
                        "existing_pipeline": existing_pipeline,
                        "created_at": article.get('created_at')
                    })

            # 5. Title word similarity
            def normalize_text(t):
                t = re.sub(r'[^\w\s]', '', t.lower())
                # Remove common words that don't help identify duplicates
                stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
                words = set(t.split()) - stopwords
                return words

            new_words = normalize_text(title)
            existing_words = normalize_text(existing_title)

            if len(new_words) >= 3 and len(existing_words) >= 3:
                overlap = len(new_words & existing_words) / max(len(new_words), 1)

                # Lower threshold for cross-pipeline (60%) vs same pipeline (70%)
                threshold = 0.60 if is_cross_pipeline else 0.70

                if overlap >= threshold:
                    # For cross-pipeline, require just 1 matching number
                    # For same pipeline, require at least 1 matching number
                    matching_nums = new_all_numbers & existing_all_numbers
                    meaningful_nums = {n for n in matching_nums if not (n.isdigit() and len(n) == 4 and 2020 <= int(n) <= 2030)}

                    if meaningful_nums:
                        return jsonify({
                            "exists": True,
                            "reason": "cross_pipeline_title_match" if is_cross_pipeline else "title_and_numbers_match",
                            "similarity": round(overlap * 100),
                            "matching_numbers": list(meaningful_nums)[:3],
                            "existing_id": existing_id,
                            "existing_title": existing_title,
                            "existing_pipeline": existing_pipeline,
                            "created_at": article.get('created_at')
                        })

        return jsonify({"exists": False})

    except Exception as e:
        print(f"❌ Duplicate check failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"exists": False, "error": str(e)})


@app.route('/api/results', methods=['POST'])
@rate_limit(max_requests=60, window_seconds=60)  # 60 requests per minute
def add_result():
    """Add a new result from n8n workflow (legacy endpoint)"""
    try:
        data = request.get_json()

        # Basic validation
        if not data or not data.get('title'):
            return jsonify({'error': 'Missing required field: title'}), 400

        results = load_results()

        # Generate unique ID - use track, fallback to category, then 'content'
        track = data.get('track') or data.get('category') or 'content'
        content_id = f"{track}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(results)}"

        result = {
            "id": content_id,
            "title": data.get('title', ''),
            "track": track,
            "category": data.get('category') or track,
            "content_type": data.get('content_type', 'news'),
            "image_url": convert_image_url(data.get('image_url', '')),
            "filename": data.get('filename', ''),
            "captions": data.get('captions', {}) if data.get('captions') else {
                'instagram': data.get('caption_instagram', ''),
                'facebook': data.get('caption_facebook', ''),
                'linkedin': data.get('caption_linkedin', ''),
                'twitter': data.get('caption_twitter', ''),
            },
            "full_article": data.get('full_article', ''),
            "source": data.get('source', ''),
            "source_url": data.get('source_url', ''),
            "official_source_url": data.get('official_source_url'),
            "status": "pending",  # pending, approved, rejected, posted
            "created_at": eastern_now().strftime('%Y-%m-%dT%H:%M:%S'),
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


@app.route('/api/results/<content_id>/delete', methods=['DELETE', 'POST'])
def delete_content(content_id):
    """Permanently delete content"""
    try:
        results = load_results()
        original_count = len(results)

        # Find the article to get slug for MongoDB deletion
        deleted_slug = None
        for r in results:
            if r.get('id') == content_id:
                deleted_slug = r.get('slug')
                break

        # Filter out the article to delete
        results = [r for r in results if r.get('id') != content_id]

        if len(results) == original_count:
            return jsonify({"success": False, "error": "Article not found"}), 404

        save_results(results)

        # Also delete from MongoDB
        if deleted_slug:
            try:
                articles_col = get_articles_collection()
                if articles_col is not None:
                    articles_col.delete_one({'slug': deleted_slug})
                    print(f"   MongoDB: Deleted article '{deleted_slug}'")
            except Exception as mongo_err:
                print(f"   ⚠️ MongoDB delete failed: {mongo_err}")

        return jsonify({"success": True, "message": f"Article {content_id} deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/articles/delete-by-slug', methods=['POST'])
def delete_article_by_slug():
    """Delete article by slug (admin endpoint)"""
    try:
        data = request.get_json()
        slug = data.get('slug', '')

        if not slug:
            return jsonify({"success": False, "error": "slug required"}), 400

        # Delete from MongoDB
        deleted_mongo = False
        try:
            articles_col = get_articles_collection()
            if articles_col is not None:
                result = articles_col.delete_one({'slug': slug})
                deleted_mongo = result.deleted_count > 0
                print(f"MongoDB: Deleted {result.deleted_count} article(s) with slug '{slug}'")
        except Exception as mongo_err:
            print(f"MongoDB delete error: {mongo_err}")

        # Also delete from local results.json
        results = load_results()
        original_count = len(results)
        results = [r for r in results if r.get('slug') != slug]
        deleted_local = len(results) < original_count

        if deleted_local:
            save_results(results)

        if deleted_mongo or deleted_local:
            return jsonify({
                "success": True,
                "message": f"Deleted article '{slug}'",
                "deleted_from_mongo": deleted_mongo,
                "deleted_from_local": deleted_local
            })
        else:
            return jsonify({"success": False, "error": f"Article '{slug}' not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/articles/clear-all', methods=['POST'])
def clear_all_articles():
    """Clear all articles from MongoDB and local storage (admin endpoint)"""
    try:
        deleted_mongo = 0
        deleted_local = 0

        # Clear MongoDB
        try:
            articles_col = get_articles_collection()
            if articles_col is not None:
                result = articles_col.delete_many({})
                deleted_mongo = result.deleted_count
                print(f"MongoDB: Deleted {deleted_mongo} articles")
        except Exception as mongo_err:
            print(f"MongoDB clear error: {mongo_err}")

        # Clear local results.json
        results = load_results()
        deleted_local = len(results)
        save_results([])

        return jsonify({
            "success": True,
            "message": "All articles cleared",
            "deleted_from_mongo": deleted_mongo,
            "deleted_from_local": deleted_local
        })

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


# =============================================================================
# CAPTION GENERATION (matching local caption_generator.py)
# =============================================================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def fix_caption_formatting(data: dict, article_url: str) -> dict:
    """Fix newline formatting in captions to ensure proper line breaks"""
    import re
    if 'captions' not in data:
        return data

    for platform, caption in data['captions'].items():
        if not caption:
            continue

        # Convert escaped newlines to actual newlines
        caption = caption.replace('\\n', '\n')

        # Fix missing newlines after headline (before 📖)
        caption = re.sub(r'([!?🇫🇷🇨🇦])\s*(📖)', r'\1\n\n\2', caption)

        # Fix missing newline after article URL
        caption = re.sub(r'(https://[^\s]+)([A-Z])', r'\1\n\n\2', caption)

        # Fix missing newlines before Key Changes/Key Statistics
        caption = re.sub(r'(\.)(\s*)(Key Changes:|Key Statistics:|Key statistics:)', r'\1\n\n\3', caption)

        # Fix newline after "Key Changes:" before first bullet
        caption = re.sub(r'(Key Changes:)\s*(📌)', r'\1\n\2', caption)
        caption = re.sub(r'(Key Statistics:|Key statistics:)\s*(📌|\*)', r'\1\n\2', caption)

        # Fix missing newlines before each 📌 bullet point
        caption = re.sub(r'(\.)(\s*)(📌)', r'\1\n\2\3', caption)

        # Fix missing newlines before "This means", "This affects", etc.
        caption = re.sub(r'(\.)(\s*)(This means|This affects|These changes|This indicates|This expansion)', r'\1\n\n\3', caption)

        # Fix missing newlines before timeline
        caption = re.sub(r'(\.)(\s*)(Timeline:|Applications submitted|The new rules|Effective)', r'\1\n\n\3', caption)

        # Fix missing newlines before 💡 Save
        caption = re.sub(r'([.!])(\s*)(💡)', r'\1\n\n\3', caption)

        # Fix missing newline between Save and Follow
        caption = re.sub(r'(Save this post!)(\s*)(🔔)', r'\1\n\3', caption)

        # Fix missing newlines before hashtags
        caption = re.sub(r'(updates!)(\s*)(#)', r'\1\n\n\3', caption)
        caption = re.sub(r'(@philata_ca)(\s*)(#)', r'\1\n\n\3', caption)
        caption = re.sub(r'(@philata\.ca[^#]*)(#)', r'\1\n\n\2', caption)
        caption = re.sub(r'([a-zA-Z0-9.!?)])(\s*)(#\w+)', r'\1\n\n\3', caption)

        # Consolidate hashtags into paragraph form
        def consolidate_hashtags(text):
            parts = re.split(r'(\n\n)(#\w+)', text, maxsplit=1)
            if len(parts) >= 3:
                pre_hashtags = parts[0] + parts[1]
                hashtag_section = parts[2] + ''.join(parts[3:]) if len(parts) > 3 else parts[2]
                hashtags_clean = re.sub(r'\s*\n+\s*', ' ', hashtag_section)
                hashtags_clean = re.sub(r'\s+', ' ', hashtags_clean)
                return pre_hashtags + hashtags_clean.strip()
            return text

        caption = consolidate_hashtags(caption)

        # Platform-specific formatting
        if platform == 'twitter':
            caption = re.sub(r'\s{2,}', '\n\n', caption)
            caption = re.sub(r'(https://[^\s]+)\s*(📌)', r'\1\n\n\2', caption)

        if platform == 'linkedin':
            caption = re.sub(r'(\.)(\s*)(Implications:|Business/Economic Impact:|Action items for professionals:|Action Items:)', r'\1\n\n\3', caption)
            caption = re.sub(r'(Implications:|Business/Economic Impact:|Action items for professionals:|Action Items:)\s*(\*|This)', r'\1\n\2', caption)
            caption = re.sub(r'(\.)(\s*)(\*\s+)', r'\1\n\3', caption)
            caption = re.sub(r'(\.)(\s*)(Save this post)', r'\1\n\n\3', caption)

        # Clean up multiple consecutive newlines (max 2)
        caption = re.sub(r'\n{3,}', '\n\n', caption)

        data['captions'][platform] = caption.strip()

    return data


def fallback_captions(article: dict, article_url: str) -> dict:
    """Generate detailed captions from article content if API fails"""
    title = article.get('title', 'Canadian Immigration Update')
    subtitle = article.get('subtitle', '')
    category = article.get('category', 'immigration').replace('_', ' ').title()

    instagram_caption = f"""🇨🇦 {title}

📖 For detailed article: {article_url}

{subtitle}

This is an important update for anyone following Canadian immigration policy. The changes announced will affect how applications are processed and who is eligible.

Key Changes:
📌 New requirements and eligibility criteria
📌 Updated processing timelines
📌 Impact on current and future applicants

Stay informed about how these changes may affect your immigration journey.

💡 Save this post!
🔔 Follow @philata.ca for updates!

#CanadaImmigration #IRCC #ImmigrationNews #ExpressEntry #PNP #Canada #Immigration #PRCanada #MoveToCanada #CanadaVisa #ImmigrationCanada #WorkInCanada #StudyInCanada #CanadaDream #NewToCanada #ImmigrationUpdate"""

    facebook_caption = f"""🇨🇦 {title}

📖 For detailed article: {article_url}

{subtitle}

This is an important update for anyone following Canadian immigration policy. The changes announced will affect how applications are processed and who is eligible.

Key Changes:
📌 New requirements and eligibility criteria
📌 Updated processing timelines
📌 Impact on current and future applicants

Stay informed about how these changes may affect your immigration journey.

💡 Save this post!
🔔 Follow @philata.ca for updates!

#CanadaImmigration #IRCC #ImmigrationNews #PRCanada #MoveToCanada #CanadaVisa #Immigration #Canada #ExpressEntry #PNP #WorkPermit #StudyInCanada"""

    linkedin_caption = f"""{title}

📖 For detailed article: {article_url}

{subtitle}

This development represents a significant update to Canadian immigration policy. Professionals and organizations should take note of the new requirements and timelines.

Key implications for the immigration sector and prospective applicants.

💡 Save this post!
🔔 Follow @philata.ca for updates!

#CanadaImmigration #IRCC #Immigration #Canada #HRNews #TalentAcquisition #GlobalMobility #WorkforcePlanning #InternationalHiring #CanadianBusiness"""

    twitter_caption = f"""🇨🇦 {title}

📖 Full article: {article_url}

📌 New policy changes announced
📌 Updated requirements and criteria
📌 Impact on applicants

This affects how applications are processed.

💡 Save & 🔔 Follow @philata_ca

#CanadaImmigration #IRCC #ExpressEntry #PRCanada #ImmigrationNews"""

    return {
        'captions': {
            'instagram': instagram_caption,
            'facebook': facebook_caption,
            'linkedin': linkedin_caption,
            'twitter': twitter_caption
        },
        'image_statement': title[:60] if len(title) <= 60 else title[:57] + '...',
        'image_subtext': category,
        'hashtag_sets': {
            'primary': ['#CanadaImmigration', '#ExpressEntry', '#IRCC', '#PRCanada', '#CanadaVisa'],
            'secondary': ['#MoveToCanada', '#ImmigrationNews', '#WorkInCanada', '#StudyInCanada', '#CanadaDream', '#NewToCanada', '#ImmigrationUpdate', '#CanadaNews']
        },
        'article_url': article_url,
        'generated_at': datetime.now().isoformat(),
        'fallback': True
    }


@app.route('/generate/captions', methods=['POST'])
def generate_captions():
    """
    Generate detailed social media captions matching local caption_generator.py.

    Request body:
    {
        "title": "Article title",
        "subtitle": "Article subtitle/summary",
        "category": "express_entry",
        "article_url": "https://philata.com/articles/...",
        "content_html": "Full article content for context",
        "key_stats": [{"value": "500", "label": "CRS Score"}]
    }
    """
    try:
        data = request.get_json()

        title = data.get('title', '')
        subtitle = data.get('subtitle', '')
        category = data.get('category', 'news')
        article_url = data.get('article_url', 'https://philata.com')
        content_html = data.get('content_html', '')[:3000]  # Limit content
        key_stats = data.get('key_stats', [])

        if not title:
            return jsonify({"success": False, "error": "Missing title"}), 400

        # Build the detailed prompt (matching caption_generator.py)
        prompt = f"""Generate detailed social media captions based on this immigration news article.

ARTICLE TITLE: {title}
SUBTITLE: {subtitle}
CATEGORY: {category}
ARTICLE URL: {article_url}

KEY STATISTICS:
{json.dumps(key_stats, indent=2)}

ARTICLE CONTENT (use this to create informative captions):
{content_html}

REQUIREMENTS:
1. Create DETAILED captions that explain the news - NOT generic messages
2. Include specific numbers, dates, and key facts from the article
3. Use relevant emojis throughout (Canadian flag sparingly)
4. DO NOT use abbreviations (apps, docs, grads, temps, info)
5. Write out full words always
6. Make captions informative enough that readers understand the news

CAPTION STRUCTURE FOR INSTAGRAM/FACEBOOK/LINKEDIN:
[Emoji] [Attention-grabbing headline]

(keep one empty line here)
📖 For detailed article: {article_url}

[2-3 sentences explaining the key news with specific numbers]

Key Changes:
📌 [Specific point 1 with numbers/dates]
📌 [Specific point 2 with numbers/dates]
📌 [Specific point 3 with numbers/dates]
📌 [Specific point 4 if applicable]

[What this means for applicants - 1-2 sentences]

[Timeline or deadline if applicable]

💡 Save this post!
🔔 Follow @philata.ca for updates!

[15-18 trending hashtags]

Return ONLY valid JSON:
{{
  "captions": {{
    "instagram": "1200-1800 characters. Follow the structure above. IMPORTANT: Keep one empty line after headline before the article link. Use 📌 emoji for each bullet point in Key Changes. End with 15-18 trending hashtags like #CanadaImmigration #ExpressEntry #IRCC #ImmigrationCanada #PRCanada #CanadaVisa #MoveToCanada #CanadianImmigration #ImmigrationNews #CanadaPR #WorkInCanada #StudyInCanada #CanadaDream #NewToCanada #ImmigrationUpdate #CanadaNews #VisaCanada #ImmigrantLife",

    "facebook": "1200-1800 characters. Same detailed structure as Instagram. IMPORTANT: Keep one empty line after headline before the article link. Use 📌 emoji for each bullet point. End with 10-12 relevant hashtags like #CanadaImmigration #IRCC #ImmigrationNews #PRCanada #MoveToCanada #CanadaVisa #Immigration #Canada #ExpressEntry #PNP #WorkPermit #StudyInCanada",

    "linkedin": "1000-1400 characters. Professional tone with:
      - Clear headline
      - One empty line then article link
      - Key statistics and implications
      - Business/economic impact
      - Action items for professionals
      - Save/Follow CTA at end
      - End with 8-10 professional hashtags like #CanadaImmigration #IRCC #Immigration #Canada #HRNews #TalentAcquisition #GlobalMobility #WorkforcePlanning #InternationalHiring #CanadianBusiness",

    "twitter": "DETAILED caption for Twitter/X Premium users. 500-800 characters. MUST be well-organized with bullet points:

      [Emoji] [Short punchy headline]

      📖 Full article: {article_url}

      📌 [Key point 1 with number/date]
      📌 [Key point 2 with number/date]
      📌 [Key point 3 with number/date]
      📌 [Key point 4 if applicable]

      [What this means - 1 short sentence]

      💡 Save & 🔔 Follow @philata_ca

      [5-8 hashtags like #CanadaImmigration #ExpressEntry #IRCC #PRCanada #ImmigrationNews]"
  }},

  "image_statement": "One powerful headline (max 10 words) with the KEY number",

  "image_subtext": "Secondary context line (max 6 words)",

  "hashtag_sets": {{
    "primary": ["#CanadaImmigration", "#IRCC", "#ExpressEntry", "#PRCanada", "#CanadaVisa"],
    "secondary": ["#MoveToCanada", "#ImmigrationNews", "#WorkInCanada", "#StudyInCanada", "#CanadaDream", "#NewToCanada", "#ImmigrationUpdate", "#CanadaNews"]
  }}
}}"""

        # Call Gemini API
        gemini_url = f"{GEMINI_URL}/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }],
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': 4000
            }
        }

        response = requests.post(gemini_url, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

        # Parse JSON response
        import re
        content = content.replace('```json', '').replace('```', '').strip()
        # Clean control characters
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)

        start = content.find('{')
        end = content.rfind('}') + 1

        if start >= 0 and end > start:
            try:
                caption_data = json.loads(content[start:end])
                caption_data['article_url'] = article_url
                caption_data['generated_at'] = datetime.now().isoformat()
                # Fix formatting
                caption_data = fix_caption_formatting(caption_data, article_url)

                return jsonify({
                    "success": True,
                    **caption_data
                })
            except json.JSONDecodeError:
                # Try more aggressive cleaning
                cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content[start:end])
                cleaned = cleaned.replace('\n', '\\n').replace('\r', '').replace('\t', ' ')
                caption_data = json.loads(cleaned)
                caption_data['article_url'] = article_url
                caption_data['generated_at'] = datetime.now().isoformat()
                caption_data = fix_caption_formatting(caption_data, article_url)

                return jsonify({
                    "success": True,
                    **caption_data
                })

        # Fallback if parsing fails
        fallback_data = fallback_captions({'title': title, 'subtitle': subtitle, 'category': category}, article_url)
        return jsonify({
            "success": True,
            **fallback_data
        })

    except Exception as e:
        print(f"Caption generation error: {e}")
        # Return fallback captions
        data = request.get_json() or {}
        fallback_data = fallback_captions({
            'title': data.get('title', 'Immigration Update'),
            'subtitle': data.get('subtitle', ''),
            'category': data.get('category', 'news')
        }, data.get('article_url', 'https://philata.com'))

        return jsonify({
            "success": True,
            **fallback_data,
            "error_info": str(e)
        })


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
# ADMIN LOGS (Password Protected)
# =============================================================================

def load_logs():
    """Load n8n logs from file"""
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_logs(logs):
    """Save n8n logs to file"""
    # Keep only last 500 logs
    logs = logs[-500:]
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

@app.route('/api/n8n/log', methods=['POST'])
def receive_n8n_log():
    """Receive logs from n8n workflow"""
    try:
        data = request.get_json()

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'pipeline': data.get('pipeline', 'unknown'),
            'action': data.get('action', 'unknown'),
            'title': data.get('title', ''),
            'status': data.get('status', 'info'),  # success, skipped, error, info
            'reason': data.get('reason', ''),
            'details': data.get('details', {}),
            'social_results': data.get('social_results', {})
        }

        logs = load_logs()
        logs.append(log_entry)
        save_logs(logs)

        return jsonify({'success': True, 'message': 'Log saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/logs')
def admin_logs():
    """Password-protected admin logs page"""
    password = request.args.get('p', '')

    if password != ADMIN_PASSWORD:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Access</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       display: flex; justify-content: center; align-items: center; height: 100vh;
                       background: #1a1a2e; margin: 0; }
                .login { background: #16213e; padding: 40px; border-radius: 12px; text-align: center; }
                h1 { color: #e94560; margin-bottom: 20px; }
                input { padding: 12px 20px; font-size: 16px; border: none; border-radius: 6px; margin-bottom: 15px; }
                button { background: #e94560; color: white; padding: 12px 30px; font-size: 16px;
                        border: none; border-radius: 6px; cursor: pointer; }
                button:hover { background: #ff6b6b; }
            </style>
        </head>
        <body>
            <div class="login">
                <h1>Admin Access</h1>
                <form method="GET">
                    <input type="password" name="p" placeholder="Password" required><br>
                    <button type="submit">Access Logs</button>
                </form>
            </div>
        </body>
        </html>
        ''', 401

    logs = load_logs()
    logs.reverse()  # Most recent first

    # Generate HTML for logs
    logs_html = ''
    for log in logs[:100]:  # Show last 100
        status_color = {
            'success': '#4ade80',
            'skipped': '#fbbf24',
            'error': '#f87171',
            'info': '#60a5fa'
        }.get(log.get('status', 'info'), '#60a5fa')

        social_html = ''
        if log.get('social_results'):
            for platform, result in log.get('social_results', {}).items():
                icon = '✓' if result.get('success') else '✗'
                social_html += f'<span class="social-badge" style="background: {"#4ade80" if result.get("success") else "#f87171"}">{platform}: {icon}</span> '

        logs_html += f'''
        <div class="log-entry" style="border-left: 4px solid {status_color}">
            <div class="log-header">
                <span class="timestamp">{log.get('timestamp', '')[:19]}</span>
                <span class="pipeline">{log.get('pipeline', '')}</span>
                <span class="status" style="background: {status_color}">{log.get('status', '').upper()}</span>
            </div>
            <div class="log-title">{log.get('title', 'No title')}</div>
            <div class="log-action"><strong>Action:</strong> {log.get('action', '')}</div>
            {f'<div class="log-reason"><strong>Reason:</strong> {log.get("reason", "")}</div>' if log.get('reason') else ''}
            {f'<div class="social-results">{social_html}</div>' if social_html else ''}
        </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>n8n Logs - Philata Admin</title>
        <meta name="robots" content="noindex, nofollow">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f0f23; color: #e0e0e0; margin: 0; padding: 20px;
            }}
            .header {{
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #333;
            }}
            h1 {{ color: #e94560; margin: 0; }}
            .stats {{ display: flex; gap: 20px; }}
            .stat {{ background: #1a1a2e; padding: 15px 25px; border-radius: 8px; text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .stat-label {{ font-size: 12px; color: #888; margin-top: 5px; }}
            .log-entry {{
                background: #1a1a2e; margin-bottom: 15px; padding: 20px;
                border-radius: 8px;
            }}
            .log-header {{
                display: flex; gap: 15px; align-items: center; margin-bottom: 10px;
            }}
            .timestamp {{ color: #888; font-size: 14px; }}
            .pipeline {{
                background: #3b82f6; color: white; padding: 4px 12px;
                border-radius: 4px; font-size: 12px; text-transform: uppercase;
            }}
            .status {{
                color: #0f0f23; padding: 4px 12px; border-radius: 4px;
                font-size: 12px; font-weight: bold;
            }}
            .log-title {{ font-size: 18px; font-weight: 600; margin-bottom: 10px; }}
            .log-action, .log-reason {{ font-size: 14px; color: #aaa; margin-bottom: 5px; }}
            .social-results {{ margin-top: 10px; }}
            .social-badge {{
                display: inline-block; padding: 4px 10px; border-radius: 4px;
                font-size: 12px; color: #0f0f23; margin-right: 8px;
            }}
            .refresh {{
                background: #3b82f6; color: white; padding: 10px 20px;
                border: none; border-radius: 6px; cursor: pointer; font-size: 14px;
            }}
            .refresh:hover {{ background: #2563eb; }}
            .empty {{ text-align: center; padding: 60px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>n8n Workflow Logs</h1>
            <div style="display: flex; gap: 15px; align-items: center;">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len([l for l in logs if l.get('status') == 'success'])}</div>
                        <div class="stat-label">Published</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #fbbf24">{len([l for l in logs if l.get('status') == 'skipped'])}</div>
                        <div class="stat-label">Skipped</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #f87171">{len([l for l in logs if l.get('status') == 'error'])}</div>
                        <div class="stat-label">Errors</div>
                    </div>
                </div>
                <button class="refresh" onclick="location.reload()">Refresh</button>
            </div>
        </div>

        {logs_html if logs_html else '<div class="empty"><h2>No logs yet</h2><p>Logs will appear here when n8n workflow runs</p></div>'}

        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/n8n/logs', methods=['GET'])
def get_logs_api():
    """API endpoint to get logs (requires password)"""
    password = request.args.get('p', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    logs = load_logs()
    logs.reverse()
    return jsonify({'logs': logs[:100]})

@app.route('/api/n8n/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all logs (requires password)"""
    password = request.args.get('p', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    save_logs([])
    return jsonify({'success': True, 'message': 'Logs cleared'})


@app.route('/api/clear-all', methods=['POST'])
def clear_all_data():
    """Clear ALL data - articles, results, logs, guides (requires password)"""
    data = request.get_json() or {}
    password = data.get('password', request.args.get('p', ''))

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized', 'hint': 'Send {"password": "your_password"}'}), 401

    cleared = []

    # Clear in-memory cache first
    global _memory_cache
    with _cache_lock:
        _memory_cache['articles'] = []
        _memory_cache['results'] = []
        _memory_cache['last_fetch'] = None
    cleared.append('memory_cache')

    # Clear all JSON data files
    data_files = {
        'results': RESULTS_FILE,
        'articles': ARTICLES_FILE,
        'approved': APPROVED_FILE,
        'guides': GUIDES_FILE,
        'logs': LOGS_FILE,
        'ai_decisions': AI_DECISIONS_FILE
    }

    for name, filepath in data_files.items():
        try:
            with open(filepath, 'w') as f:
                json.dump([], f)
            cleared.append(name)
        except Exception as e:
            pass

    # Also clear the backend queue and results
    try:
        requests.post(f"{POST_API_URL}/queue/clear", timeout=5)
        cleared.append('backend_queue')
    except:
        pass

    try:
        requests.post(f"{POST_API_URL}/results/clear", timeout=5)
        cleared.append('backend_results')
    except:
        pass

    try:
        requests.post(f"{POST_API_URL}/posting/reset", timeout=5)
        cleared.append('posting_status')
    except:
        pass

    # Clear MongoDB articles collection
    try:
        articles_col = get_articles_collection()
        if articles_col is not None:
            articles_col.delete_many({})
            cleared.append('mongodb_articles')
    except Exception as e:
        print(f"Error clearing MongoDB: {e}")

    return jsonify({
        'success': True,
        'message': 'All data cleared',
        'cleared': cleared
    })


# =============================================================================
# AI DECISION LOGGING (For Training)
# =============================================================================

def load_ai_decisions():
    """Load AI decision logs from file"""
    if os.path.exists(AI_DECISIONS_FILE):
        try:
            with open(AI_DECISIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_ai_decisions(decisions):
    """Save AI decision logs to file"""
    # Keep only last 1000 decisions for training data
    decisions = decisions[-1000:]
    with open(AI_DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2)

@app.route('/api/ai/log-decision', methods=['POST'])
def log_ai_decision():
    """Log AI approval/rejection decisions for training"""
    try:
        data = request.get_json()

        decision_entry = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'scraper_source': data.get('scraper_source', 'unknown'),
            'total_scraped': data.get('total_scraped', 0),
            'total_approved': data.get('total_approved', 0),
            'total_rejected': data.get('total_rejected', 0),
            'approved_items': data.get('approved_items', []),
            'rejected_items': data.get('rejected_items', []),
            'ai_raw_response': data.get('ai_raw_response', ''),
            'fallback_used': data.get('fallback_used', False),
            'fallback_source': data.get('fallback_source', ''),
            'fallback_items': data.get('fallback_items', [])
        }

        decisions = load_ai_decisions()
        decisions.append(decision_entry)
        save_ai_decisions(decisions)

        return jsonify({'success': True, 'message': 'AI decision logged'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/ai-decisions')
def admin_ai_decisions():
    """Password-protected AI decisions log page"""
    password = request.args.get('p', '')

    if password != ADMIN_PASSWORD:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Decisions - Admin</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       display: flex; justify-content: center; align-items: center; height: 100vh;
                       background: #1a1a2e; margin: 0; }
                .login { background: #16213e; padding: 40px; border-radius: 12px; text-align: center; }
                h1 { color: #e94560; margin-bottom: 20px; }
                input { padding: 12px 20px; font-size: 16px; border: none; border-radius: 6px; margin-bottom: 15px; }
                button { background: #e94560; color: white; padding: 12px 30px; font-size: 16px;
                        border: none; border-radius: 6px; cursor: pointer; }
                button:hover { background: #ff6b6b; }
            </style>
        </head>
        <body>
            <div class="login">
                <h1>AI Decisions Log</h1>
                <form method="GET">
                    <input type="password" name="p" placeholder="Password" required><br>
                    <button type="submit">View Decisions</button>
                </form>
            </div>
        </body>
        </html>
        ''', 401

    decisions = load_ai_decisions()
    decisions.reverse()  # Most recent first

    # Calculate stats
    total_approved = sum(d.get('total_approved', 0) for d in decisions)
    total_rejected = sum(d.get('total_rejected', 0) for d in decisions)
    total_scraped = sum(d.get('total_scraped', 0) for d in decisions)

    # Generate HTML
    decisions_html = ''
    for d in decisions[:50]:  # Show last 50 decisions
        approved_list = ''.join([
            f'<li class="approved"><strong>{item.get("title", "No title")}</strong><br><small>{item.get("reason", "")}</small></li>'
            for item in d.get('approved_items', [])
        ]) or '<li class="none">None</li>'

        rejected_list = ''.join([
            f'<li class="rejected"><strong>{item.get("title", "No title")}</strong><br><small>{item.get("reason", "")}</small></li>'
            for item in d.get('rejected_items', [])
        ]) or '<li class="none">None</li>'

        fallback_html = ''
        if d.get('fallback_used'):
            fallback_items = ''.join([
                f'<li>{item.get("title", "No title")}</li>'
                for item in d.get('fallback_items', [])
            ]) or '<li>None</li>'
            fallback_html = f'''
                <div class="fallback-section">
                    <h4>Fallback Used: {d.get('fallback_source', 'unknown')}</h4>
                    <ul>{fallback_items}</ul>
                </div>
            '''

        decisions_html += f'''
            <div class="decision-card">
                <div class="decision-header">
                    <span class="timestamp">{d.get('timestamp', '')[:19]}</span>
                    <span class="source">{d.get('scraper_source', 'unknown')}</span>
                    <span class="stats">
                        <span class="stat approved">{d.get('total_approved', 0)} approved</span>
                        <span class="stat rejected">{d.get('total_rejected', 0)} rejected</span>
                        <span class="stat total">/ {d.get('total_scraped', 0)} scraped</span>
                    </span>
                </div>
                <div class="decision-content">
                    <div class="column approved-column">
                        <h4>Approved</h4>
                        <ul>{approved_list}</ul>
                    </div>
                    <div class="column rejected-column">
                        <h4>Rejected</h4>
                        <ul>{rejected_list}</ul>
                    </div>
                </div>
                {fallback_html}
            </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Decisions Log - Philata Admin</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px;
            }}
            .header {{
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 20px; padding: 20px; background: #1e293b; border-radius: 12px;
            }}
            h1 {{ margin: 0; color: #f8fafc; }}
            .summary {{
                display: flex; gap: 20px;
            }}
            .summary-stat {{
                padding: 10px 20px; border-radius: 8px; text-align: center;
            }}
            .summary-stat.approved {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
            .summary-stat.rejected {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
            .summary-stat.total {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
            .summary-stat .number {{ font-size: 24px; font-weight: bold; }}
            .summary-stat .label {{ font-size: 12px; opacity: 0.8; }}

            .decision-card {{
                background: #1e293b; border-radius: 12px; margin-bottom: 16px;
                overflow: hidden;
            }}
            .decision-header {{
                display: flex; gap: 15px; align-items: center;
                padding: 15px 20px; background: #334155; border-bottom: 1px solid #475569;
            }}
            .timestamp {{ color: #94a3b8; font-size: 14px; }}
            .source {{
                background: #3b82f6; color: white; padding: 4px 10px;
                border-radius: 4px; font-size: 12px; font-weight: 500;
            }}
            .stats {{ margin-left: auto; display: flex; gap: 10px; }}
            .stat {{ font-size: 13px; padding: 4px 8px; border-radius: 4px; }}
            .stat.approved {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
            .stat.rejected {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
            .stat.total {{ color: #94a3b8; }}

            .decision-content {{
                display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px;
            }}
            .column h4 {{ margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .approved-column h4 {{ color: #4ade80; }}
            .rejected-column h4 {{ color: #f87171; }}
            .column ul {{ list-style: none; padding: 0; margin: 0; }}
            .column li {{
                padding: 10px; margin-bottom: 8px; border-radius: 6px; font-size: 14px;
            }}
            .column li.approved {{ background: rgba(34, 197, 94, 0.1); border-left: 3px solid #4ade80; }}
            .column li.rejected {{ background: rgba(239, 68, 68, 0.1); border-left: 3px solid #f87171; }}
            .column li.none {{ color: #64748b; font-style: italic; }}
            .column li small {{ color: #94a3b8; display: block; margin-top: 4px; }}

            .fallback-section {{
                padding: 15px 20px; background: rgba(147, 51, 234, 0.1);
                border-top: 1px solid #475569;
            }}
            .fallback-section h4 {{ color: #a78bfa; margin: 0 0 10px 0; font-size: 13px; }}
            .fallback-section ul {{ list-style: none; padding: 0; margin: 0; }}
            .fallback-section li {{ color: #c4b5fd; font-size: 13px; padding: 4px 0; }}

            .export-btn {{
                background: #3b82f6; color: white; border: none; padding: 10px 20px;
                border-radius: 6px; cursor: pointer; font-size: 14px;
            }}
            .export-btn:hover {{ background: #2563eb; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AI Decisions Log</h1>
            <div class="summary">
                <div class="summary-stat approved">
                    <div class="number">{total_approved}</div>
                    <div class="label">Total Approved</div>
                </div>
                <div class="summary-stat rejected">
                    <div class="number">{total_rejected}</div>
                    <div class="label">Total Rejected</div>
                </div>
                <div class="summary-stat total">
                    <div class="number">{total_scraped}</div>
                    <div class="label">Total Scraped</div>
                </div>
            </div>
            <a href="/api/ai/decisions?p={password}" class="export-btn">Export JSON</a>
        </div>
        {decisions_html if decisions_html else '<p style="text-align:center;color:#64748b;">No decisions logged yet</p>'}
    </body>
    </html>
    '''

@app.route('/api/ai/decisions', methods=['GET'])
def get_ai_decisions_api():
    """API endpoint to get AI decisions (requires password)"""
    password = request.args.get('p', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    decisions = load_ai_decisions()
    decisions.reverse()
    return jsonify({'decisions': decisions})

@app.route('/api/ai/decisions/clear', methods=['POST'])
def clear_ai_decisions():
    """Clear all AI decisions (requires password)"""
    password = request.args.get('p', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    save_ai_decisions([])
    return jsonify({'success': True, 'message': 'AI decisions cleared'})


# =============================================================================
# AI CHATBOT - Temporarily Disabled
# =============================================================================
# Chat functionality has been disabled. Re-enable when ready.


# =============================================================================
# SEO: SITEMAPS
# =============================================================================

@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    from flask import Response

    articles = load_articles()

    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''

    # Static pages
    static_pages = [
        ('/', '1.0', 'daily'),
        ('/articles', '0.9', 'hourly'),
        ('/dashboard', '0.8', 'hourly'),
        ('/guides', '0.8', 'weekly'),
        ('/learn', '0.7', 'weekly'),
        ('/tools/crs-calculator', '0.8', 'monthly'),
        ('/about', '0.5', 'monthly'),
        ('/contact', '0.5', 'monthly'),
    ]

    for path, priority, freq in static_pages:
        xml_content += f'''    <url>
        <loc>https://www.philata.com{path}</loc>
        <changefreq>{freq}</changefreq>
        <priority>{priority}</priority>
    </url>
'''

    # Article pages with news sitemap extension
    for article in articles[:100]:  # Limit to 100 most recent articles
        slug = article.get('slug') or article.get('id')
        created = article.get('created_at', '')[:10] if article.get('created_at') else ''
        title = article.get('title', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        image_url = article.get('featured_image') or article.get('image_url', '')

        xml_content += f'''    <url>
        <loc>https://www.philata.com/articles/{slug}</loc>
        <lastmod>{created}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
        <news:news>
            <news:publication>
                <news:name>Philata</news:name>
                <news:language>en</news:language>
            </news:publication>
            <news:publication_date>{created}</news:publication_date>
            <news:title>{title}</news:title>
        </news:news>
'''
        if image_url:
            xml_content += f'''        <image:image>
            <image:loc>{image_url}</image:loc>
            <image:title>{title}</image:title>
        </image:image>
'''
        xml_content += '''    </url>
'''

    xml_content += '</urlset>'

    return Response(xml_content, mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    from flask import Response

    content = '''User-agent: *
Allow: /

# Sitemaps
Sitemap: https://www.philata.com/sitemap.xml

# Disallow admin/API routes
Disallow: /api/
Disallow: /admin/

# Allow crawling of article pages
Allow: /articles/
Allow: /guides/
Allow: /learn/
'''
    return Response(content, mimetype='text/plain')


# =============================================================================
# ADMIN CMS ROUTES
# =============================================================================

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        if not getattr(current_user, 'is_admin', False):
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin, error = AdminUser.authenticate(username, password)
        if admin:
            login_user(admin, remember=True)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash(error or 'Invalid credentials', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
@admin_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard - overview of articles"""
    articles = load_articles_fresh()  # Fresh data for admin

    # Get stats
    total_articles = len(articles)
    categories = {}
    for article in articles:
        cat = article.get('category', 'uncategorized')
        categories[cat] = categories.get(cat, 0) + 1

    # Recent articles (last 10)
    recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:10]

    return render_template('admin/dashboard.html',
                          total_articles=total_articles,
                          categories=categories,
                          recent_articles=recent_articles,
                          admin=current_user)


@app.route('/admin/articles')
@admin_required
def admin_articles():
    """List all articles with search/filter"""
    all_articles = load_articles_fresh()  # Fresh data for admin

    # Get unique categories for filter dropdown (before filtering)
    all_categories = sorted(set(a.get('category', 'uncategorized') for a in all_articles))

    # Search/filter
    search = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')

    articles = all_articles
    if search:
        articles = [a for a in articles if search in a.get('title', '').lower()
                   or search in a.get('summary', '').lower()]

    if category_filter:
        articles = [a for a in articles if a.get('category') == category_filter]

    if status_filter == 'draft':
        articles = [a for a in articles if a.get('status') == 'draft']
    elif status_filter == 'published':
        articles = [a for a in articles if a.get('status', 'published') == 'published']

    # Sort by date (newest first)
    articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('admin/articles.html',
                          articles=paginated_articles,
                          total=total,
                          page=page,
                          per_page=per_page,
                          pages=(total + per_page - 1) // per_page,
                          categories=all_categories,
                          search=search,
                          category_filter=category_filter,
                          status_filter=status_filter)


@app.route('/admin/articles/new', methods=['GET', 'POST'])
@admin_required
def admin_article_new():
    """Create new article"""
    if request.method == 'POST':
        # Handle image upload if file provided
        image_url = request.form.get('image_url', '')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                import uuid
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(IMAGES_DIR, filename)
                file.save(filepath)
                image_url = f"/static/images/{filename}"

        data = {
            'title': request.form.get('title', '').strip(),
            'summary': request.form.get('summary', '').strip(),
            'content': request.form.get('content', ''),
            'category': request.form.get('category', 'news'),
            'source': request.form.get('source', 'Philata Editorial'),
            'source_url': request.form.get('source_url', ''),
            'image_url': image_url,
            'status': 'published' if request.form.get('action') == 'publish' else 'draft',
            'meta_description': request.form.get('meta_description', ''),
            'keywords': request.form.get('keywords', ''),
            'created_by': current_user.username,
            'created_at': datetime.utcnow().isoformat()
        }

        # Generate slug
        data['slug'] = create_slug(data['title'])

        # Validate
        is_valid, error = validate_article_data(data)
        if not is_valid:
            flash(f'Validation error: {error}', 'error')
            return render_template('admin/article_edit.html', article=data)

        # Save article
        results = load_results()
        data['id'] = f"admin_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        results.append(data)
        save_results(results)

        # Also save to MongoDB if connected
        articles_col = get_articles_collection()
        if articles_col is not None:
            try:
                articles_col.update_one(
                    {'slug': data['slug']},
                    {'$set': data},
                    upsert=True
                )
            except Exception as e:
                print(f"MongoDB save error: {e}")

        flash('Article created successfully!', 'success')
        return redirect(url_for('admin_articles'))

    return render_template('admin/article_edit.html', article=None)


@app.route('/admin/articles/<slug>/edit', methods=['GET', 'POST'])
@admin_required
def admin_article_edit(slug):
    """Edit existing article"""
    articles = load_articles()
    article = next((a for a in articles if a.get('slug') == slug), None)

    if not article:
        flash('Article not found', 'error')
        return redirect(url_for('admin_articles'))

    if request.method == 'POST':
        # Handle image upload if file provided
        image_url = request.form.get('image_url', '') or article.get('image_url', '')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                import uuid
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(IMAGES_DIR, filename)
                file.save(filepath)
                image_url = f"/static/images/{filename}"

        # Update article data
        article['title'] = request.form.get('title', '').strip()
        article['summary'] = request.form.get('summary', '').strip()
        article['content'] = request.form.get('content', '')
        article['category'] = request.form.get('category', 'news')
        article['source'] = request.form.get('source', '')
        article['source_url'] = request.form.get('source_url', '')
        article['image_url'] = image_url
        article['status'] = 'published' if request.form.get('action') == 'publish' else 'draft'
        article['meta_description'] = request.form.get('meta_description', '')
        article['keywords'] = request.form.get('keywords', '')
        article['updated_at'] = datetime.utcnow().isoformat()
        article['updated_by'] = current_user.username

        # Save to results
        results = load_results()
        for i, a in enumerate(results):
            if a.get('slug') == slug:
                results[i] = article
                break
        save_results(results)

        # Also update MongoDB
        articles_col = get_articles_collection()
        if articles_col is not None:
            try:
                articles_col.update_one(
                    {'slug': slug},
                    {'$set': article}
                )
            except Exception as e:
                print(f"MongoDB update error: {e}")

        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin_articles'))

    return render_template('admin/article_edit.html', article=article)


@app.route('/admin/articles/<slug>/delete', methods=['POST'])
@admin_required
def admin_article_delete(slug):
    """Delete article by slug or _id"""
    deleted = False

    # Delete from MongoDB (primary storage)
    articles_col = get_articles_collection()
    if articles_col is not None:
        try:
            # Try by slug first
            result = articles_col.delete_one({'slug': slug})
            if result.deleted_count > 0:
                deleted = True
            else:
                # Try by _id if slug didn't match
                try:
                    result = articles_col.delete_one({'_id': ObjectId(slug)})
                    if result.deleted_count > 0:
                        deleted = True
                except:
                    pass
        except Exception as e:
            print(f"MongoDB delete error: {e}")

    # Also try to remove from local file if it exists
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
            original_count = len(results)
            # Try by slug or _id
            results = [a for a in results if a.get('slug') != slug and str(a.get('_id', '')) != slug]
            if len(results) < original_count:
                with open(RESULTS_FILE, 'w') as f:
                    json.dump(results, f, indent=2)
                deleted = True
    except Exception as e:
        print(f"Local file delete error: {e}")

    # Clear cache to reflect changes immediately
    global _memory_cache
    with _cache_lock:
        _memory_cache['results'] = []
        _memory_cache['last_fetch'] = None

    if deleted:
        flash('Article deleted successfully!', 'success')
    else:
        flash('Article not found', 'error')

    return redirect(url_for('admin_articles'))


@app.route('/admin/articles/bulk-delete', methods=['POST'])
@admin_required
def admin_articles_bulk_delete():
    """Delete multiple articles at once"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'error': 'No articles selected'}), 400

        deleted_count = 0
        articles_col = get_articles_collection()

        for article_id in ids:
            deleted = False

            # Delete from MongoDB
            if articles_col is not None:
                try:
                    # Try by slug first
                    result = articles_col.delete_one({'slug': article_id})
                    if result.deleted_count > 0:
                        deleted = True
                    else:
                        # Try by _id if slug didn't match
                        try:
                            result = articles_col.delete_one({'_id': ObjectId(article_id)})
                            if result.deleted_count > 0:
                                deleted = True
                        except:
                            pass
                except Exception as e:
                    print(f"MongoDB delete error for {article_id}: {e}")

            # Also try to remove from local file
            try:
                if os.path.exists(RESULTS_FILE):
                    with open(RESULTS_FILE, 'r') as f:
                        results = json.load(f)
                    original_count = len(results)
                    results = [a for a in results if a.get('slug') != article_id and str(a.get('_id', '')) != article_id]
                    if len(results) < original_count:
                        with open(RESULTS_FILE, 'w') as f:
                            json.dump(results, f, indent=2)
                        deleted = True
            except Exception as e:
                print(f"Local file delete error for {article_id}: {e}")

            if deleted:
                deleted_count += 1

        # Clear cache
        global _memory_cache
        with _cache_lock:
            _memory_cache['results'] = []
            _memory_cache['last_fetch'] = None

        return jsonify({
            'success': True,
            'deleted': deleted_count,
            'message': f'Deleted {deleted_count} articles'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/articles/<slug>/preview')
@admin_required
def admin_article_preview(slug):
    """Preview article (same as public view but with admin bar)"""
    articles = load_articles()
    article = next((a for a in articles if a.get('slug') == slug), None)

    if not article:
        flash('Article not found', 'error')
        return redirect(url_for('admin_articles'))

    return render_template('admin/article_preview.html', article=article, is_preview=True)


@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def admin_upload_image():
    """Upload image for articles"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400

    # Generate unique filename
    import uuid
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)

    # Save file
    file.save(filepath)

    # Return URL
    image_url = f"/static/images/{filename}"

    return jsonify({'url': image_url, 'filename': filename})


# =============================================================================
# ADMIN - USERS MANAGEMENT
# =============================================================================

@app.route('/admin/users')
@admin_required
def admin_users():
    """List all registered users"""
    users_col = get_users_collection()
    users = []
    total_users = 0

    if users_col is not None:
        # Get pagination params
        page = request.args.get('page', 1, type=int)
        per_page = 20
        search = request.args.get('search', '').lower()

        # Build query
        query = {}
        if search:
            query = {'$or': [
                {'email': {'$regex': search, '$options': 'i'}},
                {'name': {'$regex': search, '$options': 'i'}}
            ]}

        total_users = users_col.count_documents(query)
        cursor = users_col.find(query).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page)

        for user in cursor:
            user['_id'] = str(user['_id'])
            users.append(user)

        pages = (total_users + per_page - 1) // per_page
    else:
        page = 1
        pages = 1
        search = ''

    return render_template('admin/users.html',
                          users=users,
                          total=total_users,
                          page=page,
                          pages=pages,
                          search=search)


@app.route('/admin/users/<user_id>')
@admin_required
def admin_user_detail(user_id):
    """View user details"""
    users_col = get_users_collection()
    if users_col is None:
        flash('Database not available', 'error')
        return redirect(url_for('admin_users'))

    try:
        user = users_col.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin_users'))

        user['_id'] = str(user['_id'])

        # Get user's CRS scores
        scores_col = get_user_scores_collection()
        scores = []
        if scores_col is not None:
            scores = list(scores_col.find({'user_id': user_id}).sort('created_at', -1).limit(10))

        # Get user's saved articles
        saved_col = get_saved_articles_collection()
        saved_articles = []
        if saved_col is not None:
            saved_articles = list(saved_col.find({'user_id': user_id}).sort('saved_at', -1).limit(20))

        return render_template('admin/user_detail.html',
                              user=user,
                              scores=scores,
                              saved_articles=saved_articles)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('admin_users'))


@app.route('/admin/users/<user_id>/toggle-status', methods=['POST'])
@admin_required
def admin_user_toggle_status(user_id):
    """Enable/disable user account"""
    users_col = get_users_collection()
    if users_col is None:
        flash('Database not available', 'error')
        return redirect(url_for('admin_users'))

    try:
        user = users_col.find_one({'_id': ObjectId(user_id)})
        if user:
            new_status = not user.get('is_active', True)
            users_col.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_active': new_status}}
            )
            flash(f"User {'enabled' if new_status else 'disabled'} successfully", 'success')
        else:
            flash('User not found', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect(url_for('admin_user_detail', user_id=user_id))


# =============================================================================
# ADMIN - EXPRESS ENTRY DRAWS
# =============================================================================

@app.route('/admin/draws')
@admin_required
def admin_draws():
    """Manage Express Entry draws data"""
    draws = []

    # Try MongoDB first
    try:
        db = get_database()
        if db is not None:
            draws_col = db.draws
            draws = list(draws_col.find().sort('draw_date', -1).limit(50))
            for d in draws:
                d['_id'] = str(d['_id'])
    except Exception as e:
        print(f"Error loading draws from MongoDB: {e}")

    # Fallback to local file if MongoDB empty
    if not draws:
        try:
            draws_file = os.path.join(DATA_DIR, 'draws.json')
            if os.path.exists(draws_file):
                with open(draws_file, 'r') as f:
                    data = json.load(f)
                    raw_draws = data.get('draws', [])[:50]
                    # Normalize field names to match template expectations
                    for i, d in enumerate(raw_draws):
                        draws.append({
                            '_id': None,  # No MongoDB ID for file-based draws
                            'draw_number': f"#{i+1}",
                            'draw_date': d.get('date', d.get('draw_date', '')),
                            'draw_type': d.get('type', d.get('draw_type', '')),
                            'crs_score': d.get('score', d.get('crs_score', 0)),
                            'itas_issued': d.get('itas', d.get('itas_issued', 0))
                        })
        except Exception as e:
            print(f"Error loading draws from file: {e}")

    return render_template('admin/draws.html', draws=draws)


@app.route('/admin/draws/add', methods=['GET', 'POST'])
@admin_required
def admin_draw_add():
    """Add a new Express Entry draw"""
    if request.method == 'POST':
        draw_data = {
            'draw_number': request.form.get('draw_number', ''),
            'draw_date': request.form.get('draw_date', ''),
            'draw_type': request.form.get('draw_type', ''),
            'crs_score': int(request.form.get('crs_score', 0)),
            'itas_issued': int(request.form.get('itas_issued', 0)),
            'tie_breaking_rule': request.form.get('tie_breaking_rule', ''),
            'created_at': datetime.utcnow().isoformat()
        }

        try:
            db = get_database()
            if db is not None:
                db.draws.insert_one(draw_data)
                flash('Draw added successfully!', 'success')
            else:
                flash('Database not available', 'error')
        except Exception as e:
            flash(f'Error adding draw: {e}', 'error')

        return redirect(url_for('admin_draws'))

    return render_template('admin/draw_edit.html', draw=None)


@app.route('/admin/draws/<draw_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_draw_edit(draw_id):
    """Edit an Express Entry draw"""
    try:
        db = get_database()
        if db is None:
            flash('Database not available', 'error')
            return redirect(url_for('admin_draws'))

        draw = db.draws.find_one({'_id': ObjectId(draw_id)})
        if not draw:
            flash('Draw not found', 'error')
            return redirect(url_for('admin_draws'))

        if request.method == 'POST':
            update_data = {
                'draw_number': request.form.get('draw_number', ''),
                'draw_date': request.form.get('draw_date', ''),
                'draw_type': request.form.get('draw_type', ''),
                'crs_score': int(request.form.get('crs_score', 0)),
                'itas_issued': int(request.form.get('itas_issued', 0)),
                'tie_breaking_rule': request.form.get('tie_breaking_rule', ''),
                'updated_at': datetime.utcnow().isoformat()
            }

            db.draws.update_one({'_id': ObjectId(draw_id)}, {'$set': update_data})
            flash('Draw updated successfully!', 'success')
            return redirect(url_for('admin_draws'))

        draw['_id'] = str(draw['_id'])
        return render_template('admin/draw_edit.html', draw=draw)

    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('admin_draws'))


@app.route('/admin/draws/<draw_id>/delete', methods=['POST'])
@admin_required
def admin_draw_delete(draw_id):
    """Delete an Express Entry draw"""
    try:
        db = get_database()
        if db is not None:
            result = db.draws.delete_one({'_id': ObjectId(draw_id)})
            if result.deleted_count > 0:
                flash('Draw deleted successfully!', 'success')
            else:
                flash('Draw not found', 'error')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect(url_for('admin_draws'))


# =============================================================================
# ADMIN - MEDIA LIBRARY
# =============================================================================

@app.route('/admin/media')
@admin_required
def admin_media():
    """Media library - view all uploaded images"""
    images = []
    if os.path.exists(IMAGES_DIR):
        for filename in os.listdir(IMAGES_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                filepath = os.path.join(IMAGES_DIR, filename)
                stat = os.stat(filepath)
                images.append({
                    'filename': filename,
                    'url': f'/static/images/{filename}',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

    # Sort by modified date (newest first)
    images.sort(key=lambda x: x['modified'], reverse=True)

    return render_template('admin/media.html', images=images)


@app.route('/admin/media/upload', methods=['POST'])
@admin_required
def admin_media_upload():
    """Upload new image to media library"""
    if 'image' not in request.files:
        flash('No image provided', 'error')
        return redirect(url_for('admin_media'))

    file = request.files['image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin_media'))

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        flash(f'Invalid file type. Allowed: {", ".join(allowed_extensions)}', 'error')
        return redirect(url_for('admin_media'))

    # Generate unique filename or use original
    import uuid
    use_original = request.form.get('use_original_name') == 'on'
    if use_original:
        filename = file.filename.replace(' ', '_')
    else:
        filename = f"{uuid.uuid4().hex}.{ext}"

    filepath = os.path.join(IMAGES_DIR, filename)
    file.save(filepath)

    flash(f'Image uploaded: {filename}', 'success')
    return redirect(url_for('admin_media'))


@app.route('/admin/media/<filename>/delete', methods=['POST'])
@admin_required
def admin_media_delete(filename):
    """Delete an image from media library"""
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Image deleted successfully', 'success')
    else:
        flash('Image not found', 'error')

    return redirect(url_for('admin_media'))


# =============================================================================
# ADMIN - ANALYTICS
# =============================================================================

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Analytics dashboard"""
    # Get article stats
    articles = load_articles()
    total_articles = len(articles)

    # Category breakdown
    categories = {}
    for article in articles:
        cat = article.get('category', 'uncategorized')
        categories[cat] = categories.get(cat, 0) + 1

    # Articles by month
    articles_by_month = {}
    for article in articles:
        created = article.get('created_at', '')[:7]  # YYYY-MM
        if created:
            articles_by_month[created] = articles_by_month.get(created, 0) + 1

    # User stats
    users_col = get_users_collection()
    total_users = 0
    users_by_month = {}
    if users_col is not None:
        total_users = users_col.count_documents({})
        # Users by month
        pipeline = [
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m', 'date': '$created_at'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': -1}},
            {'$limit': 12}
        ]
        try:
            for doc in users_col.aggregate(pipeline):
                if doc['_id']:
                    users_by_month[doc['_id']] = doc['count']
        except:
            pass

    # CRS scores submitted
    scores_col = get_user_scores_collection()
    total_scores = 0
    if scores_col is not None:
        total_scores = scores_col.count_documents({})

    return render_template('admin/analytics.html',
                          total_articles=total_articles,
                          total_users=total_users,
                          total_scores=total_scores,
                          categories=categories,
                          articles_by_month=dict(sorted(articles_by_month.items(), reverse=True)[:12]),
                          users_by_month=users_by_month)


# =============================================================================
# ADMIN - SETTINGS
# =============================================================================

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Site settings"""
    # Get admin users
    admins_col = AdminUser.get_admins_collection()
    admins = []
    if admins_col is not None:
        for admin in admins_col.find():
            admin['_id'] = str(admin['_id'])
            admins.append(admin)

    # Environment info
    env_info = {
        'MONGODB_URI': 'Connected' if get_database() else 'Not configured',
        'GEMINI_API_KEY': 'Set' if os.environ.get('GEMINI_API_KEY') else 'Not set',
        'POST_API_URL': os.environ.get('POST_API_URL', 'Not set'),
    }

    return render_template('admin/settings.html', admins=admins, env_info=env_info)


@app.route('/admin/settings/admin/add', methods=['POST'])
@admin_required
def admin_settings_add_admin():
    """Add new admin user"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'admin')

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('admin_settings'))

    admin, error = AdminUser.create(username, email, password, role)
    if admin:
        flash(f'Admin user "{username}" created successfully', 'success')
    else:
        flash(f'Error: {error}', 'error')

    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/admin/<admin_id>/delete', methods=['POST'])
@admin_required
def admin_settings_delete_admin(admin_id):
    """Delete admin user"""
    # Prevent deleting yourself
    if f"admin_{admin_id}" == current_user.get_id():
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_settings'))

    admins_col = AdminUser.get_admins_collection()
    if admins_col is not None:
        try:
            result = admins_col.delete_one({'_id': ObjectId(admin_id)})
            if result.deleted_count > 0:
                flash('Admin user deleted', 'success')
            else:
                flash('Admin not found', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')

    return redirect(url_for('admin_settings'))


# =============================================================================
# ADMIN - EMPLOYEES MANAGEMENT
# =============================================================================

@app.route('/admin/employees')
@admin_required
def admin_employees():
    """List all employees (admin users)"""
    admins_col = AdminUser.get_admins_collection()
    employees = []

    if admins_col is not None:
        for emp in admins_col.find().sort('created_at', -1):
            emp['_id'] = str(emp['_id'])
            employees.append(emp)

    return render_template('admin/employees.html', employees=employees)


@app.route('/admin/employees/add', methods=['GET', 'POST'])
@admin_required
def admin_employee_add():
    """Add new employee"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'editor')

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin/employee_edit.html', employee=None)

        # Create employee using AdminUser model
        admins_col = AdminUser.get_admins_collection()
        if admins_col is None:
            flash('Database not available', 'error')
            return redirect(url_for('admin_employees'))

        # Check if username exists
        if admins_col.find_one({'username': username.lower()}):
            flash('Username already exists', 'error')
            return render_template('admin/employee_edit.html', employee=None)

        # Hash password and create employee
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        employee_data = {
            'username': username.lower(),
            'name': name,
            'email': email.lower() if email else '',
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }

        admins_col.insert_one(employee_data)
        flash(f'Employee "{name or username}" added successfully', 'success')
        return redirect(url_for('admin_employees'))

    return render_template('admin/employee_edit.html', employee=None)


@app.route('/admin/employees/<employee_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_employee_edit(employee_id):
    """Edit employee"""
    admins_col = AdminUser.get_admins_collection()
    if admins_col is None:
        flash('Database not available', 'error')
        return redirect(url_for('admin_employees'))

    try:
        employee = admins_col.find_one({'_id': ObjectId(employee_id)})
        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('admin_employees'))

        if request.method == 'POST':
            update_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip().lower(),
                'role': request.form.get('role', 'editor'),
                'updated_at': datetime.utcnow()
            }

            # Update password if provided
            new_password = request.form.get('password', '').strip()
            if new_password:
                import bcrypt
                update_data['password_hash'] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            admins_col.update_one({'_id': ObjectId(employee_id)}, {'$set': update_data})
            flash('Employee updated successfully', 'success')
            return redirect(url_for('admin_employees'))

        employee['_id'] = str(employee['_id'])
        return render_template('admin/employee_edit.html', employee=employee)

    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('admin_employees'))


@app.route('/admin/employees/<employee_id>/delete', methods=['POST'])
@admin_required
def admin_employee_delete(employee_id):
    """Delete employee"""
    # Prevent deleting yourself
    if f"admin_{employee_id}" == current_user.get_id():
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_employees'))

    admins_col = AdminUser.get_admins_collection()
    if admins_col is not None:
        try:
            result = admins_col.delete_one({'_id': ObjectId(employee_id)})
            if result.deleted_count > 0:
                flash('Employee deleted successfully', 'success')
            else:
                flash('Employee not found', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')

    return redirect(url_for('admin_employees'))


@app.route('/admin/employees/<employee_id>/toggle-status', methods=['POST'])
@admin_required
def admin_employee_toggle_status(employee_id):
    """Enable/disable employee account"""
    # Prevent disabling yourself
    if f"admin_{employee_id}" == current_user.get_id():
        flash('Cannot disable your own account', 'error')
        return redirect(url_for('admin_employees'))

    admins_col = AdminUser.get_admins_collection()
    if admins_col is not None:
        try:
            employee = admins_col.find_one({'_id': ObjectId(employee_id)})
            if employee:
                new_status = not employee.get('is_active', True)
                admins_col.update_one(
                    {'_id': ObjectId(employee_id)},
                    {'$set': {'is_active': new_status}}
                )
                flash(f"Employee {'enabled' if new_status else 'disabled'} successfully", 'success')
            else:
                flash('Employee not found', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')

    return redirect(url_for('admin_employees'))


# =============================================================================
# ADMIN: GUIDES MANAGEMENT
# =============================================================================

def save_guides(data):
    """Save guides data to file"""
    try:
        with open(GUIDES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving guides: {e}")
        return False


@app.route('/admin/guides')
@admin_required
def admin_guides():
    """List all guide categories"""
    guides_data = load_guides()
    categories = guides_data.get('categories', {})
    return render_template('admin/guides.html', categories=categories)


@app.route('/admin/guides/<category_id>')
@admin_required
def admin_guides_category(category_id):
    """View guides in a category"""
    guides_data = load_guides()
    category = guides_data.get('categories', {}).get(category_id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin_guides'))
    return render_template('admin/guides_category.html', category=category, category_id=category_id)


@app.route('/admin/guides/<category_id>/add', methods=['GET', 'POST'])
@admin_required
def admin_guide_add(category_id):
    """Add a new guide to a category"""
    guides_data = load_guides()
    category = guides_data.get('categories', {}).get(category_id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin_guides'))

    if request.method == 'POST':
        guide_id = request.form.get('id', '').strip().lower().replace(' ', '-')
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        icon = request.form.get('icon', '📖').strip()
        difficulty = request.form.get('difficulty', 'Beginner')
        reading_time = request.form.get('reading_time', '10 min read').strip()
        overview = request.form.get('overview', '').strip()

        if not guide_id or not title:
            flash('Guide ID and title are required', 'error')
            return render_template('admin/guide_edit.html', category=category, category_id=category_id, guide=None)

        # Create new guide
        new_guide = {
            'id': guide_id,
            'title': title,
            'subtitle': subtitle,
            'icon': icon,
            'difficulty': difficulty,
            'reading_time': reading_time,
            'overview': overview,
            'sections': []
        }

        # Add to category
        if 'guides' not in category:
            category['guides'] = []
        category['guides'].append(new_guide)

        if save_guides(guides_data):
            flash(f'Guide "{title}" added successfully', 'success')
            return redirect(url_for('admin_guides_category', category_id=category_id))
        else:
            flash('Error saving guide', 'error')

    return render_template('admin/guide_edit.html', category=category, category_id=category_id, guide=None)


@app.route('/admin/guides/<category_id>/<guide_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_guide_edit(category_id, guide_id):
    """Edit an existing guide"""
    guides_data = load_guides()
    category = guides_data.get('categories', {}).get(category_id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin_guides'))

    # Find the guide
    guide = None
    guide_index = -1
    guides_list = category.get('guides', [])
    for i, g in enumerate(guides_list):
        if g.get('id') == guide_id:
            guide = g
            guide_index = i
            break

    if not guide:
        flash('Guide not found', 'error')
        return redirect(url_for('admin_guides_category', category_id=category_id))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        icon = request.form.get('icon', '📖').strip()
        difficulty = request.form.get('difficulty', 'Beginner')
        reading_time = request.form.get('reading_time', '10 min read').strip()
        overview = request.form.get('overview', '').strip()

        # Update guide
        guide['title'] = title
        guide['subtitle'] = subtitle
        guide['icon'] = icon
        guide['difficulty'] = difficulty
        guide['reading_time'] = reading_time
        guide['overview'] = overview

        # Handle sections
        section_titles = request.form.getlist('section_title[]')
        section_contents = request.form.getlist('section_content[]')
        new_sections = []
        for st, sc in zip(section_titles, section_contents):
            if st.strip():
                new_sections.append({'title': st.strip(), 'content': sc.strip()})
        guide['sections'] = new_sections

        if save_guides(guides_data):
            flash(f'Guide "{title}" updated successfully', 'success')
            return redirect(url_for('admin_guides_category', category_id=category_id))
        else:
            flash('Error saving guide', 'error')

    return render_template('admin/guide_edit.html', category=category, category_id=category_id, guide=guide)


@app.route('/admin/guides/<category_id>/<guide_id>/delete', methods=['POST'])
@admin_required
def admin_guide_delete(category_id, guide_id):
    """Delete a guide"""
    guides_data = load_guides()
    category = guides_data.get('categories', {}).get(category_id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin_guides'))

    # Remove the guide
    guides_list = category.get('guides', [])
    original_len = len(guides_list)
    category['guides'] = [g for g in guides_list if g.get('id') != guide_id]

    if len(category['guides']) < original_len:
        if save_guides(guides_data):
            flash('Guide deleted successfully', 'success')
        else:
            flash('Error deleting guide', 'error')
    else:
        flash('Guide not found', 'error')

    return redirect(url_for('admin_guides_category', category_id=category_id))


@app.route('/admin/learning-hub')
@admin_required
def admin_learning_hub():
    """Learning Hub admin overview"""
    guides_data = load_guides()
    categories = guides_data.get('categories', {})
    # Count total guides
    total_guides = sum(len(cat.get('guides', [])) for cat in categories.values())
    total_provinces = 0
    for cat in categories.values():
        if 'provinces' in cat:
            total_provinces += len(cat.get('provinces', []))
    return render_template('admin/learning_hub.html',
                          categories=categories,
                          total_guides=total_guides,
                          total_provinces=total_provinces)


# =============================================================================
# RUN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
