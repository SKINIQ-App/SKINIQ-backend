from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import auth_router
from skin_analysis import skin_router
from diary import diary_router  # Add this

app = FastAPI()

origins = ["*"]  # Replace with your frontend URL in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers here
app.include_router(auth_router)
app.include_router(skin_router)
app.include_router(diary_router)  # Add this too

@app.get("/")
def read_root():
    return {"message": "Skincare API is running"}
