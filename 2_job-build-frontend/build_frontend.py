"""
AMP Step 2 — Build React Frontend

Runs `npm run build` in the frontend/ directory to compile the
React + TypeScript + Vite application into static files under
frontend/dist/, which FastAPI will serve as the UI.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"


def main() -> None:
    print("=" * 60)
    print("Step 2: Building React frontend")
    print("=" * 60)
    print(f"  Source  : {FRONTEND_DIR}")
    print(f"  Output  : {DIST_DIR}")

    if not FRONTEND_DIR.exists():
        print(f"ERROR: frontend/ directory not found at {FRONTEND_DIR}", file=sys.stderr)
        sys.exit(1)

    # Ensure node_modules exist
    if not (FRONTEND_DIR / "node_modules").exists():
        print("\n[1/2] Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)
    else:
        print("\n[1/2] Node.js dependencies already installed — skipping npm install.")

    # Build
    print("\n[2/2] Running npm run build...")
    subprocess.run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), check=True)

    if not DIST_DIR.exists():
        print("ERROR: Build failed — dist/ directory not created.", file=sys.stderr)
        sys.exit(1)

    built_files = list(DIST_DIR.rglob("*"))
    print(f"\n✓ Frontend built successfully ({len(built_files)} files in dist/).")


if __name__ == "__main__":
    main()
