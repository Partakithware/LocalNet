#!/bin/bash
# uninstall_nginx.sh — Complete Nginx Removal
if [[ $EUID -ne 0 ]]; then echo "Use sudo"; exit 1; fi

read -p "Completely remove Nginx and all configs? [y/N]: " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then exit 0; fi

systemctl stop nginx
apt purge -y nginx nginx-common nginx-full
apt autoremove -y
rm -rf /etc/nginx
rm -rf /var/log/nginx

echo "Nginx has been purged."