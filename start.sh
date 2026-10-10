#!/bin/zsh
# ./start.sh        — реальные данные, доступ с телефона в той же Wi-Fi сети
# ./start.sh demo   — демо-режим
cd "$(dirname "$0")"
PORT=${PORT:-8000}
if [[ "$1" == "demo" ]]; then
  export IRONMAN_DEMO=1
  [[ -f data/demo.db ]] || .venv/bin/python -m app.sync demo
fi
IP=$(ipconfig getifaddr en0 2>/dev/null)
echo "Панель:   http://localhost:$PORT"
[[ -n "$IP" ]] && echo "Телефон:  http://$IP:$PORT"
exec .venv/bin/uvicorn app.server:app --host 0.0.0.0 --port $PORT
