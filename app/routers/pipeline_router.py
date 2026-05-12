#--- new pipeline 

"""
pipeline_router.py  —  Background-only prompt for Nano Banana.
Text is handled entirely by Claude + Playwright downstream.
"""

from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
import random
from typing import Optional

router = APIRouter()
from app.worker.tasks import generate_poster_task


# ── Layout archetypes ──────────────────────────────────────────────────────────
def get_random_layout() -> dict:
    layouts = [
        {
            "name": "center",
            "description": (
                "Place the main subject dead center horizontally and vertically. "
                "Equal empty space on left and right. "
                "Top 22% and bottom 35% must be completely clear flat background."
            ),
        },
        {
            "name": "left",
            "description": (
                "Place the main subject on the LEFT side (left 55% of canvas). "
                "The right 40% must be a clean, empty, flat background area. "
                "Top 22% and bottom 35% must be completely clear."
            ),
        },
        {
            "name": "right",
            "description": (
                "Place the main subject on the RIGHT side (right 55% of canvas). "
                "The left 40% must be a clean, empty, flat background area. "
                "Top 22% and bottom 35% must be completely clear."
            ),
        },
        {
            "name": "bottom_center",
            "description": (
                "Place the main subject at the BOTTOM-CENTER, occupying 40%-65% of canvas height. "
                "The top 40% must be atmospheric but clean — no subject elements. "
                "Bottom 35% must be flat background."
            ),
        },
    ]
    chosen = random.choice(layouts)
    print(f"[Layout] Selected: {chosen['name']}")
    return chosen


UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


@router.post("/generate-poster-complete")
async def generate_poster_complete(
    title: str = Form(...),
    title_font: str = Form("Rubik-Bold.ttf"),
    subtitle: str = Form(...),
    subtitle_font: str = Form("Rubik-Regular.ttf"),
    tagline: str = Form(""),
    brand_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    cta: str = Form(""),
    phone: str = Form(None),
    address: str = Form(None),
    website: str = Form(None),
    additional_info: str = Form(None),
    design_style_prompt: str = Form("modern minimalist with a touch of luxury"),
    style_preset: str = Form("Modern Minimal"),
    output_format: str = Form("1:1"),
    language: str = Form("hebrew"),
    variations: int = Form(1),
    image: Optional[UploadFile] = File(None),
):
    uploaded_image_path = None
    if image:
        ext = image.filename.split(".")[-1]
        image_name = f"{uuid.uuid4()}.{ext}"
        uploaded_image_path = f"{UPLOAD_DIR}/{image_name}"
        with open(uploaded_image_path, "wb") as buffer:
            buffer.write(await image.read())

    # ── Layout selection ───────────────────────────────────────────────────────
    layout_instruction = get_random_layout()
    layout_name = layout_instruction["name"]
    layout_description = layout_instruction["description"]

    # ── Content dict (passed through to Claude designer) ──────────────────────
    content = {
        "title": title,
        "subtitle": subtitle,
        "cta": cta,
        "brand_name": brand_name,
        "tagline": tagline,
        "phone": phone or "",
        "address": address or "",
        "website": website or "",
        "additional_info": additional_info or "",
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "design_style_prompt": design_style_prompt,
    }

    background_prompt = f"""
Generate a photorealistic, cinematic marketing poster background — NO TEXT.

Brand: {brand_name}
Product: {title}
Style: {design_style_prompt}
Colors: {primary_color} dominant, {secondary_color} accent
Aspect ratio: {output_format}

- High-end editorial photography quality
- Professional studio lighting
- Premium, memorable — not generic stock photography
- Zero text, letters, symbols, UI elements
"""
    

    # ── Dispatch Celery tasks 
    tasks = []
    for i in range(variations):
        task = generate_poster_task.delay(
            background_prompt,
            content,
            output_format,
            uploaded_image_path,
        )
        tasks.append(task.id)

    return {
        "status": "success",
        "message": f"Poster generation started ({variations} variation(s)).",
        "task_ids": tasks,
    }
