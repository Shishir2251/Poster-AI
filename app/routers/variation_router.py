from fastapi import APIRouter, Request
from app.schemas import PosterRequest
from app.services.ai_service import generate_poster
from app.utils.prompt_builder import build_prompt
import os

router = APIRouter()

@router.post("/generate-variations")
async def generate_variations(request: Request, data: PosterRequest):  # fix 1, adding requrest

    posters = []

    base_url = str(request.base_url).rstrip("/")  # fix 2, dynamically get the base URL instead of hardcoding it

    for i in range(5):

        prompt = build_prompt(data)

        image_path = await generate_poster(prompt)

        filename = os.path.basename(image_path)  # fix 3, use os.path.basename for safer file name extraction

        posters.append(f"{base_url}/generated/{filename}")  # using the base url in path

    return {
        "status": "success",
        "variations": posters
    }


# from fastapi import APIRouter
# from app.schemas import PosterRequest
# from app.services.ai_service import generate_poster
# from app.utils.prompt_builder import build_prompt

# router = APIRouter()

# @router.post("/generate-variations")
# async def generate_variations(data: PosterRequest):

#     posters = []

#     for i in range(5):

#         prompt = build_prompt(data)

#         image = await generate_poster(prompt)

#         posters.append(f"http://127.0.0.1:8000/{image}")

#     return {
#         "status": "success",
#         "variations": posters
#     }