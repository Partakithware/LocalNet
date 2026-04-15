#!/bin/bash
# manage_nginx.sh — Interactive Proxy Manager
if [[ $EUID -ne 0 ]]; then echo "Use sudo"; exit 1; fi

show_menu() {
    echo "--- Nginx Proxy Manager ---"
    echo "1) Add Proxy (e.g., mediajungle.localnet -> :8086)"
    echo "2) Remove Proxy"
    echo "3) Exit"
    read -p "Choice: " CHOICE

    case $CHOICE in
        1)
            read -p "Enter Domain Name (e.g. mediajungle.localnet): " DOMAIN
            read -p "Enter Port (e.g. 8086): " PORT
            
            # Create the Nginx config file
            cat > /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
            ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
            nginx -t && systemctl reload nginx
            echo "Done! $DOMAIN now routes to port $PORT."
            ;;
        2)
            read -p "Domain to remove: " REMOVE_DOM
            rm -f /etc/nginx/sites-enabled/$REMOVE_DOM
            rm -f /etc/nginx/sites-available/$REMOVE_DOM
            systemctl reload nginx
            echo "Removed $REMOVE_DOM."
            ;;
        3|*) exit 0 ;;
    esac
}
show_menu