#!/usr/bin/env bash
# FlowForge AI - Linux/Mac Launcher (cross-platform equivalent of start.bat)
set -e
cd "$(dirname "$0")"
echo "=========================================="
echo "  FlowForge AI - Linux/Mac Launcher v1.11"
echo "  Team: Shadu Team | XiHack 2026"
echo "=========================================="
BACKEND_DIR="$(pwd)/backend"
if [ ! -d "$BACKEND_DIR" ]; then
  echo "[ERROR] backend directory not found at $BACKEND_DIR"
  exit 1
fi
cd "$BACKEND_DIR"
PYTHON_CMD=""
if command -v python3 &>/dev/null; then PYTHON_CMD="python3"
elif command -v python &>/dev/null; then PYTHON_CMD="python"
else
  echo "[ERROR] Python not found. Install Python 3.11+."
  exit 1
fi
if [ ! -d "venv" ]; then
  echo "[1/4] Creating virtual environment..."
  "$PYTHON_CMD" -m venv venv
fi
VENV_PY="$BACKEND_DIR/venv/bin/python"
echo "[2/4] Installing dependencies..."
"$VENV_PY" -m pip install -r requirements.txt -q 2>/dev/null || true
if [ ! -f ".env" ]; then
  cp ../.env.example .env 2>/dev/null || echo "NVIDIA_BUILD_API_KEY=your_key" > .env
fi
echo "[3/4] Pre-flight app import check..."
"$VENV_PY" -c "from app.main import app; print('OK')"
echo "[4/4] Starting server on port 8080..."
echo "  Web UI  : http://localhost:8080"
echo "  API Docs: http://localhost:8080/api/v1/docs"
echo "  Health  : http://localhost:8080/health"
exec "$VENV_PY" -m uvicorn app.main:app --host 0.0.0.0 --port 8080
