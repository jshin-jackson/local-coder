import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

import model as model_module

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Resolve frontend dist directory (works for both local dev and CML deployment)
_BACKEND_DIR = Path(__file__).parent
_FRONTEND_DIST = (_BACKEND_DIR / ".." / "frontend" / "dist").resolve()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up — loading model...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, model_module.load_model)
    yield
    logger.info("Shutting down.")


app = FastAPI(title="Local Coder API", version="1.0.0", lifespan=lifespan)

# ---------------------------------------------------------------------------
# CORS — allow localhost (local dev) + any CML Application origin
# ---------------------------------------------------------------------------
_EXTRA_ORIGIN = os.getenv("CML_APP_ORIGIN", "")
_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]
if _EXTRA_ORIGIN:
    _CORS_ORIGINS.append(_EXTRA_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.cloudera\.com",  # CML Application URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

LANGUAGE_PROMPTS: dict[str, str] = {
    "python": "Write the following in Python",
    "javascript": "Write the following in JavaScript",
    "typescript": "Write the following in TypeScript",
    "java": "Write the following in Java",
    "go": "Write the following in Go",
    "rust": "Write the following in Rust",
    "cpp": "Write the following in C++",
    "c": "Write the following in C",
    "shell": "Write the following as a shell script",
    "sql": "Write the following in SQL",
    "html": "Write the following in HTML",
    "css": "Write the following in CSS",
    "auto": "Write the following code",
}


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="Code generation prompt")
    language: str = Field(default="auto", description="Target programming language")
    max_tokens: int = Field(default=1024, ge=64, le=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(default=0.95, ge=0.0, le=1.0, description="Top-p sampling")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/model/status")
async def model_status() -> dict:
    return model_module.get_status()


@app.post("/api/generate")
async def generate(request: GenerateRequest) -> EventSourceResponse:
    if not model_module.is_loaded():
        status = model_module.get_status()
        raise HTTPException(
            status_code=503,
            detail=status.get("error") or "Model is not loaded.",
        )

    lang_prefix = LANGUAGE_PROMPTS.get(request.language, LANGUAGE_PROMPTS["auto"])
    full_prompt = (
        f"### Instruction:\n{lang_prefix}.\n\n{request.prompt}\n\n### Response:\n"
    )

    async def event_generator() -> AsyncIterator[dict]:
        try:
            loop = asyncio.get_event_loop()

            # Run blocking generator in thread pool, forwarding tokens via a queue
            queue: asyncio.Queue[Optional[str]] = asyncio.Queue()

            def _run() -> None:
                try:
                    for token in model_module.generate_stream(
                        prompt=full_prompt,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                        top_p=request.top_p,
                    ):
                        loop.call_soon_threadsafe(queue.put_nowait, token)
                except Exception as exc:
                    loop.call_soon_threadsafe(queue.put_nowait, f"\n\n[ERROR] {exc}")
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

            loop.run_in_executor(None, _run)

            while True:
                token = await queue.get()
                if token is None:
                    yield {"event": "done", "data": json.dumps({"done": True})}
                    break
                yield {"event": "token", "data": json.dumps({"token": token})}

        except asyncio.CancelledError:
            logger.info("Client disconnected during generation.")

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Static file serving for React frontend (CML Application / production mode)
# In local dev, Vite's dev server handles this instead.
# ---------------------------------------------------------------------------

if _FRONTEND_DIST.exists():
    # Serve /assets/* (JS, CSS, images built by Vite)
    app.mount(
        "/assets",
        StaticFiles(directory=str(_FRONTEND_DIST / "assets")),
        name="static-assets",
    )

    @app.get("/vite.svg")
    async def vite_svg() -> FileResponse:
        return FileResponse(str(_FRONTEND_DIST / "vite.svg"))

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str) -> FileResponse:
        """Catch-all route: serve React's index.html for client-side routing."""
        index = _FRONTEND_DIST / "index.html"
        return FileResponse(str(index))
else:
    logger.warning(
        "frontend/dist/ not found — React UI will not be served. "
        "Run: cd frontend && npm run build"
    )
