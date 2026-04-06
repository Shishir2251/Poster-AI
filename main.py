from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routers.pipeline_router import router as pipeline_router
from app.routers.ai_helper_router import router as ai_helper_router
from app.routers.logo_router import router as logo_router
from app.worker.tasks import test_task
from celery.result import AsyncResult
from app.worker.celery_app import celery_app




app = FastAPI()

@app.get("/")
def root():
    return {"message": "Poster AI API is running"}

#endpoint to call task and status
@app.get("/test-celery")
def test_celery():
    task = test_task.delay(5, 10)
    return {
        "job_id": task.id,
        "status": task.status
        # "result": task.result   # This will be None immediately after dispatch
    }

#endpoint to get celery test task result
@app.get("/result/{job_id}")
def get_result(job_id: str):
    task_result = AsyncResult(job_id, app=celery_app)

    if task_result.state == "SUCCESS":
        return{
            "status": "Task completed!",
            "result": task_result.result
        }
    
    return {
        "status": task_result.state
    }


@app.post("/generate_poster_/result/{job_id}")
def get_poster_result(job_id:str):
    try:
        result = AsyncResult(job_id, app=celery_app)

    except Exception as e:
        return {
            "status": "error",
            "message": "Error fetching task result" + str(e)
        }

    if result.state == "SUCCESS":
        return {
            "status": result.status,
            "poster_url": result.result
        }
    if result.state == "FAILURE":
        return {
        "status": "FAILURE",
        "error": str(result.result)
    }
    
    return{
        "status": result.state
    }

@app.post("/generate_logo/result/{job_id}")
def get_logo_result(job_id:str):
    try:
        result = AsyncResult(job_id, app=celery_app)
    
    except Exception as e:
        return {
            "status": "error",
            "message": "Error fetching task result" + str(e)
        }
    
    if result.state == "SUCCESS":
        return {
            "status": result.status,
            "logo_urls": result.result
        }
    
    return {
        "status": result.state
    }

@app.get("/poster_fields/result/{job_id}")
def get_result(job_id: str):
    task_result = AsyncResult(job_id, app=celery_app)

    if task_result.state == "SUCCESS":
        return {
            "status": "completed",
            "data": task_result.result
        }

    return {
        "status": task_result.state
    }





    # if task_result.state == 'PENDING':
    #     return {"status": "Task is still pending..."}
    # elif task_result.state == 'SUCCESS':
    #     return {"status": "Task completed!", "result": task_result.result}
    # else:
    #     return {"status": f"Task is in state: {task_result.state}"}



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