from app.worker.celery_app import celery_app
import time

@celery_app.task

def test_task(x, y):
    time.sleep(5)  # Simulate a long-running task
    print(f"Task completed with inputs: {x} and {y}")
    return x + y

