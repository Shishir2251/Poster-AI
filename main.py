from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.upload_router import router as upload_router
from app.routers.brand_router import router as brand_router
from app.routers.variation_router import router as variation_router
from app.routers.poster_router import router as poster_router
from app.routers.download_router import router as download_router
from app.routers.pipeline_router import router as pipeline_router

app = FastAPI()

app.mount("/generated", StaticFiles(directory="generated"), name="generated")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# app.include_router(upload_router)
# app.include_router(brand_router)
# app.include_router(variation_router)
# app.include_router(poster_router)
# app.include_router(download_router)
app.include_router(pipeline_router)