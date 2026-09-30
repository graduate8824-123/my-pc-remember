#!/usr/bin/env bash
# MY PC REMEMBERS - Start Local Python FastAPI Backend on http://127.0.0.1:8000
set -e

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Set PYTHONPATH to project root so backend modules resolve cleanly
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "Starting MY PC REMEMBERS backend server on 127.0.0.1:8001..."
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port ${PORT:-8001} --reload
