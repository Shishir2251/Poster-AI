from fastapi import APIRouter, UploadFile, File
import shutil

from app.services.poster_service import generate_poster

router = APIRouter()


@router.post("/generate")

async def generate_poster_api(
    image: UploadFile = File(...),
    headline: str = "",
    content: str = "",
    use_ai_content: bool = False
):

    image_path = f"uploads/{image.filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    poster = generate_poster(
        image_path=image_path,
        headline=headline,
        content=content,
        font_path="fonts/Inter-Bold.ttf",
        use_ai=use_ai_content
    )

    return {"poster_url": poster}