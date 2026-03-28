from fastapi import APIRouter, UploadFile, File, Form
from app.services.logo_service import generate_logo

router = APIRouter()

@router.post("/generate-logo")
async def generate_logo_api(
    brand_name: str = Form(...),
    tagline: str = Form(None),
    vision: str = Form(None),
    industry: str = Form(None),
    logo_style: str = Form(None),
    color_palette: str = Form(None),
    reference_image: UploadFile = File(None)
):

    image_path = None

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
        "color_palette": color_palette
    }

    result = await generate_logo(data, image_path)
    base_url = "http://127.0.0.1:8000"


    return {
        "success": True,
        "logos": [
        "http://127.0.0.1:8000/generated/logo1.png"]
    }