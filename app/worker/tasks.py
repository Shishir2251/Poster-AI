from app.worker.celery_app import celery_app
import time
from app.services.ai_service import generate_poster, generate_poster_fields
# import cloudinary.uploader
from app.services.logo_service import generate_logo
from app.services.ai_service import regenerate_poster


@celery_app.task
def test_task(x, y):
    time.sleep(5)  # Simulate a long-running task
    print(f"Task completed with inputs: {x} and {y}")
    return x + y

@celery_app.task
def generate_poster_task(prompt,content, output_format = "1:1", image_path=None):
    return generate_poster(prompt, content, output_format, image_path)


@celery_app.task
def generate_poster_fields_task(user_idea:str):
    return generate_poster_fields(user_idea)


@celery_app.task
def generate_logo_task(data, path):
    return generate_logo(data, path)

@celery_app.task
def regenerate_poster_task(prompt, output_format, image_path=None):
    return regenerate_poster(prompt, output_format, image_path)



# celery -A app.worker.celery_app.celery_app worker --loglevel=info --pool=threads --concurrency=4

