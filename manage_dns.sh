#!/bin/bash
# =============================================================================
# manage_dns.sh — Interactive BIND9 Record Manager
# =============================================================================

# Configuration - Must match your setup_dns.sh values
DOMAIN="localnet"
ZONE_FILE="/etc/bind/db.$DOMAIN"
# Dynamically find the reverse zone file in /etc/bind/
REVERSE_FILE=$(ls /etc/bind/db.*.*.* 2>/dev/null | head -n 1)

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root (use sudo)."
   exit 1
fi

# Function to update serial and reload BIND
apply_changes() {
    SERIAL=$(date +%s)
    sed -i "s/[0-9]\{10\} ; Serial/$SERIAL ; Serial/" "$ZONE_FILE"
    sed -i "s/[0-9]\{10\} ; Serial/$SERIAL ; Serial/" "$REVERSE_FILE"
    
    named-checkconf && systemctl reload bind9
    echo "--- Changes applied with Serial: $SERIAL ---"
}

show_menu() {
    echo "============================================="
    echo " BIND9 Record Manager: $DOMAIN"
    echo "============================================="
    echo "1) Add A Record (Forward + Reverse)"
    echo "2) Add CNAME (Alias)"
    echo "3) Remove Record"
    echo "4) Exit"
    echo "---------------------------------------------"
    read -p "Choose an option [1-4]: " CHOICE

    case $CHOICE in
        1)
            read -p "Enter Hostname (e.g., nas): " HOST
            read -p "Enter IP (e.g., 192.168.1.50): " IP
            LAST_OCTET="${IP##*.}"
            
            echo "$HOST    IN  A   $IP" >> "$ZONE_FILE"
            echo "$LAST_OCTET    IN  PTR $HOST.$DOMAIN." >> "$REVERSE_FILE"
            apply_changes
            ;;
        2)
            read -p "Enter Alias (e.g., movies): " ALIAS
            read -p "Target Hostname (e.g., ns1): " TARGET
            echo "$ALIAS    IN  CNAME $TARGET.$DOMAIN." >> "$ZONE_FILE"
            apply_changes
            ;;
        3)
            read -p "Enter Hostname to REMOVE: " REMOVE_HOST
            # Use sed to delete lines matching the host
            sed -i "/^$REMOVE_HOST/d" "$ZONE_FILE"
            sed -i "/PTR $REMOVE_HOST.$DOMAIN./d" "$REVERSE_FILE"
            apply_changes
            ;;
        4|*)
            echo "Exiting. No changes made."
            exit 0
            ;;
    esac
}

show_menu