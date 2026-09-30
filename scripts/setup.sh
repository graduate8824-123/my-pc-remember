#!/usr/bin/env bash
# MY PC REMEMBERS - Setup script for local macOS (Apple Silicon M1) / Linux
set -e

echo "============================================="
echo "MY PC REMEMBERS - Local Environment Setup"
echo "============================================="

# 1. Python virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip and installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2. Node & Frontend dependencies
echo "Installing frontend dependencies..."
npm install

# 3. Create initial data & model directories
mkdir -p data/sample_documents/DSA models

# 4. Copy .env.example if .env does not exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env configuration file."
fi

echo "============================================="
echo "Setup complete!"
echo "To start the backend:  bash scripts/start_backend.sh"
echo "To start the frontend: bash scripts/start_frontend.sh"
echo "============================================="
