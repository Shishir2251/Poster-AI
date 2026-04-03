from fastapi import APIRouter, UploadFile, File, Form, Request
import uuid
import os
from typing import Optional
from app.services.ai_service import generate_poster
from app.schemas import get_language_rules
router = APIRouter()

from app.worker.tasks import generate_poster_task, generate_poster_fields_task

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


@router.post("/generate-poster-complete")
async def generate_poster_complete(
    request: Request,  # fix 1, importing the request
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    brand_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    cta: str = Form(...),
    design_style_prompt: str = Form(...),
    style_preset: str = Form(...),
    output_format: str = Form(...),
    language: str = Form("English"), # poster lanugae, default to english but can be set to other languages
    variations: int = Form(1),
    image: Optional[UploadFile] = File(None)
):
    language_rules = get_language_rules(language)
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

    {language_rules}

    IMPORTANT:
    Use the provided image as the MAIN SUBJECT.
    Do NOT modify the product or object inside the image.

    Only add:
    - typography
    - layout
    - branding elements
    - background styling

    Aspect Ratio: {output_format}

    IMPORTANT DESIGN RULES:
    - Keep all text inside safe margins
    - Leave padding around edges
    - Do not place text near borders
    - Ensure title, subtitle and CTA are fully visible

    Layout Guide:
    Top: Title
    Below title: Subtitle
    Center: Main visual or product
    Bottom: Call to action

    Title: {title}
    Subtitle: {subtitle}
    Description: {description}

    Brand: {brand_name}

    Call To Action: {cta}

    Design Style Prompt:
    {design_style_prompt}

    Brand Colors:
    Primary: {primary_color}
    Secondary: {secondary_color}

    Output Format:{output_format}

    Style Preset:{style_preset}

    The poster should look like a premium advertisement with modern layout,
    balanced typography, and strong visual hierarchy.
    """

    #  Dynamic base URL
    base_url = str(request.base_url).rstrip("/")

    tasks = []

    # STEP 4 — Generate Variations
    for i in range(variations):

        unique_prompt = base_prompt + f"\nCreative variation number {i+1}"

        task = generate_poster_task.delay(
            unique_prompt,
            output_format,
            uploaded_image_path
        )

        tasks.append(task.id)
    
    return{
        "status": "success",
        "message": f"Poster generation started with {variations} variations. You can check the status of your posters using the task IDs.",
        "task_ids": tasks
    }

    #     posters.append({
    #         "poster_name": filename,
    #         "view_url": f"{base_url}/generated/{filename}", # base url based on render server
    #         "download_url": f"{base_url}/download/{filename}"
    #     })

    # # STEP 5 — Return Response
    # return {
    #     "status": "success",
    #     "brand": brand_name,
    #     "uploaded_image": uploaded_image_path,
    #     "generated_posters": posters
    # }