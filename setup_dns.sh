#!/bin/bash
# =============================================================================
# setup_dns.sh — Local DNS Server Installer using BIND9
# Domain: localnet  (hosts resolve as pc.localnet, nas.localnet, etc.)
# =============================================================================

# --- Root check ---
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root (use sudo)."
    exit 1
fi

# --- Detect network info ---
DOMAIN="localnet"
IP_ADDR=$(hostname -I | awk '{print $1}')

if [[ -z "$IP_ADDR" ]]; then
    echo "ERROR: Could not detect a local IP address. Is networking up?"
    exit 1
fi

SUBNET="${IP_ADDR%.*}.0/24"
ZONE_FILE="/etc/bind/db.$DOMAIN"

# Build reverse zone name (e.g. 192.168.1.x → 1.168.192.in-addr.arpa)
OCTET3="${IP_ADDR%.*}"
OCTET3="${OCTET3##*.}"
OCTET2="${IP_ADDR%.*.*}"
OCTET2="${OCTET2##*.}"
OCTET1="${IP_ADDR%%.*}"
REVERSE_ZONE="${OCTET3}.${OCTET2}.${OCTET1}.in-addr.arpa"
REVERSE_ZONE_FILE="/etc/bind/db.${OCTET1}.${OCTET2}.${OCTET3}"

# Last octet of this server's IP (used in PTR record)
SERVER_LAST_OCTET="${IP_ADDR##*.}"

# Serial: Unix timestamp — always unique, always incrementing,
# and always fits in the 32-bit DNS serial field (max 4294967295).
SERIAL=$(date +%s)

echo "============================================="
echo " BIND9 Local DNS Installer"
echo "---------------------------------------------"
echo " Domain  : $DOMAIN"
echo " Server  : $IP_ADDR (ns1.$DOMAIN)"
echo " Subnet  : $SUBNET"
echo " Reverse : $REVERSE_ZONE"
echo " Serial  : $SERIAL"
echo "============================================="
echo ""

# --- Install BIND9 ---
echo "[1/6] Installing BIND9..."
apt update -qq && apt install -y bind9 bind9utils dnsutils
if [[ $? -ne 0 ]]; then
    echo "ERROR: apt install failed. Check your internet connection."
    exit 1
fi

# --- Write named.conf.options ---
echo "[2/6] Writing options (ACL, forwarders, recursion)..."
cat > /etc/bind/named.conf.options <<EOF
acl "trusted_network" {
    127.0.0.1;
    ${SUBNET};
};

options {
    directory "/var/cache/bind";

    // Only answer queries from this machine and local subnet
    allow-query     { "trusted_network"; };
    allow-recursion { "trusted_network"; };
    allow-transfer  { none; };

    recursion yes;

    // Upstream DNS forwarders (Cloudflare for Families — blocks malware/phishing)
    forwarders {
        1.0.0.2;
        1.1.1.2;
    };
    forward only;

    dnssec-validation auto;

    // Only listen on IPv4 — change to 'any' if you use IPv6 on your LAN
    // Uncomment listen on for other devices to pick up
    // listen-on { 127.0.0.1; 192.168.1.YOURIP; };
    listen-on-v6 { none; };
};
EOF

# --- Write named.conf.local (forward + reverse zones) ---
echo "[3/6] Registering forward and reverse zones..."
cat > /etc/bind/named.conf.local <<EOF
// Forward zone: resolves names to IPs  (e.g. pc.localnet -> 192.168.x.x)
zone "${DOMAIN}" {
    type master;
    file "${ZONE_FILE}";
};

// Reverse zone: resolves IPs to names  (e.g. 192.168.x.x -> pc.localnet)
zone "${REVERSE_ZONE}" {
    type master;
    file "${REVERSE_ZONE_FILE}";
};
EOF

# --- Write forward zone file ---
echo "[4/6] Writing forward zone file..."
cat > "${ZONE_FILE}" <<EOF
\$TTL 86400
@   IN  SOA   ns1.${DOMAIN}. admin.${DOMAIN}. (
              ${SERIAL} ; Serial (Unix timestamp - always valid)
              3600      ; Refresh (1 hour)
              900       ; Retry   (15 min)
              604800    ; Expire  (1 week)
              86400 )   ; Minimum TTL (1 day)

