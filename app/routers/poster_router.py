from fastapi import APIRouter
import os

router = APIRouter()

POSTER_DIR = "generated"

@router.get("/posters")
async def list_posters():

    posters = []

    for file in os.listdir(POSTER_DIR):

        posters.append(f"http://127.0.0.1:8000/generated/{file}")

    return {
        "posters": posters
    }