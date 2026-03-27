from fastapi import APIRouter, UploadFile, File
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"

    file_path = f"{UPLOAD_DIR}/{file_name}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "status": "success",
        "image_url": f"http://127.0.0.1:8000/uploads/{file_name}"
    }