#!/usr/bin/env bash
# setup-client-linux.sh - prepara entorno cliente en Linux (venv + deps)
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

echo "Client environment ready. To run the app:"
echo "source .venv/bin/activate"
echo "export DB_HOST=10.0.2.15  # set your server IP"
echo "export PRINT_SERVER_URL=http://10.0.2.15:5000"
echo "python3 main.py"
