import os
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings


# -----------------------------------
# Generate Unique File Name
# -----------------------------------

def generate_unique_filename(filename: str) -> str:

    extension = filename.split(".")[-1]

    unique_name = f"{uuid.uuid4()}.{extension}"

    return unique_name


# -----------------------------------
# Save Uploaded File
# -----------------------------------

async def save_upload_file(file: UploadFile) -> str:

    filename = generate_unique_filename(file.filename)

    file_path = settings.UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return str(file_path)


# -----------------------------------
# Validate Image Type
# -----------------------------------

def validate_image_type(content_type: str):

    if content_type not in [
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]:
        raise ValueError("Unsupported image format")


# -----------------------------------
# Validate Image Size
# -----------------------------------

async def validate_image_size(file: UploadFile):

    content = await file.read()

    size_mb = len(content) / (1024 * 1024)

    if size_mb > 10:
        raise ValueError("Image exceeds 10MB limit")

    file.file.seek(0)


# -----------------------------------
# Delete Temporary File
# -----------------------------------

def delete_file(path: str):

    if os.path.exists(path):
        os.remove(path)