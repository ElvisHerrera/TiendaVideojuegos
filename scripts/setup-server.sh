#!/usr/bin/env bash
# setup-server.sh - prepara un entorno virtual, instala dependencias y arranca print_server.py
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

if [ -d .venv ]; then
  echo ".venv exists, reusing"
else
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p logs
nohup python3 print_server.py > logs/print_server.log 2>&1 &
PID=$!

echo "Print server started (PID=$PID). Logs: $REPO_DIR/logs/print_server.log"
