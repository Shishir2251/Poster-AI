from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
from typing import Optional
from app.schemas import get_language_rules
router = APIRouter()

from app.worker.tasks import generate_poster_task, generate_poster_fields_task

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


@router.post("/generate-poster-complete")
async def generate_poster_complete(
    # request: Request,  # fix 1, importing the request
    title: str = Form(...),
    title_font: str = Form("Times new roman bold"),
    subtitle: str = Form(...),
    subtitle_font: str = Form("monospace italic"),
    tagline: str = Form("Your Tagline Here"),
    # description: str = Form(...),
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
    language: str = Form("hebrew"), # poster lanugae, default to english but can be set to other languages
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
    # brand_context = f"""
    # Brand Name: {brand_name}
    # Tagline: {tagline}
    # color palatte: primary color {primary_color}, secondary color {secondary_color}
    # title font: {title_font}
    # subtitle font: {subtitle_font}
    # """

    # STEP 3 — AI Prompt
    base_prompt = f"""
You are a senior professional graphic designer specializing in high-impact marketing posters.

=====================
LANGUAGE RULES (CRITICAL — NEVER VIOLATE)
=====================
{language_rules}

=====================
BRAND IDENTITY (STRICT)
=====================
Brand Name: {brand_name}
Tagline: {tagline}
Primary Color: {primary_color}
Secondary Color: {secondary_color}
Title Font Style: {title_font}
Subtitle Font Style: {subtitle_font}

- ALL design decisions must reflect this brand identity
- Colors must be consistent and intentional — no random colors
- Typography must feel aligned with the brand personality

=====================
CONTENT (RENDER EXACTLY AS GIVEN)
=====================
Title: {title}
Subtitle: {subtitle}
Call To Action: {cta}

- Render every word EXACTLY as provided — do not paraphrase, shorten, or rewrite
- Title must be the most visually dominant text element
- CTA must look like a clickable button with contrast background

=====================
CONTACT INFORMATION
=====================
Phone: {phone}
Address: {address}
Website: {website}

- Place all contact info at the very bottom of the poster
- Use small but legible font size
- Do NOT omit any contact field
- Do NOT clutter — keep it compact and clean
- Website URL must be fully visible — never truncate or clip it

=====================
DESIGN DIRECTION
=====================
Style: {design_style_prompt}
Preset: {style_preset}

=====================
LAYOUT RULES (STRICT — ENFORCE PRECISELY)
=====================
SAFE ZONE:
- Imagine a hard boundary 15% inward from ALL four edges
- NO text, NO button, NO content of any kind may appear outside this safe zone
- This applies to every corner and every edge — top, bottom, left, right

TEXT WIDTH:
- Title max width: 80% of canvas width
- If title is long, reduce font size or break into 2 lines — NEVER overflow
- Subtitle max width: 75% of canvas width
- No single line of text should stretch beyond 80% of canvas width

VERTICAL LAYOUT (top to bottom):
1. Title — positioned in top section, fully inside safe zone
2. Subtitle — directly below title, smaller font
3. Main Visual / Product Image — center of canvas
4. CTA Button — centered, at roughly 78% vertical position
5. Contact Info — at roughly 90% vertical position, small font

HIERARCHY:
- Title > Subtitle > CTA > Contact Info (in terms of visual weight)
- Strong contrast between text and background at every layer

=====================
IMAGE RULES
=====================
- Use the provided image as the MAIN SUBJECT of the poster
- DO NOT alter, modify, distort, or reimagine the product
- Place it prominently in the center zone
- Only add: background, lighting effects, shadows, decorative elements
- The product must look exactly as uploaded — same shape, same color, same form

=====================
OUTPUT QUALITY
=====================
Aspect Ratio: {output_format}
- Final result must look like a premium, print-ready marketing poster
- Clean layout, strong visual hierarchy, professional finish
- No clutter, no overcrowding, no overflowing text
- Every element must be fully visible and inside the canvas

Creative variation number: {{variation_number}}
"""

    #  Dynamic base URL
    # base_url = str(request.base_url).rstrip("/")

    tasks = []

    # STEP 4 — Generate Variations
    for i in range(variations):

        # unique_prompt = base_prompt + f"\nCreative variation number {i+1}"
        unique_prompt = base_prompt.replace("{variation_number}", str(i+1))

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