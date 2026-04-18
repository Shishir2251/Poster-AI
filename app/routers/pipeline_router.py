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
    title_font: str = Form("Rubik-Bold.ttf"),
    subtitle: str = Form(...),
    subtitle_font: str = Form("Rubik-Regular.ttf"),
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
- Think of this as a billboard background before the text is printed on it

=====================
DESIGN DIRECTION (HIGH PRIORITY)
=====================
Style instruction: {design_style_prompt}
Preset: {style_preset}

This is a HIGH PRIORITY creative directive — treat it as law.
Push the style to its fullest expression:
- If "modern minimalist" — use bold negative space, strong single focal point,
  sophisticated color palette, nothing unnecessary
- If "luxury" — dramatic lighting, rich textures, gold/dark accents, cinematic feel
- If "vintage" — warm grain, retro color grading, organic textures
- Do NOT default to safe or generic interpretations of the style
- The poster must look like it belongs in a high-end design portfolio

=====================
POSTER CONTEXT (FOR VISUAL DIRECTION ONLY — DO NOT DRAW)
=====================
This poster is for: {brand_name}
The poster promotes: {title}
Additional context: {subtitle}
Brand tagline: {tagline}

Use this information ONLY to inspire:
- A unique, creative visual concept that stands out
- Imagery, environment, and atmosphere that feels fresh and unexpected
- Avoid generic stock-photo compositions — think like an award-winning
  art director creating a campaign for a global brand
- The visual should feel surprising, premium, and memorable

DO NOT render any of these words as text in the image.

=====================
INPUT LANGUAGE
=====================
All input fields may be provided in Hebrew or English.
You must understand and interpret both languages correctly.
Do NOT translate — just use the meaning to guide your visual design decisions.

=====================
BRAND IDENTITY (STRICT)
=====================
Primary Color: {primary_color}
Secondary Color: {secondary_color}
Title Font Style: {title_font}
Subtitle Font Style: {subtitle_font}

- ALL design decisions must reflect this brand identity
- Colors must be consistent and intentional
- Use {primary_color} as the dominant background color
- Use {secondary_color} as accent color in decorative elements
- Do NOT create any button, badge, or UI element

=====================
CANVAS LAYOUT ZONES (STRICT)
=====================

ZONE 1 — TOP TEXT AREA (0% to 25%):
- Completely EMPTY — flat {primary_color} background only
- No elements, no decorations, no shadows bleeding into this zone
- Must have strong contrast to support dark or light text overlay
- This is where title and subtitle will be added in post-production

ZONE 2 — HERO VISUAL (25% to 62%):
- Place the main visual subject HERE ONLY
- Must NOT extend above 25% or below 62%
- The BOTTOM EDGE of the product must not cross 62% of canvas height
- Scale down if needed to fit strictly within this zone
- Center the product both horizontally and vertically within this zone

ZONE 3 — LOWER AREA (68% to 100%):
- Completely EMPTY — flat clean background only
- No elements, no decorations, no shadows from zone 2 bleeding in
- This area is reserved for text and CTA rendering in post-production
- Background color should match or complement {primary_color}

=====================
IMAGE RULES
=====================
- If a product image is provided, use it as the MAIN SUBJECT in ZONE 2
- If no image is provided, generate a high quality, photorealistic
  hero visual that perfectly fits the brand context in ZONE 2
- Only add: background, lighting, shadows, decorative elements
- Do NOT alter, distort, or reimagine any provided product image
- The product must look exactly as uploaded

=====================
OUTPUT QUALITY
=====================
Aspect Ratio: {output_format}
- Premium, print-ready marketing poster aesthetic
- Clean layout with strong visual hierarchy
- Professional finish — this should look like a real advertisement
- Every element fully visible inside the canvas
- No clutter, strong focal point on the hero visual

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