"""
MongoDB Database Connection Module
Handles connection to MongoDB Atlas and provides database access
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# MongoDB connection string from environment variable
MONGODB_URI = os.environ.get('MONGODB_URI', '')

# Database name
DB_NAME = os.environ.get('MONGODB_DB_NAME', 'philata')

# Global database connection
_client = None
_db = None


def get_database():
    """Get MongoDB database instance with lazy connection"""
    global _client, _db

    if _db is not None:
        return _db

    if not MONGODB_URI:
        print("Warning: MONGODB_URI not set. Database features disabled.")
        return None

    try:
        # Create client with connection pooling
        _client = MongoClient(
            MONGODB_URI,
            maxPoolSize=50,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True
        )

        # Test connection
        _client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas!")

        _db = _client[DB_NAME]

        # Create indexes for better performance
        _create_indexes(_db)

        return _db

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None


def _create_indexes(db):
    """Create database indexes for better query performance"""
    try:
        # Users collection indexes
        db.users.create_index('email', unique=True)
        db.users.create_index('created_at')

        # User scores collection indexes
        db.user_scores.create_index('user_id')
        db.user_scores.create_index([('user_id', 1), ('created_at', -1)])

        # User checklists collection indexes
        db.user_checklists.create_index('user_id')

        # Saved articles collection indexes
        db.saved_articles.create_index([('user_id', 1), ('article_id', 1)], unique=True)

        # Articles collection indexes (for news/content)
        db.articles.create_index('slug', unique=True, sparse=True)
        db.articles.create_index('created_at')
        db.articles.create_index('category')

        print("Database indexes created successfully")

    except Exception as e:
        print(f"Error creating indexes: {e}")


def close_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


# Collection access helpers
def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db.users if db is not None else None


def get_user_scores_collection():
    """Get user CRS scores collection"""
    db = get_database()
    return db.user_scores if db is not None else None


def get_user_checklists_collection():
    """Get user checklists collection"""
    db = get_database()
    return db.user_checklists if db is not None else None


def get_saved_articles_collection():
    """Get saved articles collection"""
    db = get_database()
    return db.saved_articles if db is not None else None


def get_articles_collection():
    """Get articles/news collection"""
    db = get_database()
    return db.articles if db is not None else None


def is_connected():
    """Check if database is connected"""
    db = get_database()
    return db is not None
