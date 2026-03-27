from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

GENERATED_DIR = "generated"


@router.get("/download/{poster_name}")
async def download_poster(poster_name: str):

    file_path = os.path.join(GENERATED_DIR, poster_name)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=poster_name,
        media_type="application/octet-stream"
    )