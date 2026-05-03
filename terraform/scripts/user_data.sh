#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# user_data.sh — Bootstrap script for the UniMap backend EC2 instance
# ──────────────────────────────────────────────────────────────────────────────
# This script runs ONCE on first boot as root.
# Logs: /var/log/cloud-init-output.log
#
# TODO: Uncomment and customise the sections below for your deployment.
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

echo ">>> UniMap user_data.sh — starting bootstrap $(date)"

# ── 1. System updates ────────────────────────────────────────────────────────
apt-get update -y
apt-get upgrade -y

# ── 2. Install Docker & Docker Compose ────────────────────────────────────────
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow the ubuntu user to run docker without sudo
usermod -aG docker ubuntu

# ── 3. Install Nginx (reverse proxy + TLS termination) ───────────────────────
apt-get install -y nginx
systemctl enable nginx

# ── 4. Install Certbot for Let's Encrypt TLS ─────────────────────────────────
apt-get install -y certbot python3-certbot-nginx

# ── 5. Clone repo & start services ───────────────────────────────────────────
# TODO: Replace with your actual deployment steps
#
# cd /opt
# git clone https://github.com/brook1717/unimap-jju-campus.git unimap
# cd unimap
# cp .env.example .env
# # Edit .env with production values (SECRET_KEY, DB creds, ALLOWED_HOSTS, etc.)
# docker compose -f docker-compose.yml up -d
#
# ── 6. Configure Nginx reverse proxy ─────────────────────────────────────────
# TODO: Create /etc/nginx/sites-available/unimap with:
#
# server {
#     listen 80;
#     server_name api-unimap.birukkasahun.com;
#
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }
# }
#
# ln -s /etc/nginx/sites-available/unimap /etc/nginx/sites-enabled/
# nginx -t && systemctl reload nginx
#
# ── 7. Obtain TLS certificate ────────────────────────────────────────────────
# TODO: After DNS points to this server's Elastic IP:
# certbot --nginx -d api-unimap.birukkasahun.com --non-interactive --agree-tos -m your@email.com

echo ">>> UniMap user_data.sh — bootstrap complete $(date)"
