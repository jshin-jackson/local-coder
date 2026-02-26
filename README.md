# Local Coder

A local web application for AI-powered source code generation, running entirely on your MacBook using the `midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF` model with Metal GPU acceleration.

## Architecture

```
Browser (React IDE)  ←→  FastAPI Backend  ←→  llama-cpp-python  ←→  GGUF Model (Metal GPU)
```

---

## Prerequisites

- macOS Ventura or later (Apple Silicon recommended for Metal GPU)
- Python 3.10+
- Node.js 18+
- Xcode Command Line Tools: `xcode-select --install`

---

## 1. Download the Model

Run from the **project root** (`local-coder/`):

```bash
pip install -U "huggingface-hub[cli]"

# huggingface-hub 1.4+ uses `hf` (replaces the old `huggingface-cli`)
hf download midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF \
  --include "*.gguf" \
  --local-dir ./models
```

> **File:** `gpt-oss-20b-Coding-Distill.MXFP4.gguf` (~13.8 GB)  
> **Format:** MXFP4 (Microsoft Microscaling 4-bit) — optimized quantization for this model  
> Download takes several minutes depending on network speed.

---

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (required before every session)
source .venv/bin/activate

# Install llama-cpp-python with Apple Metal (GPU) support
CMAKE_ARGS="-DGGML_METAL=on" pip install -U llama-cpp-python --no-cache-dir

# Install other dependencies
pip install -r requirements.txt

# Copy environment config (no edits needed — model path is pre-configured)
cp .env.example .env
```

The `.env` file is pre-configured with the correct model path:

```env
MODEL_PATH=../models/gpt-oss-20b-Coding-Distill.MXFP4.gguf
N_GPU_LAYERS=-1
N_CTX=4096
```

> Set `N_GPU_LAYERS=-1` to offload all layers to Metal GPU (recommended).  
> Set `N_GPU_LAYERS=0` to use CPU only.

---

## 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## 4. Running the Application

Open **two terminal windows**:

**Terminal 1 — Backend**
```bash
cd backend
source .venv/bin/activate     # ← must activate every new terminal session
uvicorn main:app --reload --port 8000
```

Expected output when ready:
```
INFO model: Loading model from .../gpt-oss-20b-Coding-Distill.MXFP4.gguf
INFO model: Model loaded successfully.       ← model takes ~30–60s to load
INFO: Application startup complete.
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

Open your browser at **http://localhost:5173**

---

## Usage

1. Select a programming language from the dropdown (or keep "Auto")
2. Type a code generation prompt in the text area
3. Press **Generate** or `⌘↵` to start
4. Watch code stream in real-time into the Monaco editor
5. Edit, copy, or save the generated code
6. Click past generations in the left sidebar to revisit them

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `../models/gpt-oss-20b-Coding-Distill.MXFP4.gguf` | Path to the GGUF model file |
| `N_GPU_LAYERS` | `-1` | Layers offloaded to GPU (-1 = all) |
| `N_CTX` | `4096` | Context window size in tokens (max 131072) |
| `N_THREADS` | `8` | CPU threads (for layers not on GPU) |
| `HOST` | `0.0.0.0` | Backend host |
| `PORT` | `8000` | Backend port |

---

## Troubleshooting

**`zsh: command not found: huggingface-cli`**
- `huggingface-hub` 1.4+ renamed the command to `hf`
- Run: `pip install -U "huggingface-hub[cli]"` then use `hf download ...`

**`ModuleNotFoundError: No module named 'sse_starlette'`**
- The virtual environment is not activated
- Run `source .venv/bin/activate` from the `backend/` directory before `uvicorn`
- The prompt should show `(.venv)` when activated correctly

**Model not loading / file not found**
- Verify the `MODEL_PATH` in `.env` matches the actual filename in `models/`
- Run `ls models/` to confirm: the file should be `gpt-oss-20b-Coding-Distill.MXFP4.gguf`
- The model download must be run from the project root (`local-coder/`), not from `backend/`

**`ggml_metal_init: skipping kernel_*_bf16 (not supported)` warnings**
- These are harmless warnings — Metal GPU does not support BF16 kernels natively
- Those operations fall back to CPU automatically; the model still runs

**`n_ctx_per_seq (4096) < n_ctx_train (131072)` warning**
- Harmless — the model supports up to 131k tokens but `N_CTX=4096` limits it to save RAM
- Increase `N_CTX` in `.env` if you need longer context (requires more memory)

**llama-cpp-python install fails**
- Ensure Xcode Command Line Tools are installed: `xcode-select --install`
- Try force reinstall: `CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --no-cache-dir --force-reinstall`

**Slow generation**
- Confirm `N_GPU_LAYERS=-1` is set in `.env` to use Metal GPU
- Check Activity Monitor → GPU History to verify GPU usage during generation

**CORS error in browser**
- Make sure the backend is running on port `8000`
- Vite proxies `/api` → `http://localhost:8000` automatically (configured in `vite.config.ts`)

---

## Deploying as a Cloudera AI AMP

This project is packaged as a **Cloudera Accelerator for Machine Learning Projects (AMP)**.  
On Cloudera AI, all setup steps run automatically — no manual commands needed.

### Automatic Setup Flow

```
[Session]  0_session-install-deps  →  pip install + npm install
[Job]      1_job-download-model    →  Download GGUF model from HuggingFace (~13.8 GB)
[Job]      2_job-build-frontend    →  npm run build (React → dist/)
[App]      3_app/start.py          →  FastAPI serves API + React UI (single CML Application)
```

### Adding to a Custom AMP Catalog

1. Go to **Site Administration → AMPs** in Cloudera AI
2. Click **Add Source**
3. Select **Git Repository URL** and enter:
   ```
   https://github.com/jshin-jackson/local-coder
   ```
4. Set the catalog file name to `catalog-entry.yaml`
5. Click **Add Source**

### Environment Variables (configurable at launch)

| Variable | Default | Description |
|---|---|---|
| `MODEL_REPO_ID` | `midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF` | HuggingFace repo ID |
| `MODEL_FILENAME` | `gpt-oss-20b-Coding-Distill.MXFP4.gguf` | GGUF filename |
| `N_GPU_LAYERS` | `-1` | GPU layers (-1 = all, 0 = CPU only) |
| `N_CTX` | `4096` | Context window size |
| `HF_TOKEN` | *(empty)* | HuggingFace token (for private/gated models) |

### Resource Requirements

| Resource | Recommended |
|---|---|
| CPU | 4 vCores |
| Memory | 32 GB |
| GPU | 1 × NVIDIA (A10G / V100 or better) |
