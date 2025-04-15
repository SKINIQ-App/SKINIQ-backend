
from dotenv import load_dotenv
load_dotenv()

import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image_to_cloudinary(file_data, filename=None):
    result = cloudinary.uploader.upload(file_data, public_id=filename or None)
    return result["secure_url"]
