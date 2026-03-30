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



# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# import os

# from app.routers.upload_router import router as upload_router
# from app.routers.brand_router import router as brand_router
# from app.routers.variation_router import router as variation_router
# from app.routers.poster_router import router as poster_router
# from app.routers.download_router import router as download_router
# from app.routers.pipeline_router import router as pipeline_router
# from app.routers.ai_helper_router import router as ai_helper_router
# from app.routers.logo_router import router as logo_router
# app = FastAPI()


# @app.get("/")
# def root():
#     return {"message": "Poster AI API is running"}

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# app.mount("/generated", StaticFiles(directory=os.path.join(BASE_DIR,"generated")), name="generated")
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# # app.include_router(upload_router)
# # app.include_router(brand_router)
# # app.include_router(variation_router)
# # app.include_router(poster_router)
# # app.include_router(download_router)
# app.include_router(pipeline_router)
# app.include_router(ai_helper_router, tags=["AI Content Assistant"])
# app.include_router(logo_router, tags=["Logo Generator"])