from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from jose import jwt
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from passlib.hash import bcrypt
from cloudinary_utils import upload_image_to_cloudinary
from mongo_utils import *
from models import predict_skin_type, predict_skin_issues
from models import generate_routine
import random
from your_email_module import send_verification_email, send_password_reset_email
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify JWT_SECRET_KEY
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.error("JWT_SECRET_KEY is not set")
    raise ValueError("JWT_SECRET_KEY is not set")

JWT_EXPIRY_MINUTES = 30  # Link expires in 30 mins

auth_router = APIRouter(prefix="/auth")
logger.info("Initializing auth_router with prefix=/auth")

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    terms_accepted: bool

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class UserProfileUpdate(BaseModel):
    profile_image: Optional[str]

class SkinDetails(BaseModel):
    gender: str
    age: int
    skinType: str
    skinConcerns: List[str]
    skinConditionDiseases: List[str]
    skinBreakouts: str
    skinDescription: str

class EmailSchema(BaseModel):
    email: EmailStr

# --- Routes ---

@auth_router.post("/login")
def login(user: UserLogin):
    logger.info(f"Login attempt for {user.email}")
    try:
        existing = get_user_by_email(user.email)
        if not existing or not bcrypt.verify(user.password, existing["password"]):
            logger.warning(f"Invalid credentials for {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if "password" not in existing:
            logger.error(f"User data corrupted for {user.email}: password missing")
            raise HTTPException(status_code=500, detail="User data is corrupted. Password missing.")
        logger.info(f"Login successful for {user.email}")
        return {"username": existing["username"], "email": existing["email"]}
    except Exception as e:
        logger.error(f"Login failed for {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@auth_router.post("/forgot-password")
def forgot_password(data: EmailSchema):
    logger.info(f"Forgot password request for {data.email}")
    try:
        user = get_user_by_email(data.email)
        if not user:
            logger.warning(f"User not found: {data.email}")
            raise HTTPException(status_code=404, detail="User not found")

        # Create JWT reset token
        reset_token = jwt.encode(
            {
                "email": data.email,
                "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
            },
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        # Construct reset link
        reset_link = f"https://skiniq-backend.onrender.com/static/reset_password.html?token={reset_token}"

        # Send reset email
        send_password_reset_email(data.email, user["username"], reset_link)
        logger.info(f"Password reset email sent to {data.email}")
        return {"message": "Reset password link sent to your email"}
    except Exception as e:
        logger.error(f"Forgot password failed for {data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forgot password failed: {str(e)}")

@auth_router.get("/static/reset_password.html", response_class=HTMLResponse)
async def serve_reset_password_page():
    logger.info("Serving reset password page")
    try:
        with open("static/reset_password.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Reset password page not found")
        raise HTTPException(status_code=404, detail="Reset password page not found")
    except Exception as e:
        logger.error(f"Error serving reset password page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving reset password page: {str(e)}")

@auth_router.post("/reset-password")
def reset_password(data: ResetPassword):
    logger.info("Reset password request")
    try:
        payload = jwt.decode(data.token, JWT_SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            logger.warning("Invalid token: no email in payload")
            raise HTTPException(status_code=400, detail="Invalid token")
    except Exception:
        logger.warning("Invalid or expired token")
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    try:
        user = get_user_by_email(email)
        if not user:
            logger.warning(f"User not found for email: {email}")
            raise HTTPException(status_code=404, detail="User not found")

        hashed_pwd = bcrypt.hash(data.new_password)
        update_user_by_username(user["username"], {"password": hashed_pwd})
        logger.info(f"Password reset successful for {email}")
        return {"message": "Password reset successful"}
    except Exception as e:
        logger.error(f"Password reset failed for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@auth_router.post("/signup")
def signup(user: UserCreate):
    logger.info(f"Received signup request for email: {user.email}")
    try:
        if get_user_by_email(user.email):
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user_data = user.dict()
        user_data["password"] = bcrypt.hash(user.password)
        user_data["email_verified"] = False

        otp = random.randint(100000, 999999)
        user_data["otp"] = otp
        
        create_user(user_data)
        
        send_verification_email(user.email, otp, user.username)
        
        logger.info(f"Signup successful for {user.email}, OTP sent")
        return {"message": "Signup successful. OTP sent to email."}
    except Exception as e:
        logger.error(f"Signup failed for {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@auth_router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    logger.info(f"Verifying OTP for {data.email}")
    try:
        user = get_user_by_email(data.email)
        if not user:
            logger.warning(f"User not found: {data.email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if str(user.get("otp")) != data.otp:
            logger.warning(f"Invalid OTP for {data.email}: stored={user.get('otp')}, received={data.otp}")
            raise HTTPException(status_code=400, detail="Invalid OTP")

        update_user_by_email(data.email, {"email_verified": True})
        logger.info(f"Email verified for {data.email}")
        return {"message": "Email verified successfully"}
    except Exception as e:
        logger.error(f"OTP verification failed for {data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")

@auth_router.post("/send-otp")
async def send_otp(user: EmailSchema):
    logger.info(f"Send OTP request for {user.email}")
    try:
        otp = random.randint(100000, 999999)
        existing_user = get_user_by_email(user.email)

        if existing_user:
            update_user_by_email(user.email, {"otp": otp})
            send_verification_email(user.email, str(otp), existing_user["username"])
            logger.info(f"OTP {otp} sent to {user.email}")
        else:
            logger.warning(f"User not found: {user.email}")
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "OTP sent"}
    except Exception as e:
        logger.error(f"Send OTP failed for {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Send OTP failed: {str(e)}")

@auth_router.post("/upload-skin-photo/{username}")
def upload_skin_photo(username: str, file: UploadFile = File(...)):
    logger.info(f"Uploading skin photo for {username}")
    try:
        # Upload to Cloudinary
        image_url = upload_image_to_cloudinary(file.file)

        # Predict skin type
        file.file.seek(0)
        skin_type = predict_skin_type(file.file)

        # Save to DB
        update_user_by_username(username, {
            "profile_image": image_url,
            "predicted_skin_type": skin_type
        })

        logger.info(f"Skin photo uploaded for {username}, skin type: {skin_type}")
        return {
            "message": "Skin photo uploaded and skin type predicted",
            "image_url": image_url,
            "predicted_skin_type": skin_type
        }
    except Exception as e:
        logger.error(f"Skin photo upload failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/update-skin-details/{username}")
def update_skin_details(username: str, details: SkinDetails):
    logger.info(f"Updating skin details for {username}")
    try:
        # Predict skin issues
        predicted_issues = predict_skin_issues(details.skinDescription)

        # Save to DB
        update_user_by_username(username, {
            "skin_details": details.dict(),
            "predicted_skin_issues": predicted_issues
        })

        logger.info(f"Skin details updated for {username}")
        return {
            "message": "Skin details updated and issues predicted",
            "predicted_skin_issues": predicted_issues
        }
    except Exception as e:
        logger.error(f"Skin details update failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.get("/profile/{username}")
def get_profile(username: str):
    logger.info(f"Fetching profile for {username}")
    try:
        user = get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        predicted_skin_type = user.get("predicted_skin_type", "")
        predicted_issues = user.get("predicted_skin_issues", [])

        routine = generate_routine(predicted_skin_type, predicted_issues)

        logger.info(f"Profile fetched for {username}")
        return {
            "username": user["username"],
            "email": user["email"],
            "profile_image": user.get("profile_image"),
            "skin_details": user.get("skin_details", {}),
            "predicted_skin_type": predicted_skin_type,
            "predicted_skin_issues": predicted_issues,
            "recommended_routine": routine
        }
    except Exception as e:
        logger.error(f"Profile fetch failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Profile fetch failed: {str(e)}")

@auth_router.post("/update-profile-image/{username}")
def update_profile_image(username: str, file: UploadFile = File(...)):
    logger.info(f"Updating profile image for {username}")
    try:
        image_url = upload_image_to_cloudinary(file.file)
        update_user_by_username(username, {"profile_image": image_url})
        logger.info(f"Profile image updated for {username}")
        return {"message": "Profile image updated", "profile_image": image_url}
    except Exception as e:
        logger.error(f"Profile image update failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

logger.info("All routes in auth_router registered")