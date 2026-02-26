#!/bin/bash
# Docker image build script for Cloudera AI (CML) Model deployments.
# This script runs during the image build phase when deploying CML-native Models.

set -e

echo "=== Installing Python dependencies with CUDA support ==="

# Install llama-cpp-python with CUDA GPU acceleration for Cloudera AI
CMAKE_ARGS="-DGGML_CUDA=on" pip install -U llama-cpp-python --no-cache-dir

# Install remaining Python dependencies
pip install -r backend/requirements.txt

echo "=== Build complete ==="
echo "NOTE: React frontend (frontend/dist/) is pre-built and committed to git."
echo "      Run 'cd frontend && npm run build' locally to update the UI build."
