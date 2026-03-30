from fastapi import APIRouter, UploadFile, File, Form, Request
from app.services.logo_service import generate_logo
import os
from schemas import get_language_rules

router = APIRouter()

@router.post("/generate-logo")
async def generate_logo_api(
    request: Request,  # fix 1
    brand_name: str = Form(...),
    tagline: str = Form(None),
    vision: str = Form(None),
    industry: str = Form(None),
    logo_style: str = Form(None),
    color_palette: str = Form(None),
    language: str = Form("English"), # english default, but can be set to other languages
    reference_image: UploadFile = File(None)
):
    image_path = None

    # fix 2
    os.makedirs("uploads", exist_ok=True)

    if reference_image:
        image_path = f"uploads/{reference_image.filename}"
        with open(image_path, "wb") as f:
            f.write(await reference_image.read())

    data = {
        "brand_name": brand_name,
        "tagline": tagline,
        "vision": vision,
        "industry": industry,
        "logo_style": logo_style,
        "color_palette": color_palette,
        "language": language
    }

    result = await generate_logo(data, image_path)

    # fix 3- dynamic url
    base_url = str(request.base_url).rstrip("/")

    logos = []
    for path in result:
        filename = os.path.basename(path)
        logos.append({
            "view_url": f"{base_url}/generated/{filename}",
            "download_url": f"{base_url}/download/{filename}"
        })

    return {
        "success": True,
        "logos": logos
    }