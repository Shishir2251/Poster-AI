from fastapi import APIRouter, UploadFile, File, Form, Request
import shutil
import os

from app.services.poster_service import generate_poster

router = APIRouter()


@router.post("/generate")
async def generate_poster_api(
    request: Request,
    image: UploadFile = File(...),
    headline: str = Form(""),
    content: str = Form(""),
    use_ai_content: bool = Form(False)
):
    os.makedirs("uploads", exist_ok=True)
    image_path = f"uploads/{image.filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    poster_path = generate_poster(
        image_path=image_path,
        headline=headline,
        content=content,
        font_path="fonts/Inter-Bold.ttf",
        use_ai=use_ai_content
    )

    # Return a full accessible URL
    base_url = str(request.base_url).rstrip("/")
    poster_url = f"{base_url}/{poster_path}"

    return {"poster_url": poster_url}