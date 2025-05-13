from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
import certifi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

client = None
db = None
users_collection = None
diary_collection = None
skin_analysis_collection = None

def init_mongo():
    global client, db, users_collection, diary_collection, skin_analysis_collection
    if client is None:
        try:
            connection_string = os.getenv("MONGODB_URL")
            if not connection_string:
                raise Exception("MONGODB_URL not set in environment")
            client = MongoClient(
                connection_string,
                ssl=True,
                tlsCAFile=certifi.where(),
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                serverSelectionTimeoutMS=20000
            )
            db = client["skincare"]
            db.command("ping")
            users_collection = db["users"]
            diary_collection = db["diary_entries"]
            skin_analysis_collection = db["skin_analysis"]
            logger.info("Connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            client = None
            raise Exception("Failed to connect to MongoDB")
    return True

def create_user(user_data):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        result = users_collection.insert_one(user_data)
        logger.info(f"User created: {user_data.get('email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to create user {user_data.get('email')}: {e}")
        raise

def get_user_by_email(email):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        user = users_collection.find_one({"email": email})
        logger.info(f"User fetch attempted for: {email}")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user by email {email}: {e}")
        raise

def get_user_by_username(username):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        user = users_collection.find_one({"username": username})
        logger.info(f"User fetch attempted for: {username}")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user by username {username}: {e}")
        raise

def update_user_by_username(username, data):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        result = users_collection.update_one({"username": username}, {"$set": data})
        logger.info(f"User updated: {username}")
        return result
    except Exception as e:
        logger.error(f"Failed to update user {username}: {e}")
        raise

def save_diary_entry(entry):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        result = diary_collection.insert_one(entry)
        logger.info(f"Diary entry saved for {entry.get('username')}")
        return result
    except Exception as e:
        logger.error(f"Failed to save diary entry for {entry.get('username')}: {e}")
        raise

def get_user_diary_entries(username):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        entries = list(diary_collection.find({"username": username}))
        logger.info(f"Fetched {len(entries)} diary entries for {username}")
        return entries
    except Exception as e:
        logger.error(f"Failed to fetch diary entries for {username}: {e}")
        raise

def store_skin_analysis(username, skin_type, skin_info, image_url=None, description=None):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        doc = {
            "username": username,
            "skin_type": skin_type,
            "skin_info": skin_info,
            "image_url": image_url,
            "description": description
        }
        result = skin_analysis_collection.insert_one(doc)
        logger.info(f"Skin analysis stored for {username}")
        return result
    except Exception as e:
        logger.error(f"Failed to store skin analysis for {username}: {e}")
        raise

def update_user_by_email(email: str, update_data: dict):
    if not init_mongo():
        raise Exception("Failed to connect to MongoDB")
    try:
        user = get_user_by_email(email)
        if user:
            result = users_collection.update_one({"email": email}, {"$set": update_data})
            logger.info(f"User updated by email: {email}")
            return True
        logger.info(f"No user found to update for email: {email}")
        return False
    except Exception as e:
        logger.error(f"Failed to update user by email {email}: {e}")
        raise

logger.info("MongoDB utilities loaded")