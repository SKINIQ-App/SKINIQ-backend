from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]  # Replace with your frontend URL in production

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers with error handling
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
    app.include_router(diary_router)
    logger.info("Successfully included diary_router")
except ImportError as e:
    logger.error(f"Failed to import diary_router: {e}")
except Exception as e:
    logger.error(f"Error including diary_router: {e}")

@app.get("/")
def read_root():
    return {"message": "Skincare API is running"}