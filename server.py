from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Suppress favicon request errors
@app.get("/favicon.ico")
async def get_favicon():
    # Return 204 No Content to avoid 404 errors in logs
    return Response(status_code=status.HTTP_204_NO_CONTENT)

try:
    from auth import auth_router
    app.include_router(auth_router)
    logger.info("Successfully included auth_router")
except ImportError as e:
    logger.error(f"Failed to import auth_router: {e}")
except Exception as e:
    logger.error(f"Error including auth_router: {e}")

try:
    from skin_analysis import skin_router
    app.include_router(skin_router)
    logger.info("Successfully included skin_router")
except ImportError as e:
    logger.error(f"Failed to import skin_router: {e}")
except Exception as e:
    logger.error(f"Error including skin_router: {e}")

try:
    from diary import diary_router
    app.include_router(diary_router, prefix="/diary")
    logger.info("Successfully included diary_router")
except ImportError as e:
    logger.error(f"Failed to import diary_router: {e}")
except Exception as e:
    logger.error(f"Error including diary_router: {e}")

@app.get("/")
def read_root():
    return {"message": "Skincare API is running"}

@app.get("/profile/")
def get_all_profiles():
    logger.info("Fetching all profiles")
    try:
        from mongo_utils import get_user_by_username
        return {"message": "Profile endpoint is working"}
    except Exception as e:
        logger.error(f"Error fetching profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching profiles: {str(e)}")

@app.get("/static/privacy_policy.html", response_class=HTMLResponse)
async def serve_privacy_policy_page():
    logger.info("Serving privacy policy page")
    try:
        with open("static/privacy_policy.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Privacy policy page not found")
        raise HTTPException(status_code=404, detail="Privacy policy page not found")
    except Exception as e:
        logger.error(f"Error serving privacy policy page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving privacy policy page: {str(e)}")