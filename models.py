"""
User Model and Authentication
Flask-Login integration with MongoDB
"""

from datetime import datetime
from flask_login import UserMixin
from bson import ObjectId
import bcrypt

from database import get_users_collection, get_user_scores_collection, get_user_checklists_collection, get_saved_articles_collection


class User(UserMixin):
    """User model for Flask-Login"""

    def __init__(self, user_data):
        self.id = str(user_data.get('_id', ''))
        self.email = user_data.get('email', '')
        self.name = user_data.get('name', '')
        self.password_hash = user_data.get('password_hash', '')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.last_login = user_data.get('last_login')
        self.is_verified = user_data.get('is_verified', False)

        # Profile data
        self.profile = user_data.get('profile', {})

    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return self.id

    @property
    def is_active(self):
        """User is active"""
        return True

    @property
    def is_authenticated(self):
        """User is authenticated"""
        return True

    @property
    def is_anonymous(self):
        """User is not anonymous"""
        return False

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile': self.profile
        }

    # =========================================================================
    # Static methods for user operations
    # =========================================================================

    @staticmethod
    def create(email, password, name=''):
        """Create a new user"""
        users = get_users_collection()
        if users is None:
            return None, "Database not available"

        # Check if email already exists
        if users.find_one({'email': email.lower()}):
            return None, "Email already registered"

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            'email': email.lower(),
            'name': name,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_verified': False,
            'profile': {
                'target_program': None,
                'target_province': None,
                'crs_score': None,
                'immigration_stage': 'researching'  # researching, preparing, applied, approved
            }
        }

        result = users.insert_one(user_data)
        user_data['_id'] = result.inserted_id

        return User(user_data), None

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        users = get_users_collection()
        if users is None:
            return None

        try:
            user_data = users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass

        return None

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        users = get_users_collection()
        if users is None:
            return None

        user_data = users.find_one({'email': email.lower()})
        if user_data:
            return User(user_data)

        return None

    @staticmethod
    def authenticate(email, password):
        """Authenticate user with email and password"""
        users = get_users_collection()
        if users is None:
            return None, "Database not available"

        user_data = users.find_one({'email': email.lower()})
        if not user_data:
            return None, "Invalid email or password"

        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            # Update last login
            users.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return User(user_data), None

        return None, "Invalid email or password"

    @staticmethod
    def update_profile(user_id, profile_data):
        """Update user profile"""
        users = get_users_collection()
        if users is None:
            return False

        try:
            result = users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'profile': profile_data}}
            )
            return result.modified_count > 0
        except:
            return False

    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        users = get_users_collection()
        if users is None:
            return False

        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            result = users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password_hash': password_hash}}
            )
            return result.modified_count > 0
        except:
            return False


# =============================================================================
# User CRS Score Functions
# =============================================================================

def save_user_score(user_id, score_data):
    """Save user's CRS score calculation"""
    scores = get_user_scores_collection()
    if scores is None:
        return None

    score_doc = {
        'user_id': user_id,
        'score': score_data.get('total', 0),
        'breakdown': score_data.get('breakdown', {}),
        'factors': score_data.get('factors', {}),
        'created_at': datetime.utcnow()
    }

    result = scores.insert_one(score_doc)
    return str(result.inserted_id)


def get_user_scores(user_id, limit=10):
    """Get user's CRS score history"""
    scores = get_user_scores_collection()
    if scores is None:
        return []

    cursor = scores.find(
        {'user_id': user_id}
    ).sort('created_at', -1).limit(limit)

    return list(cursor)


def get_latest_user_score(user_id):
    """Get user's most recent CRS score"""
    scores = get_user_scores_collection()
    if scores is None:
        return None

    return scores.find_one(
        {'user_id': user_id},
        sort=[('created_at', -1)]
    )


# =============================================================================
# User Checklist Functions
# =============================================================================

def save_user_checklist(user_id, program, checklist_data):
    """Save or update user's document checklist progress"""
    checklists = get_user_checklists_collection()
    if checklists is None:
        return False

    checklists.update_one(
        {'user_id': user_id, 'program': program},
        {
            '$set': {
                'items': checklist_data.get('items', []),
                'updated_at': datetime.utcnow()
            },
            '$setOnInsert': {
                'created_at': datetime.utcnow()
            }
        },
        upsert=True
    )
    return True


def get_user_checklist(user_id, program):
    """Get user's checklist for a program"""
    checklists = get_user_checklists_collection()
    if checklists is None:
        return None

    return checklists.find_one({'user_id': user_id, 'program': program})


def get_all_user_checklists(user_id):
    """Get all user's checklists"""
    checklists = get_user_checklists_collection()
    if checklists is None:
        return []

    return list(checklists.find({'user_id': user_id}))


# =============================================================================
# Saved Articles Functions
# =============================================================================

def save_article(user_id, article_id, article_data=None):
    """Save an article for a user"""
    saved = get_saved_articles_collection()
    if saved is None:
        return False

    try:
        saved.update_one(
            {'user_id': user_id, 'article_id': article_id},
            {
                '$set': {
                    'article_title': article_data.get('title', '') if article_data else '',
                    'article_category': article_data.get('category', '') if article_data else '',
                    'saved_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        return True
    except:
        return False


def unsave_article(user_id, article_id):
    """Remove a saved article"""
    saved = get_saved_articles_collection()
    if saved is None:
        return False

    result = saved.delete_one({'user_id': user_id, 'article_id': article_id})
    return result.deleted_count > 0


def get_saved_articles(user_id):
    """Get user's saved articles"""
    saved = get_saved_articles_collection()
    if saved is None:
        return []

    return list(saved.find({'user_id': user_id}).sort('saved_at', -1))


def is_article_saved(user_id, article_id):
    """Check if article is saved by user"""
    saved = get_saved_articles_collection()
    if saved is None:
        return False

    return saved.find_one({'user_id': user_id, 'article_id': article_id}) is not None
