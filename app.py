"""
Philata.ca - Canadian Immigration Content Hub
Dashboard for viewing and approving generated content
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Data storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
APPROVED_FILE = os.path.join(DATA_DIR, 'approved.json')


def load_results():
    """Load all results"""
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


@app.route('/dashboard')
def dashboard():
    """Content dashboard"""
    results = load_results()
    return render_template('dashboard.html', results=results)


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
            "image_url": data.get('image_url', ''),
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
