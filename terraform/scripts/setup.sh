#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# setup.sh — Full UniMap production bootstrap for Ubuntu 22.04 (t3.micro)
# ──────────────────────────────────────────────────────────────────────────────
# Usage:  Passed as AWS EC2 user_data, or run manually:
#         sudo bash setup.sh 2>&1 | tee /var/log/user_data.log
#
# Idempotent — safe to re-run.  Every section checks before acting.
# Logs all output to /var/log/user_data.log
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

LOG_FILE="/var/log/user_data.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "============================================================"
echo "  UniMap setup.sh — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================================"

# ── Configuration ─────────────────────────────────────────────────────────────
APP_NAME="unimap"
APP_DIR="/opt/${APP_NAME}"
REPO_URL="https://github.com/brook1717/unimap-jju-campus.git"
REPO_BRANCH="main"

# Database
DB_NAME="unimap_db"
DB_USER="unimap_user"
DB_PASS="unimap_pass"

# Django
DJANGO_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS="api-unimap.birukkasahun.com,jigjigaunimap.birukkasahun.com,localhost,127.0.0.1"
CORS_ORIGINS="https://jigjigaunimap.birukkasahun.com,http://localhost:5173"
CSRF_ORIGINS="https://api-unimap.birukkasahun.com,https://jigjigaunimap.birukkasahun.com"

# Gunicorn
GUNICORN_WORKERS=2        # t3.micro: 2 vCPU, 1 GB RAM — keep it lean
GUNICORN_BIND="127.0.0.1:8000"
GUNICORN_USER="www-data"

# Domains (for Nginx)
API_DOMAIN="api-unimap.birukkasahun.com"
FRONTEND_DOMAIN="jigjigaunimap.birukkasahun.com"

# ══════════════════════════════════════════════════════════════════════════════
# 1. SWAP FILE (1 GB) — prevents OOM kills on t3.micro
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [1/8] Configuring swap..."

if ! swapon --show | grep -q '/swapfile'; then
    if [ ! -f /swapfile ]; then
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
    fi
    swapon /swapfile
    # Persist across reboots
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    # Tune swappiness for a server workload
    sysctl vm.swappiness=10
    grep -q 'vm.swappiness' /etc/sysctl.conf || echo 'vm.swappiness=10' >> /etc/sysctl.conf
    echo "    Swap enabled: $(swapon --show)"
else
    echo "    Swap already active — skipping."
fi

# ══════════════════════════════════════════════════════════════════════════════
# 2. SYSTEM PACKAGES
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [2/8] Installing system packages..."

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y

apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential libpq-dev \
    gdal-bin libgdal-dev libgeos-dev libproj-dev binutils \
    postgresql postgresql-contrib postgis postgresql-16-postgis-3 \
    nginx certbot python3-certbot-nginx \
    git curl ufw

echo "    Installed: python3 $(python3 --version 2>&1 | awk '{print $2}'), nginx $(nginx -v 2>&1 | awk -F/ '{print $2}'), psql $(psql --version | awk '{print $3}')"

# ══════════════════════════════════════════════════════════════════════════════
# 3. FIREWALL (UFW)
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [3/8] Configuring firewall..."

ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
echo "    UFW status: $(ufw status | head -3)"

# ══════════════════════════════════════════════════════════════════════════════
# 4. POSTGRESQL + POSTGIS DATABASE
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [4/8] Setting up PostgreSQL database..."

systemctl enable postgresql
systemctl start postgresql

# Create user (idempotent: IF NOT EXISTS not available for roles, use DO block)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"

# Create database (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 || \
    sudo -u postgres createdb -O "${DB_USER}" "${DB_NAME}"

# Enable PostGIS extension
sudo -u postgres psql -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Grant permissions
sudo -u postgres psql -c "ALTER USER ${DB_USER} CREATEDB;"

echo "    Database '${DB_NAME}' ready with PostGIS extension."

