from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from passlib.hash import bcrypt
from cloudinary_utils import upload_image_to_cloudinary
from mongo_utils import *
from models import predict_skin_type, predict_skin_issues
from models import generate_routine


auth_router = APIRouter()

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    terms_accepted: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr
    new_password: str

class UserProfileUpdate(BaseModel):
    profile_image: Optional[str]

class SkinDetails(BaseModel):
    gender: str
    age: int
    skinType: str
    skinConcerns: List[str]
    skinConditionDiseases: List[str]
    skinBreakouts:str
    skinDescription: str

# --- Routes ---

@auth_router.post("/login")
def login(user: UserLogin):
    existing = get_user_by_email(user.email)
    if not existing or not bcrypt.verify(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if "password" not in existing:
        raise HTTPException(status_code=500, detail="User data is corrupted. Password missing.")

    try:
        if not bcrypt.verify(user.password, existing["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    return {"username": existing["username"], "email": existing["email"]}

@auth_router.post("/forgot-password")
def forgot_password(data: ForgotPassword):
    user = get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_pwd = bcrypt.hash(data.new_password)
    update_user_by_username(user["username"], {"password": hashed_pwd})
    return {"message": "Password reset successful"}

@auth_router.post("/signup")
def signup(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    user_data = user.dict()
    user_data["password"] = bcrypt.hash(user.password)
    user_data["email_verified"] = False
    create_user(user_data)
    return {"message": "Signup successful"}

@auth_router.post("/upload-skin-photo/{username}")
def upload_skin_photo(username: str, file: UploadFile = File(...)):
    try:
        # Upload to Cloudinary
        image_url = upload_image_to_cloudinary(file.file)

        # Predict skin type
        file.file.seek(0)  # reset pointer for reuse
        skin_type = predict_skin_type(file.file)

        # Save to DB
        update_user_by_username(username, {
            "profile_image": image_url,
            "predicted_skin_type": skin_type
        })

        return {
            "message": "Skin photo uploaded and skin type predicted",
            "image_url": image_url,
            "predicted_skin_type": skin_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/update-skin-details/{username}")
def update_skin_details(username: str, details: SkinDetails):
    try:
        # Predict skin issues
        predicted_issues = predict_skin_issues(details.skinDescription)

        # Save to DB
        update_user_by_username(username, {
            "skin_details": details.dict(),
            "predicted_skin_issues": predicted_issues
        })

        return {
            "message": "Skin details updated and issues predicted",
            "predicted_skin_issues": predicted_issues
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/profile/{username}")
def get_profile(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    predicted_skin_type = user.get("predicted_skin_type", "")
    predicted_issues = user.get("predicted_skin_issues", [])

    routine = generate_routine(predicted_skin_type, predicted_issues)

    return {
        "username": user["username"],
        "email": user["email"],
        "profile_image": user.get("profile_image"),
        "skin_details": user.get("skin_details", {}),
        "predicted_skin_type": predicted_skin_type,
        "predicted_skin_issues": predicted_issues,
        "recommended_routine": routine
    }


@auth_router.post("/update-profile-image/{username}")
def update_profile_image(username: str, file: UploadFile = File(...)):
    try:
        image_url = upload_image_to_cloudinary(file.file)
        update_user_by_username(username, {"profile_image": image_url})
        return {"message": "Profile image updated", "profile_image": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
