"""
AMP Step 1 — Download GGUF Model

Downloads the gpt-oss-20b-Coding-Distill GGUF model from HuggingFace
into the project's models/ directory.

Environment variables (set via .project-metadata.yaml or CML UI):
  MODEL_REPO_ID   — HuggingFace repo ID (default: midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF)
  MODEL_FILENAME  — GGUF filename to download (default: gpt-oss-20b-Coding-Distill.MXFP4.gguf)
  HF_TOKEN        — Optional HuggingFace token for private/gated models
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
MODELS_DIR = ROOT_DIR / "models"

MODEL_REPO_ID = os.getenv("MODEL_REPO_ID", "midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF")
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "gpt-oss-20b-Coding-Distill.MXFP4.gguf")
HF_TOKEN = os.getenv("HF_TOKEN", None) or None


def main() -> None:
    print("=" * 60)
    print("Step 1: Downloading GGUF model from HuggingFace")
    print("=" * 60)
    print(f"  Repo    : {MODEL_REPO_ID}")
    print(f"  File    : {MODEL_FILENAME}")
    print(f"  Dest    : {MODELS_DIR}")

    target = MODELS_DIR / MODEL_FILENAME
    if target.exists():
        size_gb = target.stat().st_size / (1024 ** 3)
        print(f"\n✓ Model already exists ({size_gb:.1f} GB) — skipping download.")
        return

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Installing huggingface-hub...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "huggingface-hub[cli]"],
                       check=True)
        from huggingface_hub import hf_hub_download

    print(f"\nDownloading {MODEL_FILENAME} (~13.8 GB) — this may take several minutes...")

    downloaded_path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=str(MODELS_DIR),
        token=HF_TOKEN,
    )

    size_gb = Path(downloaded_path).stat().st_size / (1024 ** 3)
    print(f"\n✓ Model downloaded successfully: {downloaded_path} ({size_gb:.1f} GB)")

    # Write MODEL_PATH to a local .env for the application to read
    env_path = ROOT_DIR / "backend" / ".env"
    env_lines = []
    if env_path.exists():
        env_lines = env_path.read_text().splitlines()

    # Update or append MODEL_PATH
    model_path_value = f"../models/{MODEL_FILENAME}"
    new_lines = [l for l in env_lines if not l.startswith("MODEL_PATH=")]
    new_lines.append(f"MODEL_PATH={model_path_value}")

    env_path.write_text("\n".join(new_lines) + "\n")
    print(f"✓ Updated backend/.env with MODEL_PATH={model_path_value}")


if __name__ == "__main__":
    main()
