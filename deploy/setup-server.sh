#!/bin/bash
# Установка панели на чистый Ubuntu 24.04 (под root):
#   curl -fsSL https://raw.githubusercontent.com/rkuskildin/ironman-dashboard/main/deploy/setup-server.sh | bash -s -- [домен]
# Без домена адрес будет <ip-через-дефисы>.nip.io — HTTPS выпустится автоматически.
set -euo pipefail
REPO=${REPO:-https://github.com/rkuskildin/ironman-dashboard.git}
IP=$(curl -fsS https://api.ipify.org)
DOMAIN=${1:-${IP//./-}.nip.io}

apt-get update -q
apt-get install -y -q git python3-venv caddy ufw
id ironman &>/dev/null || useradd --system --home /opt/ironman --shell /usr/sbin/nologin ironman
mkdir -p /opt/ironman
[ -d /opt/ironman/app/.git ] || git clone -q "$REPO" /opt/ironman/app
python3 -m venv /opt/ironman/venv
/opt/ironman/venv/bin/pip install -q -r /opt/ironman/app/requirements.txt
mkdir -p /opt/ironman/app/data
if [ ! -f /opt/ironman/app/.env ]; then
  sed "s#^PUBLIC_URL=.*#PUBLIC_URL=https://$DOMAIN#; s#^GOOGLE_HEALTH_REDIRECT_URI=.*#GOOGLE_HEALTH_REDIRECT_URI=https://$DOMAIN/api/fitbit/callback#" \
    /opt/ironman/app/.env.example > /opt/ironman/app/.env
fi
chmod 600 /opt/ironman/app/.env
chown -R ironman:ironman /opt/ironman

cp /opt/ironman/app/deploy/ironman.service /etc/systemd/system/ironman.service
sed "s#^DOMAIN {#$DOMAIN {#" /opt/ironman/app/deploy/Caddyfile.example > /etc/caddy/Caddyfile
cat > /usr/local/bin/ironman-user <<'SH'
#!/bin/bash
# Пользователи панели: ironman-user add <логин> --role athlete|coach [--name "Имя"] | invite | list | remove <логин>
export LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONIOENCODING=utf-8
cd /opt/ironman/app && exec sudo -u ironman /opt/ironman/venv/bin/python -m app.auth "$@"
SH
chmod +x /usr/local/bin/ironman-user

ufw allow OpenSSH >/dev/null && ufw allow 80/tcp >/dev/null && ufw allow 443/tcp >/dev/null && ufw --force enable >/dev/null
systemctl daemon-reload
systemctl enable --now ironman
systemctl reload caddy

echo
echo "Готово: https://$DOMAIN"
echo "Дальше:"
echo "  1) nano /opt/ironman/app/.env          — цель, пороги, доступы; потом: systemctl restart ironman"
echo "  2) ironman-user add <логин> --role athlete   — ваш вход в панель"
echo "  3) Garmin: sudo -u ironman /opt/ironman/venv/bin/python -m app.sync garmin-login (из /opt/ironman/app)"
