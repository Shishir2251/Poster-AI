from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/download/{poster_name}")
async def download_poster(poster_name: str):

    file_path = f"generated/{poster_name}"

    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=poster_name
    )