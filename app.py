"""
Philata.ca - Canadian Immigration Content Hub
Dashboard for viewing and approving generated content
Comprehensive Immigration Guides
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
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


# Default images for article categories (Unsplash direct URLs - no API needed)
DEFAULT_ARTICLE_IMAGES = {
    'express_entry': {
        'url': 'https://images.unsplash.com/photo-1569974507005-6dc61f97fb5c?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1569974507005-6dc61f97fb5c?w=400&q=80',
        'credit': 'Ali Tawfiq',
        'credit_link': 'https://unsplash.com/@alitwfiq'
    },
    'pnp': {
        'url': 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=400&q=80',
        'credit': 'Scott Webb',
        'credit_link': 'https://unsplash.com/@scottwebb'
    },
    'policy': {
        'url': 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=400&q=80',
        'credit': 'Jason Hafso',
        'credit_link': 'https://unsplash.com/@jasonhafso'
    },
    'study_permit': {
        'url': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400&q=80',
        'credit': 'Vasily Koloda',
        'credit_link': 'https://unsplash.com/@napr0tiv'
    },
    'work_permit': {
        'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80',
        'credit': 'Alex Kotliarskyi',
        'credit_link': 'https://unsplash.com/@frantic'
    },
    'forms': {
        'url': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&q=80',
        'credit': 'Scott Graham',
        'credit_link': 'https://unsplash.com/@homajob'
    },
    'educational': {
        'url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&q=80',
        'credit': 'Green Chameleon',
        'credit_link': 'https://unsplash.com/@craftedbygc'
    },
    'default': {
        'url': 'https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=1200&q=80',
        'thumb': 'https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=400&q=80',
        'credit': 'John Lee',
        'credit_link': 'https://unsplash.com/@john_artifexfilms'
    }
}

def get_unsplash_image(category, title=''):
    """Get default Unsplash image based on category"""
    return DEFAULT_ARTICLE_IMAGES.get(category, DEFAULT_ARTICLE_IMAGES['default'])


def load_guides():
    """Load immigration guides data"""
    if os.path.exists(GUIDES_FILE):
        with open(GUIDES_FILE, 'r') as f:
            return json.load(f)
    return {"categories": {}}


def load_articles():
    """Load articles from Post API"""
    try:
        response = requests.get(f"{POST_API_URL}/results/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            raw_results = data if isinstance(data, list) else data.get('results', [])

            # Filter only items with full_article content
            articles = []
            for r in raw_results:
                if r.get('full_article') and len(r.get('full_article', '')) > 200:
                    # Get Unsplash image data if available from stored data
                    unsplash = r.get('unsplash_image', {}) or {}
                    category = r.get('category', '')

                    # If no Unsplash image stored, fetch one based on category
                    if not unsplash.get('url'):
                        unsplash = get_unsplash_image(category, r.get('title', '')) or {}

                    article = {
                        'id': r.get('id', ''),
                        'slug': create_slug(r.get('title', '')),
                        'title': r.get('title', ''),
                        'track': r.get('track', 'regular'),
                        'category': category,
                        'created_at': r.get('timestamp', r.get('date', '')),
                        'image_url': unsplash.get('url', ''),
                        'image_thumb': unsplash.get('thumb', ''),
                        'image_credit': unsplash.get('credit', ''),
                        'image_credit_link': unsplash.get('credit_link', ''),
                        'full_article': r.get('full_article', ''),
                        'source': r.get('source', ''),
                        'source_url': r.get('source_url', ''),
                        'reading_time': max(1, len(r.get('full_article', '').split()) // 200)
                    }
                    articles.append(article)

            articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
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
    """Load all results from Post API"""
    try:
        response = requests.get(f"{POST_API_URL}/results/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The API returns a list of results
            raw_results = data if isinstance(data, list) else data.get('results', [])

            # Transform to expected format
            results = []
            for r in raw_results:
                result = {
                    'id': r.get('id', ''),
                    'title': r.get('title', ''),
                    'track': r.get('track', 'regular'),
                    'category': r.get('category', ''),
                    'created_at': r.get('timestamp', r.get('date', '')),
                    'image_url': convert_image_url(r.get('image_url', '')),
                    'full_article': r.get('full_article', r.get('title', '')),
                    'source': r.get('source', ''),
                    'source_url': r.get('source_url', ''),
                    'captions': {
                        'instagram': r.get('caption_instagram', r.get('captions', {}).get('instagram', '')),
                        'facebook': r.get('caption_facebook', r.get('captions', {}).get('facebook', '')),
                        'linkedin': r.get('caption_linkedin', r.get('captions', {}).get('linkedin', '')),
                        'twitter': r.get('caption_twitter', r.get('captions', {}).get('twitter', ''))
                    }
                }
                results.append(result)

            # Sort by created_at (most recent first)
            results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return results
    except Exception as e:
        print(f"Error fetching from Post API: {e}")

    # Fallback to local file if API fails
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

@app.route('/articles')
def articles():
    """Articles listing page"""
    all_articles = load_articles()
    category = request.args.get('category')

    if category:
        all_articles = [a for a in all_articles if a.get('category') == category]

    return render_template('articles.html', articles=all_articles, category=category)


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
        "version": "1.0",
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


@app.route('/api/results', methods=['POST'])
def add_result():
    """Add a new result from n8n workflow"""
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
# RUN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
