#!/usr/bin/env bash

echo "Starting Celery..."
celery -A app.worker.celery_app.celery_app worker \
  --loglevel=info \
  --pool=threads \
  --concurrency=4 &

echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port $PORT