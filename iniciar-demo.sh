#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"

if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi
. .venv/bin/activate
python -m pip install -q -r backend/requirements.txt

HOST=0.0.0.0 PORT=5000 ADMIN_EMAILS=helena@fitbattle.dev python backend/tests/servidor_dev.py &
API_PID=$!
python -m http.server 5500 --bind 0.0.0.0 --directory frontend &
FRONT_PID=$!
trap 'kill $API_PID $FRONT_PID 2>/dev/null' EXIT INT TERM

echo
echo "FitBattle demo no ar."
echo "  Tela de login (este computador): http://localhost:5500/login.html"
echo "  Tela de login (outro aparelho da rede): http://IP_DESTE_COMPUTADOR:5500/login.html"
echo "  API: http://localhost:5000/healthz"
echo "  Login de demonstracao: helena@fitbattle.dev / senhaforte123"
echo "  Para encerrar: Ctrl+C"
echo

wait