# ══════════════════════════════════════════════════════════════════════════════
# 5. APPLICATION — Clone, venv, install, configure
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [5/8] Deploying application..."

# Clone or pull
if [ -d "${APP_DIR}/.git" ]; then
    echo "    Repo exists — pulling latest..."
    cd "${APP_DIR}"
    git fetch origin
    git reset --hard "origin/${REPO_BRANCH}"
else
    echo "    Cloning repo..."
    git clone --branch "${REPO_BRANCH}" "${REPO_URL}" "${APP_DIR}"
    cd "${APP_DIR}"
fi

# Python virtual environment
if [ ! -d "${APP_DIR}/backend/venv" ]; then
    python3 -m venv "${APP_DIR}/backend/venv"
    echo "    Created venv at ${APP_DIR}/backend/venv"
fi

source "${APP_DIR}/backend/venv/bin/activate"
pip install --upgrade pip wheel setuptools
pip install -r "${APP_DIR}/backend/requirements.txt"
echo "    Installed $(pip list --format=columns | wc -l) Python packages."

# ── .env file (only create if missing — never overwrite existing secrets) ────
ENV_FILE="${APP_DIR}/.env"
if [ ! -f "${ENV_FILE}" ]; then
    cat > "${ENV_FILE}" <<ENVEOF
# ─── Django ──────────────────────────────────────────────────────────────
SECRET_KEY=${DJANGO_SECRET}
DEBUG=False
ALLOWED_HOSTS=${ALLOWED_HOSTS}

# ─── PostgreSQL / PostGIS ────────────────────────────────────────────────
POSTGRES_DB=${DB_NAME}
POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${DB_PASS}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ─── CORS ────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS=${CORS_ORIGINS}

# ─── CSRF ────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS=${CSRF_ORIGINS}

# ─── Gunicorn ────────────────────────────────────────────────────────────
GUNICORN_WORKERS=${GUNICORN_WORKERS}
GUNICORN_TIMEOUT=120

# ─── Topology Data ──────────────────────────────────────────────────────
TOPOLOGY_GEOJSON_PATH=${APP_DIR}/data/topology_paths.geojson
ENVEOF
    echo "    Created ${ENV_FILE}"
else
    echo "    ${ENV_FILE} already exists — skipping (delete manually to regenerate)."
fi

# ── Django management commands ───────────────────────────────────────────────
cd "${APP_DIR}/backend"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
echo "    Migrations applied, static files collected."

# Seed data if the locations table is empty
LOCATION_COUNT=$(python manage.py shell -c "from locations.models import CampusLocation; print(CampusLocation.objects.count())" 2>/dev/null || echo "0")
if [ "${LOCATION_COUNT}" = "0" ]; then
    python manage.py seed_campus || echo "    Warning: seed_campus failed (may need manual seeding)."
    echo "    Seeded campus data."
else
    echo "    ${LOCATION_COUNT} locations already in DB — skipping seed."
fi

deactivate

# Set ownership so www-data can read/serve
chown -R www-data:www-data "${APP_DIR}/backend/staticfiles" "${APP_DIR}/backend/media" 2>/dev/null || true

# ══════════════════════════════════════════════════════════════════════════════
# 6. BUILD FRONTEND (static files for Nginx)
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [6/8] Building frontend..."

if command -v node &>/dev/null; then
    echo "    Node $(node --version) already installed."
else
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    echo "    Installed Node $(node --version)."
fi

cd "${APP_DIR}/frontend"
npm ci --production=false
npm run build
echo "    Frontend built at ${APP_DIR}/frontend/dist"

# ══════════════════════════════════════════════════════════════════════════════
# 7. GUNICORN — systemd service
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [7/8] Configuring Gunicorn service..."

GUNICORN_SERVICE="/etc/systemd/system/${APP_NAME}-gunicorn.service"

