from app.worker.celery_app import celery_app
import time
from app.services.ai_service import generate_poster, generate_poster_fields
# import cloudinary.uploader


@celery_app.task
def test_task(x, y):
    time.sleep(5)  # Simulate a long-running task
    print(f"Task completed with inputs: {x} and {y}")
    return x + y

@celery_app.task
def generate_poster_task(prompt, output_format = "1:1", image_path=None):
    return generate_poster(prompt, output_format, image_path)


@celery_app.task
def generate_poster_fields_task(user_idea:str):
    return generate_poster_fields(user_idea)




