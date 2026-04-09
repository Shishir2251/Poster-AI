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
    brand_context = f"""
    Brand Name: {brand_name}
    Tagline: {tagline}
    color palatte: primary color {primary_color}, secondary color {secondary_color}
    title font: {title_font}
    subtitle font: {subtitle_font}
    """

    # STEP 3 — AI Prompt
    base_prompt = f"""
You are a professional graphic designer creating high-quality marketing posters.

=====================
LANGUAGE RULES
=====================
{language_rules}

=====================
BRAND IDENTITY (STRICT)
=====================
{brand_context}

=====================
CONTENT
=====================
Title: {title}
Subtitle: {subtitle}
Call To Action: {cta}

=====================
CONTACT INFORMATION
=====================
Phone: {phone}
Address: {address}
Website: {website}

IMPORTANT:
- The design MUST strictly follow the brand identity
- Colors should be consistent with the brand palette
- Typography and layout must feel aligned with the brand personality
- Contact info should be clearly visible
- Place near bottom or CTA
- Do not clutter layout with contact details, but ensure they are easily found.

=====================
DESIGN DIRECTION
=====================
Style Prompt:
{design_style_prompt}

Style Preset:
{style_preset}

=====================
LAYOUT RULES
=====================
- Top: Title
- Below Title: Subtitle
- Center: Main visual
- Bottom: CTA

- Maintain safe margins
- Avoid text near edges
- Ensure strong visual hierarchy

=====================
IMAGE RULES
=====================
- Use the provided image as the MAIN SUBJECT
- DO NOT modify the subject
- Only enhance with background, typography, and layout

=====================
OUTPUT
=====================
Aspect Ratio: {output_format}

The final output should look like a premium, modern advertisement with clean layout and strong branding.

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