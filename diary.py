from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from mongo_utils import save_diary_entry, get_user_diary_entries
from cloudinary_utils import upload_image_to_cloudinary
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

diary_router = APIRouter()

@diary_router.post("/diary_entry")  # Changed from /diary/upload to /diary_entry to match frontend
async def upload_diary(username: str = Form(...), description: str = Form(None), file: UploadFile = File(None)):
    try:
        image_url = upload_image_to_cloudinary(file.file) if file else None
        entry = {
            "username": username,
            "description": description,
            "image_url": image_url,
            "date": datetime.now().isoformat()
        }
        save_diary_entry(entry)
        logger.info(f"Diary entry uploaded for {username}")
        return {"message": "Diary entry uploaded"}
    except Exception as e:
        logger.error(f"Diary entry upload failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diary entry upload failed: {str(e)}")

@diary_router.get("/diary/{username}")
def get_diary_entries(username: str):
    try:
        entries = get_user_diary_entries(username)
        logger.info(f"Fetched diary entries for {username}")
        return {"entries": entries}
    except Exception as e:
        logger.error(f"Failed to fetch diary entries for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch diary entries: {str(e)}")