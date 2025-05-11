from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
import certifi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Global variables for lazy initialization
client = None
db = None
users_collection = None
diary_collection = None
skin_analysis_collection = None

def init_mongo():
    global client, db, users_collection, diary_collection, skin_analysis_collection
    if client is None:
        try:
            client = MongoClient(
                os.getenv("MONGODB_URL"),
                ssl=True,
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=True,  # Temporary for testing
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=30000
            )
            db = client["skincare"]
            db.command("ping")
            users_collection = db["users"]
            diary_collection = db["diary_entries"]
            skin_analysis_collection = db["skin_analysis"]
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

def create_user(user_data):
    init_mongo()
    logger.info(f"Creating user: {user_data.get('email')}")
    try:
        result = users_collection.insert_one(user_data)
        logger.info(f"User created: {user_data.get('email')}, ID: {result.inserted_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create user {user_data.get('email')}: {e}")
        raise

def get_user_by_email(email):
    init_mongo()
    logger.info(f"Fetching user by email: {email}")
    try:
        user = users_collection.find_one({"email": email})
        if user:
            logger.info(f"User found: {email}")
        else:
            logger.info(f"No user found for email: {email}")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user by email {email}: {e}")
        raise

def get_user_by_username(username):
    init_mongo()
    logger.info(f"Fetching user by username: {username}")
    try:
        user = users_collection.find_one({"username": username})
        if user:
            logger.info(f"User found: {username}")
        else:
            logger.info(f"No user found for username: {username}")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user by username {username}: {e}")
        raise

def update_user_by_username(username, data):
    init_mongo()
    logger.info(f"Updating user: {username}")
    try:
        result = users_collection.update_one({"username": username}, {"$set": data})
        logger.info(f"User updated: {username}, matched: {result.matched_count}, modified: {result.modified_count}")
        return result
    except Exception as e:
        logger.error(f"Failed to update user {username}: {e}")
        raise

def save_diary_entry(entry):
    init_mongo()
    logger.info(f"Saving diary entry for {entry.get('username')}")
    try:
        result = diary_collection.insert_one(entry)
        logger.info(f"Diary entry saved for {entry.get('username')}, ID: {result.inserted_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to save diary entry for {entry.get('username')}: {e}")
        raise

def get_user_diary_entries(username):
    init_mongo()
    logger.info(f"Fetching diary entries for {username}")
    try:
        entries = list(diary_collection.find({"username": username}))
        logger.info(f"Found {len(entries)} diary entries for {username}")
        return entries
    except Exception as e:
        logger.error(f"Failed to fetch diary entries for {username}: {e}")
        raise

def store_skin_analysis(username, skin_type, skin_info, image_url=None, description=None):
    init_mongo()
    logger.info(f"Storing skin analysis for {username}")
    try:
        doc = {
            "username": username,
            "skin_type": skin_type,
            "skin_info": skin_info,
            "image_url": image_url,
            "description": description
        }
        result = skin_analysis_collection.insert_one(doc)
        logger.info(f"Skin analysis stored for {username}, ID: {result.inserted_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to store skin analysis for {username}: {e}")
        raise

def update_user_by_email(email: str, update_data: dict):
    init_mongo()
    logger.info(f"Updating user by email: {email}")
    try:
        user = get_user_by_email(email)
        if user:
            result = users_collection.update_one({"email": email}, {"$set": update_data})
            logger.info(f"User updated by email: {email}, matched: {result.matched_count}, modified: {result.modified_count}")
            return True
        else:
            logger.info(f"No user found to update for email: {email}")
            return False
    except Exception as e:
        logger.error(f"Failed to update user by email {email}: {e}")
        raise

logger.info("MongoDB utilities module loaded (lazy initialization)")