from fastapi import APIRouter, UploadFile, File, Form
from mongo_utils import save_diary_entry, get_user_diary_entries
from cloudinary_utils import upload_image_to_cloudinary
from datetime import datetime

diary_router = APIRouter()

@diary_router.post("/diary/upload")
async def upload_diary(username: str = Form(...), description: str = Form(None), file: UploadFile = File(None)):
    image_url = upload_image_to_cloudinary(file.file) if file else None
    entry = {
        "username": username,
        "description": description,
        "image_url": image_url,
        "date": datetime.now().isoformat()
    }
    save_diary_entry(entry)
    return {"message": "Diary entry uploaded"}

@diary_router.get("/diary/{username}")
def get_diary_entries(username: str):
    entries = get_user_diary_entries(username)
    return {"entries": entries}
