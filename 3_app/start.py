"""
AMP Step 3 — Start Application

Launches the FastAPI server as a CML Application.
FastAPI serves both:
  - /api/*      → REST + SSE code generation API
  - /*          → React frontend static files (from frontend/dist/)

CML Application requires the server to listen on:
  - Host: 0.0.0.0
  - Port: CDSW_APP_PORT (environment variable set by CML)

Note: CML runs scripts in a Jupyter/IPython context with an existing asyncio
event loop. nest_asyncio patches the loop to allow uvicorn to run inside it.
"""

import os
import sys
from pathlib import Path

# CML Jobs/Sessions do not define __file__; working directory is the project root.
ROOT_DIR = Path(os.getcwd())
sys.path.insert(0, str(ROOT_DIR / "backend"))

import nest_asyncio
nest_asyncio.apply()

import uvicorn

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("CDSW_APP_PORT", os.getenv("PORT", "8000")))

print(f"Starting Local Coder on {HOST}:{PORT}")
uvicorn.run(
    "main:app",
    host=HOST,
    port=PORT,
    reload=False,
    app_dir=str(ROOT_DIR / "backend"),
)
