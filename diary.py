from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List
import logging
from datetime import datetime
from cloudinary_utils import upload_image_to_cloudinary
from mongo_utils import get_user_by_username, update_user_by_username

diary_router = APIRouter()
logger = logging.getLogger(__name__)

@diary_router.post("/diary_entry")
async def create_diary_entry(
    username: str = Form(...),
    date: str = Form(...),
    text: str = Form(...),
    file: List[UploadFile] = File(...),
):
    try:
        user = get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        photo_urls = []
        for photo in file:
            photo_url = upload_image_to_cloudinary(photo.file, filename=photo.filename)
            photo_urls.append(photo_url)

        diary_entry = {
            "date": date,
            "text": text,
            "photos": photo_urls,
            "created_at": datetime.utcnow().isoformat(),
        }

        if "diary_entries" not in user:
            user["diary_entries"] = []
        user["diary_entries"].append(diary_entry)

        update_user_by_username(username, {"diary_entries": user["diary_entries"]})
        logger.info(f"Diary entry created for {username} on {date}")
        return {"message": "Diary entry created successfully"}
    except Exception as e:
        logger.error(f"Failed to create diary entry for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create diary entry: {str(e)}")

@diary_router.get("/diary/entries/{username}")
async def get_diary_entries(username: str):
    try:
        user = get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        diary_entries = user.get("diary_entries", [])
        logger.info(f"Fetched diary entries for {username}")
        return {"diary_entries": diary_entries}
    except Exception as e:
        logger.error(f"Failed to fetch diary entries for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch diary entries: {str(e)}")