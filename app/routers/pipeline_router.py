from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
from typing import Optional
from app.services.ai_service import generate_poster

router = APIRouter()

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


@router.post("/generate-poster-complete")
async def generate_poster_complete(
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    brand_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    cta: str = Form(...),
    style: str = Form(...),
    poster_style: str = Form(...),
    design_style_prompt: str = Form(...),
    output_format: str = Form(...),
    variations: int = Form(3),
    image: Optional[UploadFile] = File(None)
):

    uploaded_image_path = None

    # STEP 1 — Upload Image
    if image:
        ext = image.filename.split(".")[-1]
        image_name = f"{uuid.uuid4()}.{ext}"
        uploaded_image_path = f"{UPLOAD_DIR}/{image_name}"

        with open(uploaded_image_path, "wb") as buffer:
            buffer.write(await image.read())

    # STEP 2 — Brand Context
    brand_context = f"""
    Brand Name: {brand_name}
    Primary Color: {primary_color}
    Secondary Color: {secondary_color}
    """

    # STEP 3 — AI Prompt
    base_prompt = f"""
    Create a professional marketing poster.

    Title: {title}
    Subtitle: {subtitle}
    Description: {description}

    Brand: {brand_name}

    Call To Action: {cta}

    Style: {style}

    Poster Style: {poster_style}

    Brand Colors:
    {primary_color} and {secondary_color}

    Design should look like a premium advertisement poster.
    """

    posters = []

    # STEP 4 — Generate Variations
    for i in range(variations):

        unique_prompt = base_prompt + f"\nCreative variation number {i+1}"

        poster_file = await generate_poster(unique_prompt)

        filename = os.path.basename(poster_file)

        posters.append({
            "poster_name": poster_file,
            "view_url": f"http://127.0.0.1:8000/generated/{poster_file}",
            "download_url": f"http://127.0.0.1:8000/download/{poster_file}"
        })

    # STEP 5 — Return Response
    return {
        "status": "success",
        "brand": brand_name,
        "uploaded_image": uploaded_image_path,
        "generated_posters": posters
    }