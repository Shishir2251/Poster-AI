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
- Recreate the poster from scratch while closely matching the original layout and composition
- Treat the provided image (if any) as a visual reference, not something to lightly modify
- Maintain overall visual consistency unless changes are explicitly requested

=====================
LANGUAGE RULES (CRITICAL — NEVER VIOLATE)
=====================
{language_rules}

=====================
ORIGINAL CONTEXT
=====================
{original_prompt if original_prompt else "No original prompt provided"}

=====================
USER REQUESTED CHANGES
=====================
Title: {title if title else "UNCHANGED"}
Subtitle: {subtitle if subtitle else "UNCHANGED"}
Tagline: {tagline if tagline else "UNCHANGED"}
Brand Name: {brand_name if brand_name else "UNCHANGED"}

CTA: {cta if cta else "UNCHANGED"}
Phone: {phone if phone else "UNCHANGED"}
Address: {address if address else "UNCHANGED"}
Website: {website if website else "UNCHANGED"}

Title Font Style: {title_font if title_font else "UNCHANGED"}
Subtitle Font Style: {subtitle_font if subtitle_font else "UNCHANGED"}

Primary Color: {primary_color if primary_color else "UNCHANGED"}
Secondary Color: {secondary_color if secondary_color else "UNCHANGED"}

Style Direction: {design_style_prompt if design_style_prompt else "UNCHANGED"}
Style Preset: {style_preset if style_preset else "UNCHANGED"}

=====================
UNCHANGED FIELD RULES (CRITICAL)
=====================
- Any field marked as "UNCHANGED" must remain EXACTLY the same as in the original design
- Do NOT rewrite, rephrase, reposition, or restyle unchanged fields
- Preserve the exact text, placement, size, and visual appearance of unchanged elements
- Only modify fields that contain new values

=====================
TEXT ACCURACY RULES (CRITICAL)
=====================
- Use EXACT text provided in each field
- Do NOT rephrase, translate, or modify wording
- Do NOT add extra words
- Preserve capitalization exactly
- Ensure all text is clearly readable and not distorted

=====================
LAYOUT CONSISTENCY
=====================
- Maintain similar positioning of elements (top, center, bottom)
- Keep hierarchy:
  Title = largest and most prominent  
  Subtitle = secondary  
  Tagline / body = smaller  
  CTA = clear and visible  
- Preserve alignment style (centered, left, or right aligned)
- Keep spacing, margins, and padding balanced

=====================
STYLE & COLOR CONTROL
=====================
- If colors are provided → apply them consistently across the design
- If font styles are provided → match similar visual style (do not require exact font match)
- Maintain strong contrast and readability

=====================
IMAGE RULES
=====================
- If image_url is provided:
  - Use it as the base visual reference
  - Match layout, structure, and composition closely
  - Do NOT ignore the reference image
- If no image_url:
  - Generate a new high-quality poster based on context

=====================
VARIATION CONTROL
=====================
- This is variation #{'{variation_number}'}
- Keep content identical across variations
- Introduce subtle differences in layout, typography, or visual balance
- Do NOT drastically change the design concept

=====================
OUTPUT REQUIREMENTS
=====================
Aspect Ratio: {output_format}
- High-quality, professional marketing poster
- Clean typography and strong hierarchy
- Ensure all text fits within boundaries
- No overflow, clipping, or cutoff
- Visually balanced and aesthetically polished
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