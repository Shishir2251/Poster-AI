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
        "layout": layout_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "design_style_prompt": design_style_prompt,
    }

    # ── Background-only prompt for Nano Banana ─────────────────────────────────
    # CRITICAL: zero text instructions here — Claude handles all text downstream
    # ── Background-only prompt for Nano Banana ────────────────────────────────
    background_prompt = f"""
You are a world-class visual artist and cinematographer.
Generate a PHOTOREALISTIC BACKGROUND IMAGE ONLY — absolutely no text.

═══════════════════════════════════════════
ABSOLUTE RULE — ZERO TEXT
═══════════════════════════════════════════
- Do NOT render any letters, words, numbers, or symbols
- Do NOT draw placeholder boxes, UI elements, buttons, or badges
- Do NOT add watermarks, logos, or decorative writing
- This is a pure background canvas — text will be composited later

═══════════════════════════════════════════
BRAND CONTEXT
═══════════════════════════════════════════
Language   : {language}
Brand      : {brand_name}
Product    : {title}
Subtitle   : {subtitle}
Style      : {design_style_prompt}
Preset     : {style_preset}
Primary    : {primary_color}
Secondary  : {secondary_color}

═══════════════════════════════════════════
PRODUCT / SUBJECT TO GENERATE
═══════════════════════════════════════════
The poster is for: "{title}"
Category hint from style preset: {style_preset}

You MUST generate a photorealistic hero subject relevant to this product/brand.
- Understand the product from its name and context — even if the name is in Hebrew or another language
- Generate the actual product or a lifestyle scene featuring it
- Do NOT generate an empty gradient — there MUST be a recognisable subject in ZONE 2
- Examples: if product is a phone → show a sleek smartphone; if food → show the dish; if fashion → show clothing

═══════════════════════════════════════════
COMPOSITION
═══════════════════════════════════════════
{layout_description}

ZONE 1 — TOP (0%–22%)    : Flat, clean background — NOTHING here
ZONE 2 — HERO (22%–65%)  : Main subject / scene — MUST have a product or scene
ZONE 3 — BOTTOM (65%–100%): Flat, clean background — NOTHING here

═══════════════════════════════════════════
VISUAL DIRECTION
═══════════════════════════════════════════
- Cinematic, immersive — high-end editorial photography quality
- Professional three-point studio lighting
- Rich textures, atmospheric depth, premium feel
- Dominant color: {primary_color} | Accent: {secondary_color}
- If product image is uploaded: place it faithfully as the hero in ZONE 2
- If no image uploaded: generate the product scene based on brand context above
- Surprising, premium, memorable — not generic stock photography

Aspect ratio: {output_format}
"""

    # ── Dispatch Celery tasks ──────────────────────────────────────────────────
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






#-----------------previous working code-----------------
# from fastapi import APIRouter, UploadFile, File, Form
# import uuid
# import os
# from typing import Optional
# # from app.schemas import get_language_rules
# router = APIRouter()

# from app.worker.tasks import generate_poster_task

# import random

# def get_random_layout() -> dict:
#     layouts = [
#         {
#             "name": "center",
#             "description": """
# COMPOSITION: CENTER FOCUSED
# - Place the main subject dead center horizontally and vertically within ZONE 2
# - Equal empty space on left and right
# - Text will be placed above and below the subject
# """
#         },
#         {
#             "name": "left",
#             "description": """
# COMPOSITION: LEFT ALIGNED
# - Place the main subject on the LEFT side of the canvas within ZONE 2
# - Subject should occupy the left 55% of the canvas width
# - Leave the right 40% as clean, empty background
# - Text will be placed on the right side and in top/bottom zones
# """
#         },
#         {
#             "name": "right",
#             "description": """
# COMPOSITION: RIGHT ALIGNED  
# - Place the main subject on the RIGHT side of the canvas within ZONE 2
# - Subject should occupy the right 55% of the canvas width
# - Leave the left 40% as clean, empty background
# - Text will be placed on the left side and in top/bottom zones
# """
#         },
#         {
#             "name": "bottom_center",
#             "description": """
# COMPOSITION: BOTTOM ANCHORED
# - Place the main subject at the BOTTOM of ZONE 2, centered horizontally
# - Subject should sit at the lower portion of ZONE 2 (50% to 62%)
# - Leave the upper portion of ZONE 2 as atmospheric background
# - Creates a dramatic look with subject emerging from the bottom
# """
#         }
#     ]
    
