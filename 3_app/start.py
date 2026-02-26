"""
AMP Step 3 — Start Application

Launches the FastAPI server as a CML Application.
FastAPI serves both:
  - /api/*      → REST + SSE code generation API
  - /*          → React frontend static files (from frontend/dist/)

CML Application requires the server to listen on:
  - Host: 0.0.0.0
  - Port: CDSW_APP_PORT (environment variable set by CML)

Event loop strategy:
  CML executes scripts inside a Jupyter/IPython context that already runs
  a uvloop event loop. Three approaches fail in this environment:
    1. uvicorn.run()      → "Runner.run() cannot be called from running loop"
    2. nest_asyncio       → uvloop does not support nest_asyncio
    3. os.execv()         → CML port detection fails ("Duplicate port 0")

  Solution: run uvicorn.Server.serve() in a *new thread* with a *new asyncio
  event loop* (not uvloop). The new thread has no pre-existing loop, so
  uvicorn starts cleanly and CML detects the port binding correctly.
"""

import asyncio
import os
import sys
import threading
from pathlib import Path

# CML does not define __file__; working directory is always the project root.
ROOT_DIR = Path(os.getcwd())
sys.path.insert(0, str(ROOT_DIR / "backend"))

import uvicorn
from main import app  # import directly — avoids app_dir parameter

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("CDSW_APP_PORT", os.getenv("PORT", "8000")))

print(f"Starting Local Coder on {HOST}:{PORT}")
print(f"Backend dir: {ROOT_DIR / 'backend'}")


def _run_server() -> None:
    """Run uvicorn in a dedicated thread with a fresh asyncio event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = uvicorn.Config(
        app,                     # pass app object directly, not as string
        host=HOST,
        port=PORT,
        loop="asyncio",          # use standard asyncio, not uvloop
        reload=False,
        log_level="info",
    )
    server = uvicorn.Server(config)

    try:
        loop.run_until_complete(server.serve())
    finally:
        loop.close()


thread = threading.Thread(target=_run_server, daemon=False)
thread.start()
thread.join()
