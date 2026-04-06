from fastapi import APIRouter
from pydantic import BaseModel
# from app.services.ai_service import generate_poster_fields
from app.worker.tasks import generate_poster_fields_task

router = APIRouter()

class IdeaInput(BaseModel):
    idea: str


@router.post("/ai-generate-poster-fields")
async def ai_generate_fields(data: IdeaInput):

    result =  generate_poster_fields_task.delay(data.idea) # no need to use get()

    return {
        "success": True,
        "generated_fields": result.id
    }