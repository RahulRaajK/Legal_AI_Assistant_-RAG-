"""
Simple cross-platform launcher to run the full app with one command.

Usage:
    python run_local.py

This will:
  - Ensure a virtualenv exists and install backend requirements
  - Ensure frontend dependencies are installed
  - Start the FastAPI backend (uvicorn) on port 8000
  - Start the Next.js frontend dev server on port 3000

Requirements (must be installed on the machine):
  - Python 3.10+ (to match project dependencies)
  - Node.js + npm
  - Ollama running locally with the configured model pulled (e.g. `mistral`)
"""

import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_REQ = ROOT / "requirements.txt"
VENV_DIR = ROOT / "venv"
FRONTEND_DIR = ROOT / "frontend"


def run(cmd, cwd=None, env=None):
    """Run a command, streaming output, and raise on failure."""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if result.returncode != 0:
        raise SystemExit(f"Command failed with exit code {result.returncode}: {cmd}")


def ensure_venv():
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    if os.name == "nt":
        python_bin = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_bin = VENV_DIR / "bin" / "python"

    return str(python_bin)


def install_backend_deps(python_bin: str):
    if not BACKEND_REQ.exists():
        print("requirements.txt not found, skipping backend dependency install.")
        return
    print("Installing backend dependencies (pip)...")
    run(f'"{python_bin}" -m pip install --upgrade pip', cwd=str(ROOT))
    run(f'"{python_bin}" -m pip install -r requirements.txt', cwd=str(ROOT))


def install_frontend_deps():
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists():
        return
    print("Installing frontend dependencies (npm)...")
    run("npm install", cwd=str(FRONTEND_DIR))


def main():
    # 1) Backend env + deps
    python_bin = ensure_venv()
    install_backend_deps(python_bin)

    # 2) Frontend deps
    install_frontend_deps()

    # 3) Start backend and frontend
    env_backend = os.environ.copy()
    env_backend["PYTHONPATH"] = str(ROOT)

    backend_cmd = f'"{python_bin}" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload'

    print("\nStarting backend and frontend. Press Ctrl+C to stop both.")

    # Start backend
    backend_proc = subprocess.Popen(
        backend_cmd,
        shell=True,
        cwd=str(ROOT),
        env=env_backend,
    )

    # Start frontend
    env_frontend = os.environ.copy()
    env_frontend.setdefault("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    frontend_proc = subprocess.Popen(
        "npm run dev",
        shell=True,
        cwd=str(FRONTEND_DIR),
        env=env_frontend,
    )

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        for proc in (backend_proc, frontend_proc):
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()

