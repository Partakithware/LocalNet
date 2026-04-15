#!/bin/bash
# =============================================================================
# remove_dns.sh — Local DNS Server Uninstaller (BIND9 deep clean)
# =============================================================================

# --- Root check ---
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root (use sudo)."
    exit 1
fi

echo "============================================="
echo " BIND9 Local DNS Uninstaller"
echo " This will completely remove BIND9 and all"
echo " configuration files from this machine."
echo "============================================="
echo ""
read -p "Are you sure you want to continue? [y/N]: " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Aborted. Nothing was changed."
    exit 0
fi

echo ""

# --- Stop and disable the service ---
echo "[1/5] Stopping BIND9 service..."
if systemctl is-active --quiet bind9; then
    systemctl stop bind9
    echo "      Service stopped."
else
    echo "      Service was not running."
fi

systemctl disable bind9 2>/dev/null
echo "      Service disabled from autostart."

# --- Remove packages (purge leaves no config behind) ---
echo "[2/5] Purging BIND9 packages..."
apt purge -y bind9 bind9utils bind9-doc dnsutils 2>/dev/null
apt autoremove -y 2>/dev/null

# --- Remove config and data directories ---
echo "[3/5] Removing config and cache directories..."
rm -rf /etc/bind
rm -rf /var/cache/bind
rm -rf /var/lib/bind
echo "      Directories removed."

# --- Check port 53 is now free ---
echo "[4/5] Checking port 53 is free..."
if ss -tulpn 2>/dev/null | grep -q ':53'; then
    echo "      NOTE: Something is still listening on port 53:"
    ss -tulpn | grep ':53'
    echo "      This is likely systemd-resolved — that is normal on Ubuntu."
    echo "      It is NOT BIND9."
else
    echo "      Port 53 is clear. BIND9 is fully removed."
fi

# --- DNS resolver reminder ---
echo "[5/5] Checking your DNS resolver setting..."
CURRENT_NS=$(grep -m1 '^nameserver' /etc/resolv.conf 2>/dev/null | awk '{print $2}')
if [[ "$CURRENT_NS" == "127.0.0.1" ]]; then
    echo ""
    echo "  *** ACTION REQUIRED ***"
    echo "  Your /etc/resolv.conf is still pointing to 127.0.0.1"
    echo "  BIND9 is gone, so you will lose internet access!"
    echo ""
    echo "  Fix it now by running:"
    echo "    echo 'nameserver 1.1.1.2' > /etc/resolv.conf"
    echo ""
    echo "  Or if you use Netplan/systemd-resolved, restore your"
    echo "  network config and run: sudo netplan apply"
else
    echo "      Current DNS resolver: ${CURRENT_NS:-unknown}"
    echo "      Looks fine - no action needed."
fi

# --- Final verification ---
echo ""
echo "============================================="
echo " UNINSTALL COMPLETE"
echo "---------------------------------------------"
echo " Verify with these commands:"
echo "   which named          (should return nothing)"
echo "   ss -tulpn | grep :53 (should show no named)"
echo "   ls /etc/bind         (should say No such file)"
echo "============================================="