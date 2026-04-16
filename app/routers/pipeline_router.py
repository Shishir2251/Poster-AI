from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
from typing import Optional
from app.schemas import get_language_rules
router = APIRouter()

from app.worker.tasks import generate_poster_task

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


@router.post("/generate-poster-complete")
async def generate_poster_complete(
    title: str = Form(...),
    title_font: str = Form("Times new roman bold"),
    subtitle: str = Form(...),
    subtitle_font: str = Form("monospace italic"),
    tagline: str = Form("Your Tagline Here"),
    brand_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    cta: str = Form("Call to action button text"),
    phone: str = Form(None),
    address: str = Form(None),
    website: str = Form(None),
    design_style_prompt: str = Form("Make this poster look modern and minimalistic with a touch of vintage"),
    style_preset: str = Form("Modern Minimal"),
    output_format: str = Form("1:1 square"),
    language: str = Form("hebrew"),
    variations: int = Form(1),
    image: Optional[UploadFile] = File(None)
):
    uploaded_image_path = None

    if image:
        ext = image.filename.split(".")[-1]
        image_name = f"{uuid.uuid4()}.{ext}"
        uploaded_image_path = f"{UPLOAD_DIR}/{image_name}"
        with open(uploaded_image_path, "wb") as buffer:
            buffer.write(await image.read())

    content = {
        "title": title,
        "subtitle": subtitle,
        "cta": cta,
        "brand_name": brand_name,
        "tagline": tagline,
        "phone": phone or "",
        "address": address or "",
        "website": website or ""
    }

    base_prompt = f"""
You are a senior professional graphic designer specializing
in high-impact marketing posters.

=====================
CRITICAL: THIS IS A POSTER BACKGROUND ONLY
=====================
You are generating ONLY the visual background layer of a poster.
A separate professional text rendering system will add ALL text afterward.

ABSOLUTE TEXT RULE — ZERO TOLERANCE:
- Do NOT render any text, letters, numbers, or characters anywhere
- Do NOT draw placeholder bars, boxes, lines, or wireframe shapes
- Do NOT add watermarks, decorative scripts, or any readable marks

=====================
POSTER CONTEXT (FOR VISUAL DIRECTION ONLY — DO NOT DRAW)
=====================
This poster is for: {brand_name}
The poster promotes: {title}
Additional context: {subtitle}

Use this information ONLY to decide:
- What kind of imagery, props, or environment fits the business
- What mood and atmosphere the poster should convey
- What decorative elements make sense (e.g. pizza ingredients, herbs,
  flour dust for a pizza brand — NOT the actual text)

DO NOT render any of these words as text in the image.

=====================
INPUT LANGUAGE
=====================
All input fields may be provided in Hebrew or English.
You must understand and interpret both languages correctly.
If input is in Hebrew, treat it as Hebrew context.
If input is in English, treat it as English context.
Do NOT translate — just use the meaning to guide your visual design decisions.

=====================
BRAND IDENTITY (STRICT)
=====================
Primary Color: {primary_color}
Secondary Color: {secondary_color}
Title Font Style: {title_font}
Subtitle Font Style: {subtitle_font}

- Use {primary_color} as the dominant background color
- Use {secondary_color} only as subtle accent color in the design
- Do NOT create any button, badge, or UI element

=====================
DESIGN DIRECTION (HIGH PRIORITY)
=====================
Style instruction: {design_style_prompt}
Preset: {style_preset}

This style instruction is a HIGH PRIORITY creative directive.
Every visual decision — color treatment, lighting, texture, composition,
decorative elements, mood, and atmosphere — must strongly reflect this style.
If the style says "luxury", the poster must feel expensive and premium.
If the style says "vintage", use warm tones, textures, and retro aesthetics.
If the style says "minimalist", keep backgrounds clean with minimal decoration.
The style instruction overrides generic design choices — treat it as law.

=====================
CANVAS LAYOUT ZONES (STRICT)
=====================

ZONE 1 — TOP TEXT AREA (0% to 28%):
- Completely EMPTY — flat {primary_color} background only
- No elements, no decorations, no shadows here
- Must have strong contrast to support text overlay

ZONE 2 — HERO VISUAL (28% to 75%):
- Place the main visual subject HERE ONLY
- Must NOT extend above 28% or below 75%
- Scale down if needed to fit strictly within this zone
- Add background, lighting, shadows, decorative elements here

ZONE 3 — LOWER AREA (75% to 100%):
- Completely EMPTY — flat {primary_color} background only
- No elements, no decorations whatsoever
- This area is reserved for text and CTA rendering later

=====================
IMAGE RULES
=====================
- If a product image is provided, use it as the MAIN SUBJECT in ZONE 2
- If no image is provided, generate a high quality, photorealistic
  visual that fits the brand context in ZONE 2
- Only add: background, lighting, shadows, decorative elements
- Do NOT alter or reimagine any provided product image

=====================
OUTPUT QUALITY
=====================
Aspect Ratio: {output_format}
- Premium, print-ready marketing poster
- Every element fully visible inside the canvas

Creative variation number: {{variation_number}}
"""

    tasks = []
    for i in range(variations):
        unique_prompt = base_prompt.replace("{variation_number}", str(i + 1))
        task = generate_poster_task.delay(
            unique_prompt,
            content,
            output_format,
            uploaded_image_path
        )
        tasks.append(task.id)

    return {
        "status": "success",
        "message": f"Poster generation started with {variations} variations.",
        "task_ids": tasks
    }