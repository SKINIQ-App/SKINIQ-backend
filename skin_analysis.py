from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from mongo_utils import update_user_by_username, get_user_by_username, store_skin_analysis
from models import predict_skin_type, predict_skin_issues, generate_routine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

skin_router = APIRouter(prefix="/skin")

class SkinDetails(BaseModel):
    username: str
    gender: str
    age: int
    skinType: str
    skinConcerns: List[str]
    skinConditionDiseases: List[str]
    skinBreakouts: str
    skinDescription: str

class SkinAnalysisResponse(BaseModel):
    skin_type: str
    skin_issues: List[str]
    routine: List[str]

@skin_router.post("/analyze")
async def analyze_skin(username: str, file: UploadFile = File(...)):
    try:
        user = get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        # Predict skin type from image
        skin_type = predict_skin_type(file.file)
        
        # Fallback routine if prediction fails
        routine = ["Use gentle cleanser and moisturizer daily"]
        skin_issues = []

        # Update user data
        update_data = {"predicted_skin_type": skin_type}
        update_user_by_username(username, update_data)
        
        # Store analysis
        store_skin_analysis(username, skin_type, {"source": "image"})

        # Generate routine
        routine = generate_routine(skin_type, skin_issues)

        logger.info(f"Skin analysis completed for {username}: {skin_type}")
        return SkinAnalysisResponse(
            skin_type=skin_type,
            skin_issues=skin_issues,
            routine=routine
        )
    except Exception as e:
        logger.error(f"Skin analysis failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Skin analysis failed: {str(e)}")
@skin_router.post("/questionnaire")
async def process_questionnaire(details: SkinDetails):
    try:
        user = get_user_by_username(details.username)
        if not user:
            logger.warning(f"User not found: {details.username}")
            raise HTTPException(status_code=404, detail="User not found")

        # Predict skin issues from description
        skin_issues = predict_skin_issues(details.skinDescription)

        # Save skin details
        skin_info = {
            "gender": details.gender,
            "age": details.age,
            "skin_type": details.skinType,
            "concerns": details.skinConcerns,
            "diseases": details.skinConditionDiseases,
            "breakouts": details.skinBreakouts,
            "description": details.skinDescription
        }

        update_data = {
            "skin_details": skin_info,
            "predicted_skin_issues": skin_issues
        }
        update_user_by_username(details.username, update_data)

        # Store analysis
        store_skin_analysis(details.username, details.skinType, skin_info, description=details.skinDescription)

        # Generate routine
        routine = generate_routine(details.skinType, skin_issues)

        logger.info(f"Questionnaire processed for {details.username}")
        return SkinAnalysisResponse(
            skin_type=details.skinType,
            skin_issues=skin_issues,
            routine=routine
        )
    except Exception as e:
        logger.error(f"Questionnaire processing failed for {details.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Questionnaire processing failed: {str(e)}")