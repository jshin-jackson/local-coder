import os
import logging
from pathlib import Path
from typing import Iterator, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_llm = None
_model_path: Optional[str] = None
_load_error: Optional[str] = None


def _resolve_model_path(path: str) -> str:
    """Resolve model path relative to the backend directory."""
    p = Path(path)
    if p.is_absolute():
        return str(p)
    # Resolve relative to backend directory
    base = Path(__file__).parent
    resolved = (base / p).resolve()
    return str(resolved)


def load_model() -> None:
    """Load the GGUF model using llama-cpp-python. Called once at startup."""
    global _llm, _model_path, _load_error

    raw_path = os.getenv("MODEL_PATH", "../models/model.gguf")
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
