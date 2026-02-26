"""
AMP Step 3 — Start Application

Launches the FastAPI server as a CML Application.
FastAPI serves both:
  - /api/*      → REST + SSE code generation API
  - /*          → React frontend static files (from frontend/dist/)

CML Application requires the server to listen on:
  - Host: 0.0.0.0
  - Port: CDSW_APP_PORT (environment variable set by CML)

Note: CML runs scripts inside a Jupyter/IPython context that already has
a running uvloop event loop. uvicorn.run() and nest_asyncio both fail in
this environment. The only reliable solution is to launch uvicorn as a
completely separate subprocess via os.execv(), which replaces the current
process entirely and starts a fresh event loop.
"""

import os
import sys
from pathlib import Path

# CML Jobs/Sessions do not define __file__; working directory is the project root.
ROOT_DIR = Path(os.getcwd())

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("CDSW_APP_PORT", os.getenv("PORT", "8000"))

print(f"Starting Local Coder on {HOST}:{PORT}")
print(f"Backend dir: {ROOT_DIR / 'backend'}")

# Replace the current process entirely with uvicorn.
# os.execv() avoids all event loop conflicts because there is no parent loop.
os.chdir(str(ROOT_DIR / "backend"))
os.execv(
    sys.executable,
    [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", HOST,
        "--port", str(PORT),
        "--no-access-log",
    ],
)