; --- Name Servers ---
@       IN  NS    ns1.${DOMAIN}.

; --- DNS server itself ---
ns1     IN  A     ${IP_ADDR}

; ==========================================================
; ADD YOUR DEVICES BELOW
; Format:  hostname   IN  A   192.168.x.y
; Example entries (edit IPs to match your actual devices):
; ==========================================================
; pc        IN  A   ${IP_ADDR%.*}.10
; laptop    IN  A   ${IP_ADDR%.*}.11
; nas       IN  A   ${IP_ADDR%.*}.20
; printer   IN  A   ${IP_ADDR%.*}.30
; router    IN  A   ${IP_ADDR%.*}.1
; pi        IN  A   ${IP_ADDR%.*}.50
EOF

# --- Write reverse zone file ---
echo "[5/6] Writing reverse zone file..."
cat > "${REVERSE_ZONE_FILE}" <<EOF
\$TTL 86400
@   IN  SOA   ns1.${DOMAIN}. admin.${DOMAIN}. (
              ${SERIAL} ; Serial (Unix timestamp)
              3600      ; Refresh
              900       ; Retry
              604800    ; Expire
              86400 )   ; Minimum TTL

; --- Name Servers ---
@               IN  NS    ns1.${DOMAIN}.

; --- PTR Records (reverse lookup: last IP octet -> hostname) ---
; This server
${SERVER_LAST_OCTET}   IN  PTR   ns1.${DOMAIN}.

; ==========================================================
; ADD YOUR DEVICES BELOW
; Format:  last_octet   IN  PTR   hostname.localnet.
; Must match the forward zone entries above.
; ==========================================================
; 10    IN  PTR   pc.${DOMAIN}.
; 11    IN  PTR   laptop.${DOMAIN}.
; 20    IN  PTR   nas.${DOMAIN}.
; 30    IN  PTR   printer.${DOMAIN}.
; 1     IN  PTR   router.${DOMAIN}.
; 50    IN  PTR   pi.${DOMAIN}.
EOF

# --- Validate config before restarting ---
echo "[6/6] Validating configuration..."

named-checkconf
if [[ $? -ne 0 ]]; then
    echo "ERROR: named-checkconf found problems in your config. BIND9 not restarted."
    exit 1
fi

named-checkzone "${DOMAIN}" "${ZONE_FILE}"
if [[ $? -ne 0 ]]; then
    echo "ERROR: Forward zone file has errors. BIND9 not restarted."
    exit 1
fi

named-checkzone "${REVERSE_ZONE}" "${REVERSE_ZONE_FILE}"
if [[ $? -ne 0 ]]; then
    echo "ERROR: Reverse zone file has errors. BIND9 not restarted."
    exit 1
fi

# --- Restart and verify ---
systemctl restart bind9

sleep 1  # Give it a moment to come up

if systemctl is-active --quiet bind9; then
    echo ""
    echo "============================================="
    echo " SUCCESS - BIND9 is running!"
    echo "---------------------------------------------"
    echo " DNS Server IP : ${IP_ADDR}"
    echo " Domain        : ${DOMAIN}"
    echo " Trusted Subnet: ${SUBNET}"
    echo "---------------------------------------------"
    echo " NEXT STEPS:"
    echo "  1. Add device entries to: ${ZONE_FILE}"
    echo "     and matching PTR lines to: ${REVERSE_ZONE_FILE}"
    echo "  2. Update the serial (use: date +%s) each time you edit."
    echo "  3. Run: systemctl reload bind9  (after edits)"
    echo "  4. Point your router's DHCP DNS to: ${IP_ADDR}"
    echo "     (so all devices on the LAN use this server)"
    echo ""
    echo " Quick test commands:"
    echo "   nslookup ns1.${DOMAIN} ${IP_ADDR}"
    echo "   dig @${IP_ADDR} ns1.${DOMAIN}"
    echo "   dig @${IP_ADDR} -x ${IP_ADDR}"
    echo "============================================="
else
    echo ""
    echo "ERROR: BIND9 failed to start after restart."
    echo "Check logs with: journalctl -xe -u bind9"
    exit 1
fi