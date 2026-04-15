#!/bin/bash
# nginx_install.sh — Lean Nginx Setup for Local Reverse Proxy
if [[ $EUID -ne 0 ]]; then echo "Use sudo"; exit 1; fi

echo "[1/3] Installing Nginx..."
apt update -qq && apt install -y nginx

echo "[2/3] Cleaning default bloat..."
# Stop the default 'Welcome to Nginx' page from hogging port 80
rm -f /etc/nginx/sites-enabled/default

echo "[3/3] Setting up directory permissions..."
chown -R www-data:www-data /var/www/html

systemctl restart nginx
echo "============================================="
echo " SUCCESS: Nginx is ready for your services."
echo "============================================="