#     chosen = random.choice(layouts)
#     print(f"Selected layout: {chosen['name']}")
#     # return chosen["description"]
#     return chosen

# UPLOAD_DIR = "uploads"
# GENERATED_DIR = "generated"

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(GENERATED_DIR, exist_ok=True)


# @router.post("/generate-poster-complete")
# async def generate_poster_complete(
#     title: str = Form(...),
#     title_font: str = Form("Rubik-Bold.ttf"),
#     subtitle: str = Form(...),
#     subtitle_font: str = Form("Rubik-Regular.ttf"),
#     tagline: str = Form("Your Tagline Here"),
#     brand_name: str = Form(...),
#     primary_color: str = Form(...),
#     secondary_color: str = Form(...),
#     cta: str = Form("Call to action button text"),
#     phone: str = Form(None),
#     address: str = Form(None),
#     website: str = Form(None),
#     additional_info: str = Form(None),  # add after website field
#     design_style_prompt: str = Form("Make this poster look modern and minimalistic with a touch of vintage"),
#     style_preset: str = Form("Modern Minimal"),
#     output_format: str = Form("1:1 square"),
#     language: str = Form("hebrew"),
#     variations: int = Form(1),
#     image: Optional[UploadFile] = File(None)
# ):
#     uploaded_image_path = None

#     if image:
#         ext = image.filename.split(".")[-1]
#         image_name = f"{uuid.uuid4()}.{ext}"
#         uploaded_image_path = f"{UPLOAD_DIR}/{image_name}"
#         with open(uploaded_image_path, "wb") as buffer:
#             buffer.write(await image.read())

#     content = {
#         "title": title,
#         "subtitle": subtitle,
#         "cta": cta,
#         "brand_name": brand_name,
#         "tagline": tagline,
#         "phone": phone or "",
#         "address": address or "",
#         "website": website or "",
#         "additional_info": additional_info or ""
#     }
#     layout_instruction = get_random_layout()
#     layout_name = layout_instruction["name"]
#     layout_description = layout_instruction["description"]
#     content["layout"] = layout_name


#     base_prompt = f"""
# ROLE: You are a world-class Creative Director and Graphic Designer.
# TASK: Create a premium, print-ready marketing poster for {brand_name}.

# SUBJECT & COMPOSITION:
# - Layout Goal: {layout_description}
# - Composition: Create a cinematic scene featuring the brand elements. 
# - Lighting: Use professional studio lighting (three-point setup) that complements the {primary_color} palette.
# - Background: A high-detail, immersive environment that reflects the "{design_style_prompt}" aesthetic.

# TYPOGRAPHY & CONTENT (HEBREW):
# Render the following text EXACTLY as written in modern Hebrew script. 
# CRITICAL: Use Right-to-Left (RTL) reading order.

# 1. MAIN TITLE: "{content['title']}" 
#    - Style: Bold, artistic, and integrated into the scene's 3D space.
#    - font : {title_font}
# 2. SUBTITLE: "{content['subtitle']}" 
#    - Style: Clean, elegant, placed with clear hierarchy below the title.
#    - font : {subtitle_font}
# 3. CALL TO ACTION: "{content['cta']}" 
#    - Style: Rendered inside a high-quality UI element or button that matches the {secondary_color} accent.

# INTEGRATION RULES:
# - All text must be in the {language} language
# - If language is Hebrew, the text must be rendered in Right-to-Left (RTL) order.
# - The Hebrew text must interact with the environment (e.g., casting soft shadows or reflecting the scene's light).
# - Ensure 100% legibility while maintaining an editorial, high-end magazine look.
# - Style Preset: {style_preset}
# """

#     tasks = []
#     for i in range(variations):
#         unique_prompt = base_prompt.replace("{variation_number}", str(i + 1))
#         task = generate_poster_task.delay(
#             unique_prompt,
#             content,
#             output_format,
#             uploaded_image_path
#         )
#         tasks.append(task.id)

#     return {
#         "status": "success",
#         "message": f"Poster generation started with {variations} variations.",
#         "task_ids": tasks
#     }