cat > "${GUNICORN_SERVICE}" <<SERVICEEOF
[Unit]
Description=UniMap Gunicorn daemon
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=${GUNICORN_USER}
Group=${GUNICORN_USER}
WorkingDirectory=${APP_DIR}/backend
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/backend/venv/bin/gunicorn \\
    unimap_backend.wsgi:application \\
    --bind ${GUNICORN_BIND} \\
    --workers ${GUNICORN_WORKERS} \\
    --timeout 120 \\
    --access-logfile /var/log/${APP_NAME}-gunicorn-access.log \\
    --error-logfile  /var/log/${APP_NAME}-gunicorn-error.log
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5s
KillMode=mixed

# Hardening
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=${APP_DIR}/backend/media /var/log

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable "${APP_NAME}-gunicorn"
systemctl restart "${APP_NAME}-gunicorn"
echo "    Gunicorn service active: $(systemctl is-active ${APP_NAME}-gunicorn)"

# ══════════════════════════════════════════════════════════════════════════════
# 8. NGINX — reverse proxy (API + React SPA)
# ══════════════════════════════════════════════════════════════════════════════
echo ">>> [8/8] Configuring Nginx..."

NGINX_CONF="/etc/nginx/sites-available/${APP_NAME}"

cat > "${NGINX_CONF}" <<'NGINXEOF'
# ── UniMap — API backend ──────────────────────────────────────────────────────
server {
    listen 80;
    server_name API_DOMAIN_PLACEHOLDER;

    client_max_body_size 10M;

    # Django static files (collectstatic output)
    location /static/ {
        alias APP_DIR_PLACEHOLDER/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django media uploads
    location /media/ {
        alias APP_DIR_PLACEHOLDER/backend/media/;
        expires 7d;
    }

    # API + Admin → Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}

# ── UniMap — React frontend SPA ──────────────────────────────────────────────
server {
    listen 80;
    server_name FRONTEND_DOMAIN_PLACEHOLDER;

    root APP_DIR_PLACEHOLDER/frontend/dist;
    index index.html;

    # Cache hashed assets aggressively
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # PWA service worker — never cache
    location = /sw.js {
        expires off;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }

    # SPA fallback — serve index.html for all non-file routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINXEOF

# Replace placeholders with actual values
sed -i "s|API_DOMAIN_PLACEHOLDER|${API_DOMAIN}|g"       "${NGINX_CONF}"
sed -i "s|FRONTEND_DOMAIN_PLACEHOLDER|${FRONTEND_DOMAIN}|g" "${NGINX_CONF}"
sed -i "s|APP_DIR_PLACEHOLDER|${APP_DIR}|g"              "${NGINX_CONF}"

# Enable site, remove default
ln -sf "${NGINX_CONF}" /etc/nginx/sites-enabled/${APP_NAME}
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t
systemctl reload nginx
echo "    Nginx configured and reloaded."

# ══════════════════════════════════════════════════════════════════════════════
# DONE
# ══════════════════════════════════════════════════════════════════════════════

echo ""
echo "============================================================"
echo "  UniMap deployment complete — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================================"
echo ""
echo "  Services:"
echo "    Gunicorn : systemctl status ${APP_NAME}-gunicorn"
echo "    Nginx    : systemctl status nginx"
echo "    Postgres : systemctl status postgresql"
echo ""
echo "  Logs:"
echo "    Bootstrap : ${LOG_FILE}"
echo "    Gunicorn  : /var/log/${APP_NAME}-gunicorn-access.log"
echo "    Gunicorn  : /var/log/${APP_NAME}-gunicorn-error.log"
echo "    Nginx     : /var/log/nginx/access.log"
echo ""
echo "  Next steps:"
echo "    1. Point DNS A records to this server's Elastic IP:"
echo "       ${API_DOMAIN}      → <EIP>"
echo "       ${FRONTEND_DOMAIN} → <EIP>"
echo "    2. Obtain TLS certificates:"
echo "       sudo certbot --nginx -d ${API_DOMAIN} -d ${FRONTEND_DOMAIN}"
echo "    3. Verify:"
echo "       curl -s http://localhost:8000/api/locations/ | head -c 200"
echo "============================================================"
