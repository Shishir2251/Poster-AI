from celery import Celery

from dotenv import load_dotenv
import os

load_dotenv()

# celery_app = Celery(
#     "worker",
#     broker=os.getenv("REDIS_URL"),
#     backend=os.getenv("REDIS_URL")
# )

celery_app = Celery(
    "worker",
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND")
)

# print("Celery broker URL:", os.environ.get("CELERY_BROKER_URL"))
# print("Celery result backend URL:", os.environ.get("CELERY_RESULT_BACKEND"))

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC'
)

import app.worker.tasks