from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from mongo_utils import update_user_by_username, get_user_by_username

skin_router = APIRouter()

class SkinDetails(BaseModel):
    username: str
    skin_type: str = None
    skin_concerns: list[str] = []
    breakouts: str = []
    diseases: list[str] = []
    description: str = ""
    profile_image: str = None

@skin_router.post("/update-skin-details")
def update_skin_details(details: SkinDetails):
    user = get_user_by_username(details.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skin_info = {
        "skin_type": details.skin_type,
        "concerns": details.skin_concerns,
        "breakouts": details.breakouts,
        "diseases": details.diseases,
        "description": details.description
    }

    update_data = {"skin_info": skin_info}
    if details.profile_image:
        update_data["profile_image"] = details.profile_image

    update_user_by_username(details.username, update_data)
    return {"message": "Skin details updated successfully"}
