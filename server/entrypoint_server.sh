#!/bin/bash

set -e

echo "running FastAPI gunicorn server.."

(cd /app/app && python -m alembic upgrade head)
python -m uvicorn app.src.main:app --reload --port=80 --host=0.0.0.0
# python -m gunicorn app.src.main:app --reload --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
