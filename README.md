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

```bash
pip install huggingface-hub

# Download the Q4_K_M quantized variant (~12 GB, best quality/speed balance)
huggingface-cli download midorin-Linux/gpt-oss-20b-Coding-Distill-GGUF \
  --include "*Q4_K_M*" \
  --local-dir ./models
```

> If you have less RAM (16 GB), use `Q4_0` (~11 GB). For 32 GB+ machines, try `Q6_K` for better quality.

---

## 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install llama-cpp-python with Apple Metal (GPU) support
CMAKE_ARGS="-DGGML_METAL=on" pip install -U llama-cpp-python --no-cache-dir

# Install other dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env` and set `MODEL_PATH` to the path of your downloaded `.gguf` file:

```env
MODEL_PATH=../models/gpt-oss-20b-Coding-Distill-Q4_K_M.gguf
N_GPU_LAYERS=-1
N_CTX=4096
```

> Set `N_GPU_LAYERS=-1` to offload all layers to the Metal GPU.
> Set `N_GPU_LAYERS=0` to use CPU only.

---

## 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## 4. Running the Application

Open two terminal windows:

**Terminal 1 — Backend**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
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
| `MODEL_PATH` | `../models/model.gguf` | Path to the GGUF model file |
| `N_GPU_LAYERS` | `-1` | Layers offloaded to GPU (-1 = all) |
| `N_CTX` | `4096` | Context window size in tokens |
| `N_THREADS` | `8` | CPU threads (for layers not on GPU) |
| `HOST` | `0.0.0.0` | Backend host |
| `PORT` | `8000` | Backend port |

---

## Troubleshooting

**Model not loading**
- Verify the `MODEL_PATH` in `.env` points to an existing `.gguf` file
- Run `ls models/` to confirm the file was downloaded

**llama-cpp-python install fails**
- Ensure Xcode Command Line Tools are installed: `xcode-select --install`
- Try: `CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --no-cache-dir --force-reinstall`

**Slow generation**
- Confirm `N_GPU_LAYERS=-1` is set in `.env` to use Metal GPU
- Check Activity Monitor → GPU History to verify GPU usage

**CORS error in browser**
- Make sure the backend is running on port `8000` (Vite proxies `/api` to it automatically)
