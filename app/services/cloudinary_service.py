import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

)

def upload_image(file_path: str):
    try:
        response = cloudinary.uploader.upload(file_path)
        return response.get("secure_url")
    
    except Exception as e:
        print("cloudinary upload failed. Error:", e)
        return None
    