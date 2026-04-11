from fastapi import APIRouter, Form
from typing import Optional
from app.worker.tasks import generate_poster_task
from app.schemas import get_language_rules

router = APIRouter()


@router.post("/regenerate-poster")
async def regenerate_poster(
    # original context
    original_prompt: Optional[str] = Form(None),
    language: Optional[str] = Form("english"),

    # content overrides
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    tagline: Optional[str] = Form(None),
    brand_name: Optional[str] = Form(None),

    cta: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    website: Optional[str] = Form(None),

    # styling
    title_font: Optional[str] = Form(None),
    subtitle_font: Optional[str] = Form(None),
    primary_color: Optional[str] = Form(None),
    secondary_color: Optional[str] = Form(None),

    design_style_prompt: Optional[str] = Form(None),
    style_preset: Optional[str] = Form(None),

    # layout
    output_format: Optional[str] = Form("1:1 square"),
    variations: int = Form(1),

    image_url: Optional[str] = Form(None)
):
    """
    Regenerate poster with partial updates.
    """

    language_rules = get_language_rules(language or "english")

    # STEP 1 — BUILD PROMPT

    base_prompt = f"""
You are a senior professional graphic designer specializing in high-impact marketing posters.

=====================
REGENERATION MODE (IMPORTANT)
=====================
- You are editing an EXISTING poster
- Apply ONLY requested changes
- Preserve layout, spacing, and hierarchy
- Keep visual consistency unless change is required

=====================
LANGUAGE RULES
=====================
{language_rules}

=====================
ORIGINAL CONTEXT
=====================
{original_prompt if original_prompt else "No original prompt provided"}

=====================
USER REQUESTED CHANGES
=====================
Title: {title}
Subtitle: {subtitle}
Tagline: {tagline}
Brand Name: {brand_name}

CTA: {cta}
Phone: {phone}
Address: {address}
Website: {website}

Title Font: {title_font}
Subtitle Font: {subtitle_font}

Primary Color: {primary_color}
Secondary Color: {secondary_color}

Style Direction: {design_style_prompt}
Style Preset: {style_preset}

=====================
RULES
=====================
- If a field is NULL → keep original unchanged
- Modify ONLY provided fields
- Do NOT redesign entire poster unless necessary
- Maintain professional layout and spacing

=====================
IMAGE RULES
=====================
- The provided image_url is the BASE poster
- Apply edits on top of it
- If no image_url → generate fresh variation

=====================
OUTPUT
=====================
- High-quality marketing poster
- Clean typography
- Strong hierarchy
- No overflow

Creative variation number: {{variation_number}}
"""

    # STEP 2 — TASK CREATION

    tasks = []

    for i in range(variations):

        unique_prompt = base_prompt.replace(
            "{variation_number}", str(i + 1)
        )

        task = generate_poster_task.delay(
            unique_prompt,
            output_format,
            image_url   
        )

        tasks.append(task.id)

    return {
        "status": "success",
        "message": f"Poster regeneration started with {variations} variations.",
        "task_ids": tasks
    }










# from fastapi import APIRouter, UploadFile, File, Form
# from typing import Optional
# import uuid

# from app.worker.tasks import generate_poster_task
# from app.schemas import get_language_rules

# router = APIRouter()


# @router.post("/regenerate-poster")
# async def regenerate_poster(
#     # optional identity / structure fields
#     original_prompt: Optional[str] = Form(None),
#     language: Optional[str] = Form(None),

#     # optional brand overrides
#     title: Optional[str] = Form(None),
#     subtitle: Optional[str] = Form(None),
#     tagline: Optional[str] = Form(None),
#     brand_name: Optional[str] = Form(None),

#     # styling tweaks
#     title_font: Optional[str] = Form(None),
#     subtitle_font: Optional[str] = Form(None),
#     primary_color: Optional[str] = Form(None),
#     secondary_color: Optional[str] = Form(None),
#     design_style_prompt: Optional[str] = Form(None),
#     style_preset: Optional[str] = Form(None),

#     # content overrides
#     cta: Optional[str] = Form(None),
#     phone: Optional[str] = Form(None),
#     address: Optional[str] = Form(None),
#     website: Optional[str] = Form(None),

#     # layout control
#     output_format: Optional[str] = Form(None),
#     variations: int = Form(1),

#     # optional new image
#     image_url: Optional[str] = Form(None)
# ):
#     """
#     Regenerate poster with partial updates.
#     Everything is optional — only overrides what user provides.
#     """

#     language_rules = get_language_rules(language or "english")

#     uploaded_image_path = None

#     # STEP 1 — handle optional image (same as your current system)
#     if image_url:
#         ext = image.filename.split(".")[-1]
#         image_name = f"{uuid.uuid4()}.{ext}"
#         uploaded_image_path = f"uploads/{image_name}"

#         with open(uploaded_image_path, "wb") as buffer:
#             buffer.write(await image.read())

#     # STEP 2 — BUILD DYNAMIC REGEN PROMPT

#     base_prompt = f"""
# You are a senior professional graphic designer specializing in high-impact marketing posters.

# =====================
# REGENERATION MODE (IMPORTANT)
# =====================
# - You are modifying an EXISTING poster design
# - Only apply changes requested by the user
# - Keep all unchanged elements consistent with original design intent
# - Maintain visual harmony and brand identity

# =====================
# LANGUAGE RULES
# =====================
# {language_rules}

# =====================
# ORIGINAL CONTEXT (if provided)
# =====================
# {original_prompt if original_prompt else "No original prompt provided"}

# =====================
# OVERRIDES (ONLY APPLY IF NOT NULL)
# =====================
# Title: {title}
# Subtitle: {subtitle}
# Tagline: {tagline}
# Brand Name: {brand_name}

# CTA: {cta}
# Phone: {phone}
# Address: {address}
# Website: {website}

# Title Font: {title_font}
# Subtitle Font: {subtitle_font}

# Primary Color: {primary_color}
# Secondary Color: {secondary_color}

# Style Direction: {design_style_prompt}
# Style Preset: {style_preset}

# =====================
# REGENERATION RULES
# =====================
# - If a field is NULL → keep original value unchanged
# - If a field is provided → replace ONLY that element
# - Do NOT redesign everything unless explicitly required
# - Preserve layout unless layout change is implied
# - Maintain spacing, hierarchy, and visual balance

# =====================
# IMAGE RULES
# =====================
# - If new image is provided → replace main subject only
# - If no image → keep original visual structure
# - Do NOT distort product or change its identity

# =====================
# OUTPUT REQUIREMENTS
# =====================
# - High-quality marketing poster
# - Clean typography
# - Strong hierarchy
# - No overflow outside canvas
# - Professional commercial design

# Creative variation number: {{variation_number}}
# """

#     tasks = []

#     # STEP 3 — generate variations
#     for i in range(variations):

#         unique_prompt = base_prompt.replace(
#             "{variation_number}", str(i + 1)
#         )

#         task = generate_poster_task.delay(
#             unique_prompt,
#             output_format,
#             uploaded_image_path
#         )

#         tasks.append(task.id)

#     return {
#         "status": "success",
#         "message": f"Poster regeneration started with {variations} variations.",
#         "task_ids": tasks
#     }