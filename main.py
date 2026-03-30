from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routers.pipeline_router import router as pipeline_router
from app.routers.ai_helper_router import router as ai_helper_router
from app.routers.logo_router import router as logo_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Poster AI API is running"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

generated_path = os.path.join(BASE_DIR, "generated")
uploads_path = os.path.join(BASE_DIR, "uploads")

# create folders if they don't exist
os.makedirs(generated_path, exist_ok=True)
os.makedirs(uploads_path, exist_ok=True)

app.mount("/generated", StaticFiles(directory=generated_path), name="generated")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

app.include_router(pipeline_router)
app.include_router(ai_helper_router, tags=["AI Content Assistant"])
app.include_router(logo_router, tags=["Logo Generator"])