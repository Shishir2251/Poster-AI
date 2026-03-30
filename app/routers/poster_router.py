from fastapi import APIRouter, Request
import os

router = APIRouter()

POSTER_DIR = "generated"

@router.get("/posters")
async def list_posters(request: Request):  # fix 1, import Request and add it as a parameter

    posters = []

    base_url = str(request.base_url).rstrip("/")  # fix 2, dynamically get the base URL

    for file in os.listdir(POSTER_DIR):
        posters.append(f"{base_url}/generated/{file}")  # fix 3, use the dynamic base URL instead of hardcoding it

    return {
        "posters": posters
    }