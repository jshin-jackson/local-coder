import os
import logging
from pathlib import Path
from typing import Iterator, Optional
from dotenv import load_dotenv

# Explicitly load .env from backend/ regardless of cwd
try:
    _env_file = Path(__file__).parent / ".env"
except NameError:
    _env_file = Path.cwd() / "backend" / ".env"
load_dotenv(dotenv_path=_env_file, override=False)

logger = logging.getLogger(__name__)

_llm = None
_model_path: Optional[str] = None
_load_error: Optional[str] = None


def _resolve_model_path(path: str) -> str:
    """Resolve model path — supports absolute paths and paths relative to project root."""
    p = Path(path)
    if p.is_absolute():
        return str(p)

    # In CML, __file__ is not defined; use cwd (always project root) as base.
    try:
        base = Path(__file__).parent          # local: backend/
        resolved = (base / p).resolve()
    except NameError:
        base = Path.cwd()                     # CML: project root
        # Strip leading "../" since cwd is already the project root
        clean = path.lstrip("./").lstrip("../")
        resolved = (base / clean).resolve()

    return str(resolved)


def load_model() -> None:
    """Load the GGUF model using llama-cpp-python. Called once at startup."""
    global _llm, _model_path, _load_error

    model_filename = os.getenv("MODEL_FILENAME", "gpt-oss-20b-Coding-Distill.MXFP4.gguf")
    raw_path = os.getenv("MODEL_PATH", f"../models/{model_filename}")
    _model_path = _resolve_model_path(raw_path)

    if not Path(_model_path).exists():
        _load_error = f"Model file not found: {_model_path}"
        logger.error(_load_error)
        return

    try:
        from llama_cpp import Llama

        n_gpu_layers = int(os.getenv("N_GPU_LAYERS", "-1"))
        n_ctx = int(os.getenv("N_CTX", "4096"))
        n_threads = int(os.getenv("N_THREADS", "8"))

        logger.info(f"Loading model from {_model_path} (n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx})")
        _llm = Llama(
            model_path=_model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False,
        )
        logger.info("Model loaded successfully.")
        _load_error = None
    except ImportError:
        _load_error = (
            "llama-cpp-python is not installed. "
            "Run: CMAKE_ARGS=\"-DGGML_METAL=on\" pip install -U llama-cpp-python --no-cache-dir"
        )
        logger.error(_load_error)
    except Exception as e:
        _load_error = f"Failed to load model: {e}"
        logger.error(_load_error)


def is_loaded() -> bool:
    return _llm is not None


def get_status() -> dict:
    return {
        "loaded": is_loaded(),
        "model_path": _model_path,
        "error": _load_error,
    }


def generate_stream(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.2,
    top_p: float = 0.95,
    stop: Optional[list[str]] = None,
) -> Iterator[str]:
    """Yield generated text tokens one at a time."""
    if not is_loaded():
        raise RuntimeError(_load_error or "Model is not loaded.")

    stop_sequences = stop or ["<|endoftext|>", "</s>"]

    stream = _llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop_sequences,
        stream=True,
    )

    for chunk in stream:
        token = chunk["choices"][0]["text"]
        if token:
            yield token
