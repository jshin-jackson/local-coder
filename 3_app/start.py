"""
AMP Step 3 — Start Application

Launches the FastAPI server as a CML Application.
FastAPI serves both:
  - /api/*      → REST + SSE code generation API
  - /*          → React frontend static files (from frontend/dist/)

CML Application requires the server to listen on:
  - Host: 0.0.0.0
  - Port: CDSW_APP_PORT (environment variable set by CML)
"""

import os
import sys
from pathlib import Path

# Ensure the backend package is importable
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

import uvicorn

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("CDSW_APP_PORT", os.getenv("PORT", "8000")))


if __name__ == "__main__":
    print(f"Starting Local Coder on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        app_dir=str(ROOT_DIR / "backend"),
    )
