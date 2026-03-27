from fastapi import APIRouter
from app.schemas import PosterRequest
from app.services.ai_service import generate_poster
from app.utils.prompt_builder import build_prompt

router = APIRouter()

@router.post("/generate-variations")
async def generate_variations(data: PosterRequest):

    posters = []

    for i in range(5):

        prompt = build_prompt(data)

        image = await generate_poster(prompt)

        posters.append(f"http://127.0.0.1:8000/{image}")

    return {
        "status": "success",
        "variations": posters
    }