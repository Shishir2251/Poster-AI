from fastapi import APIRouter, UploadFile, File, Request
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-image")
async def upload_image(request: Request, file: UploadFile = File(...)):  # fix 1, import Request and add it as a parameter

    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"

    file_path = f"{UPLOAD_DIR}/{file_name}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # fix 2, dynamically get the base URL instead of hardcoding it
    base_url = str(request.base_url).rstrip("/")

    return {
        "status": "success",
        "image_url": f"{base_url}/uploads/{file_name}"
    }