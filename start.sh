#!/usr/bin/env bash

echo "Installing Playwright browser..."
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright python -m playwright install chromium

echo "Starting Celery..."
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright celery -A app.worker.celery_app.celery_app worker \
  --loglevel=info \
  --pool=threads \
  --concurrency=4 &

echo "Starting FastAPI..."
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright uvicorn main:app --host 0.0.0.0 --port $PORT




# echo "Starting Celery..."
# celery -A app.worker.celery_app.celery_app worker \
#   --loglevel=info \
#   --pool=threads \
#   --concurrency=4 &

# echo "Starting FastAPI..."
# uvicorn main:app --host 0.0.0.0 --port $PORT