from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import generate_poster_fields

router = APIRouter()

class IdeaInput(BaseModel):
    idea: str


@router.post("/ai-generate-poster-fields")
async def ai_generate_fields(data: IdeaInput):

    result = await generate_poster_fields(data.idea)

    return {
        "success": True,
        "generated_fields": result
    }