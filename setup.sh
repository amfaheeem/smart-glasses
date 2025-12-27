#!/bin/bash
# Quick setup script for Smart Glasses Pipeline

set -e

echo "🕶️  Smart Glasses Navigation Pipeline - Setup"
echo "=============================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $PYTHON_VERSION"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --user fastapi uvicorn[standard] opencv-python \
    pydantic python-multipart websockets numpy \
    pytest pytest-asyncio
echo ""

# Generate sample video
echo "🎬 Generating sample video..."
cd "$(dirname "$0")"
PYTHONPATH=. python3 apps/generate_sample.py
echo ""

# Run tests
echo "🧪 Running tests..."
PYTHONPATH=. python3 -m pytest tests/ -v --tb=short
echo ""

echo "✅ Setup complete!"
echo ""
echo "To start the pipeline:"
echo "  PYTHONPATH=. python3 apps/run_replay.py"
echo ""
echo "Then open: http://localhost:8000"
echo ""

