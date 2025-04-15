from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URL"))
db = client["skincare"]

users_collection = db["users"]
diary_collection = db["diary_entries"]
skin_analysis_collection = db["skin_analysis"]

def create_user(user_data): return users_collection.insert_one(user_data)
def get_user_by_email(email): return users_collection.find_one({"email": email})
def get_user_by_username(username): return users_collection.find_one({"username": username})
def update_user_by_username(username, data): return users_collection.update_one({"username": username}, {"$set": data})
def save_diary_entry(entry): return diary_collection.insert_one(entry)
def get_user_diary_entries(username): return list(diary_collection.find({"username": username}))

def store_skin_analysis(username, skin_type, skin_info, image_url=None, description=None):
    doc = {
        "username": username,
        "skin_type": skin_type,
        "skin_info": skin_info,
        "image_url": image_url,
        "description": description
    }
    return skin_analysis_collection.insert_one(doc)

def update_user_by_email(email: str, update_data: dict):
    user = get_user_by_email(email)
    if user:
        db.users.update_one({"email": email}, {"$set": update_data})
        return True
    else:
        return False