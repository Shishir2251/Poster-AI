from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.poster_routes import router as poster_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated posters as static files
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

app.include_router(poster_router, prefix="/api/poster", tags=["poster"])


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} v{settings.API_VERSION} is running"}