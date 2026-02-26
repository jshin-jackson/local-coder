"""
AMP Step 0 — Install Dependencies

Installs all Python and Node.js dependencies required by Local Coder.
- llama-cpp-python compiled with CUDA GPU support (for Cloudera AI NVIDIA GPU instances)
- FastAPI, uvicorn, sse-starlette, and other Python backend dependencies
- Node.js packages for the React frontend
"""

import subprocess
import sys
import os

# CML Sessions do not define __file__; the working directory is always the project root.
ROOT_DIR = os.getcwd()


def run(cmd: list[str], cwd: str = ROOT_DIR) -> None:
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=True)
    return result


def main() -> None:
    print("=" * 60)
    print("Step 0: Installing dependencies")
    print("=" * 60)

    # --- Python: llama-cpp-python (CUDA if available, otherwise CPU) ---
    print("\n[1/3] Installing llama-cpp-python...")

    def _install_llama_cpp(cuda: bool) -> bool:
        env = os.environ.copy()
        if cuda:
            env["CMAKE_ARGS"] = "-DGGML_CUDA=on"
            label = "CUDA GPU"
        else:
            env.pop("CMAKE_ARGS", None)
            label = "CPU"
        print(f"    Attempting build with {label} support...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "llama-cpp-python", "--no-cache-dir"],
            cwd=ROOT_DIR,
            env=env,
        )
        return result.returncode == 0

    if not _install_llama_cpp(cuda=True):
        print("    CUDA build failed (CUDA Toolkit not found) — falling back to CPU build.")
        print("    NOTE: The Application step requires a GPU instance for acceptable performance.")
        if not _install_llama_cpp(cuda=False):
            raise RuntimeError("llama-cpp-python installation failed for both CUDA and CPU builds.")

    # --- Python: remaining backend dependencies ---
    print("\n[2/3] Installing Python backend dependencies...")
    run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])

    # --- Node.js: frontend dependencies ---
    print("\n[3/3] Installing Node.js frontend dependencies...")
    run(["npm", "install"], cwd=os.path.join(ROOT_DIR, "frontend"))

    print("\n✓ All dependencies installed successfully.")


if __name__ == "__main__":
    main()
