#!/bin/zsh
# Выложить код на сервер: данные (data/) и настройки (.env) сервера не трогаются.
#   DEPLOY_HOST — SSH-хост из ~/.ssh/config (по умолчанию «ironman»)
#   PUBLIC_URL  — адрес панели для проверки (берётся из .env, если не задан)
set -e
cd "$(dirname "$0")"
HOST=${DEPLOY_HOST:-ironman}
[[ -z "$PUBLIC_URL" && -f .env ]] && PUBLIC_URL=$(grep -E '^PUBLIC_URL=' .env | cut -d= -f2-)
rsync -az --delete --exclude '.venv' --exclude '__pycache__' --exclude 'data/' --exclude '.env' \
  --exclude '.git' --exclude '.DS_Store' --exclude 'deploy.sh' ./ "$HOST":/opt/ironman/app/
ssh "$HOST" 'chown -R ironman:ironman /opt/ironman/app && systemctl restart ironman && sleep 3 && systemctl is-active ironman'
[[ -n "$PUBLIC_URL" ]] && curl -s -o /dev/null -w "$PUBLIC_URL → %{http_code}\n" "$PUBLIC_URL/login"
