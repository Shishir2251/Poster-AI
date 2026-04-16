from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
from typing import Optional
from app.schemas import get_language_rules
router = APIRouter()

from app.worker.tasks import generate_poster_task
from app.schemas import TEXT_PLACEHOLDER_RULES, HIERARCHY_RULES

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
    
    


    tasks = []
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
CRITICAL: BACKGROUND TEMPLATE ONLY
=====================
You are generating a POSTER BACKGROUND only.
A separate text rendering system will add ALL text afterward.
DO NOT render any text, characters, numbers, or letters anywhere.
No placeholder bars, no wireframe boxes, no mockup shapes.
Think of it as a billboard before the text is printed on it.

=====================
BRAND IDENTITY (STRICT)
=====================
Brand color palette: {primary_color} and {secondary_color}
Title Font Style: {title_font}
Subtitle Font Style: {subtitle_font}

- ALL design decisions must reflect this brand identity
- Colors must be consistent and intentional
- Typography must feel aligned with brand personality

=====================
CONTACT INFORMATION ZONE
=====================
- Reserve a clean footer area for contact information
- DO NOT draw any text, lines, or placeholder shapes
- Just leave clean flat background in the footer area

=====================
DESIGN DIRECTION
=====================
Style: {design_style_prompt}
Preset: {style_preset}

=====================
LAYOUT RULES (STRICT)
=====================
SAFE ZONE:
- Hard boundary 15% inward from ALL four edges
- NO content outside this safe zone

VERTICAL ORDER (top to bottom):
1. TOP ZONE (0% to 28%)   — completely clean {primary_color} background, nothing here
2. CENTER ZONE (28% to 68%) — main hero visual/product ONLY, strictly within this zone
3. CTA ZONE (74% to 82%)  — one empty rounded pill button shape, filled with {secondary_color}, nothing inside
4. BOTTOM ZONE (82% to 100%) — clean flat background, completely empty

=====================
IMAGE RULES
=====================
- Use the provided image as the MAIN SUBJECT
- Do NOT alter, distort, or reimagine the product
- Place it strictly within CENTER ZONE (28% to 68%) only
- Scale the product down if needed to fit within this zone
- Only add: background, lighting, shadows, decorative elements
- Product must look exactly as uploaded

=====================
OUTPUT QUALITY
=====================
Aspect Ratio: {output_format}
- Premium, print-ready marketing poster
- Clean layout, strong visual hierarchy, professional finish
- No clutter, no overflowing text
- Every element fully visible inside the canvas

Creative variation number: {{variation_number}}
"""

    # STEP 4 — Generate Variations
    for i in range(variations):
        # unique_prompt = base_prompt + f"\nCreative variation number {i+1}"
        unique_prompt = base_prompt.replace("{variation_number}", str(i+1))

        task = generate_poster_task.delay(
            unique_prompt,
            content,
            output_format,
            uploaded_image_path
        )

        tasks.append(task.id)
    
    return{
        "status": "success",
        "message": f"Poster generation started with {variations} variations. You can check the status of your posters using the task IDs.",
        "task_ids": tasks
    }
