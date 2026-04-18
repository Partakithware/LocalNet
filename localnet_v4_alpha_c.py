#!/usr/bin/env python3
"""
LocalNet Manager v4 — Web Interface
Run with: sudo python3 localnet_v4.py
Then open: http://localhost:8091

v4 adds: Auth, SQLite, Backups, TXT/SRV/Wildcard DNS, DHCP,
         Ad Blocking, System Logs, Certbot/Let's Encrypt

alpha_c adds: Device Manager (DNS tab) — auto-discovery via BIND9 query logs,
              per-device DNS controls (block/unblock, hostname registration,
              ping, rename, notes, remove), managed ACL-based DNS blocking.
"""

import os, sys, json, glob, socket, subprocess, threading, re, time, base64
import hashlib, secrets, sqlite3, zipfile, functools
from queue import Queue, Empty
from pathlib import Path
from datetime import datetime

try:
    from flask import Flask, jsonify, request, Response, stream_with_context, session, redirect, send_file
except ImportError:
    print("ERROR: Flask not installed.\nRun: pip install flask", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ─── Globals ──────────────────────────────────────────────────────────────────
CONFIG_DIR  = Path("/etc/localnet")
CONFIG_PATH = CONFIG_DIR / "config.json"
CERT_DIR    = Path("/etc/localnet/certs")
CA_DIR      = Path("/etc/localnet/ca")
DB_PATH     = Path("/etc/localnet/localnet.db")
BACKUP_DIR  = Path("/etc/localnet/backups")

# Fallback tmp dir when not root
_tmp = Path("/tmp/localnet_v4")
_tmp.mkdir(exist_ok=True)

subscribers: list = []
log_history: list = []

DEFAULT_CONFIG = {
    "domain": "localnet",
    "vpn_safe": True,
    "server_ip": "",
    "forwarders": ["1.1.1.2", "1.0.0.2"],
    "password_hash": "",
    "secret_key": "",
    "adblock_enabled": False,
}

# ─── Config ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    for p in [CONFIG_PATH, Path("/tmp/localnet_v4_config.json")]:
        if p.exists():
            try:
                return {**DEFAULT_CONFIG, **json.loads(p.read_text())}
            except Exception:
                pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict) -> bool:
    for p in [CONFIG_PATH, Path("/tmp/localnet_v4_config.json")]:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(cfg, indent=2))
            return True
        except Exception:
            continue
    return False

def init_app_secret():
    """Ensure flask has a stable secret key (persisted in config)."""
    cfg = load_config()
    if not cfg.get("secret_key"):
        cfg["secret_key"] = secrets.token_hex(32)
        save_config(cfg)
    app.secret_key = cfg["secret_key"]

# ─── Auth Helpers ─────────────────────────────────────────────────────────────
DEFAULT_PASSWORD = "localnet"

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def check_pw(pw: str) -> bool:
    cfg = load_config()
    stored = cfg.get("password_hash", "")
    if not stored:
        # First run: accept default password
        return pw == DEFAULT_PASSWORD
    return hmac_eq(hash_pw(pw), stored)

def hmac_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())

import hmac  # ensure imported

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authed"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

# ─── SQLite DB ────────────────────────────────────────────────────────────────
def get_db_path() -> Path:
    if os.geteuid() == 0:
        return DB_PATH
    return _tmp / "localnet.db"

def db_connect():
    p = get_db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    return con

def db_init():
    with db_connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS record_notes (
            host    TEXT NOT NULL,
            domain  TEXT NOT NULL,
            note    TEXT DEFAULT '',
            PRIMARY KEY (host, domain)
        );
        CREATE TABLE IF NOT EXISTS proxy_notes (
            domain TEXT PRIMARY KEY,
            note   TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS backups (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            path       TEXT NOT NULL,
            label      TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS devices (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            ip               TEXT NOT NULL UNIQUE,
            label            TEXT DEFAULT '',
            hostname         TEXT DEFAULT '',
            mac              TEXT DEFAULT '',
            notes            TEXT DEFAULT '',
            blocked          INTEGER DEFAULT 0,
            dns_registered   INTEGER DEFAULT 0,
            first_seen       TEXT NOT NULL,
            last_seen        TEXT NOT NULL,
            query_count      INTEGER DEFAULT 0
        );
        """)

def db_get_note(table: str, key_col: str, key_val: str, extra_col: str = None, extra_val: str = None) -> str:
    try:
        with db_connect() as con:
            if extra_col:
                row = con.execute(f"SELECT note FROM {table} WHERE {key_col}=? AND {extra_col}=?",
                                  (key_val, extra_val)).fetchone()
            else:
                row = con.execute(f"SELECT note FROM {table} WHERE {key_col}=?", (key_val,)).fetchone()
            return row["note"] if row else ""
    except Exception:
        return ""

def db_set_note(table: str, key_col: str, key_val: str, note: str, extra_col: str = None, extra_val: str = None):
    try:
        with db_connect() as con:
            if extra_col:
                con.execute(f"INSERT INTO {table} ({key_col},{extra_col},note) VALUES (?,?,?) "
                            f"ON CONFLICT({key_col},{extra_col}) DO UPDATE SET note=excluded.note",
                            (key_val, extra_val, note))
            else:
                con.execute(f"INSERT INTO {table} ({key_col},note) VALUES (?,?) "
                            f"ON CONFLICT({key_col}) DO UPDATE SET note=excluded.note",
                            (key_val, note))
    except Exception as e:
        log(f"DB error: {e}", "error")

def db_list_backups() -> list:
    try:
        with db_connect() as con:
            rows = con.execute("SELECT * FROM backups ORDER BY id DESC LIMIT 20").fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

def db_add_backup(path: str, label: str):
    try:
        with db_connect() as con:
            con.execute("INSERT INTO backups (path,label,created_at) VALUES (?,?,?)",
                        (path, label, datetime.now().isoformat(timespec="seconds")))
    except Exception as e:
        log(f"DB backup log error: {e}", "error")

# ─── Device Manager DB Helpers ───────────────────────────────────────────────
DEVICE_BLOCK_ACL = Path("/etc/bind/localnet-blocked-devices.acl")
QUERY_LOG_PATH   = Path("/var/log/named/queries.log")
_device_scan_lock = threading.Lock()

def db_list_devices() -> list:
    try:
        with db_connect() as con:
            rows = con.execute(
                "SELECT * FROM devices ORDER BY last_seen DESC"
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

def db_upsert_device(ip: str, hostname: str = "", mac: str = "") -> dict:
    """Insert or update a device record when a DNS query is seen from it."""
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with db_connect() as con:
            existing = con.execute(
                "SELECT id, query_count FROM devices WHERE ip=?", (ip,)
            ).fetchone()
            if existing:
                con.execute(
                    "UPDATE devices SET last_seen=?, query_count=query_count+1"
                    + (", hostname=? " if hostname else " ")
                    + "WHERE ip=?",
                    (now, hostname, ip) if hostname else (now, ip)
                )
                return {"id": existing["id"], "ip": ip}
            else:
                cur = con.execute(
                    "INSERT INTO devices (ip, hostname, mac, first_seen, last_seen, query_count)"
                    " VALUES (?,?,?,?,?,1)",
                    (ip, hostname, mac, now, now)
                )
                return {"id": cur.lastrowid, "ip": ip}
    except Exception as e:
        log(f"Device upsert error: {e}", "error")
        return {}

def db_update_device(device_id: int, fields: dict):
    allowed = {"label", "hostname", "mac", "notes", "blocked", "dns_registered"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    try:
        with db_connect() as con:
            set_clause = ", ".join(f"{k}=?" for k in updates)
            con.execute(
                f"UPDATE devices SET {set_clause} WHERE id=?",
                (*updates.values(), device_id)
            )
    except Exception as e:
        log(f"Device update error: {e}", "error")

def db_remove_device(device_id: int):
    try:
        with db_connect() as con:
            con.execute("DELETE FROM devices WHERE id=?", (device_id,))
    except Exception as e:
        log(f"Device remove error: {e}", "error")

def db_get_device(device_id: int) -> dict | None:
    try:
        with db_connect() as con:
            row = con.execute(
                "SELECT * FROM devices WHERE id=?", (device_id,)
            ).fetchone()
            return dict(row) if row else None
    except Exception:
        return None

def _write_block_acl():
    """Rewrite the BIND9 blocked-devices ACL file from DB and reload."""
    try:
        devices = db_list_devices()
        blocked_ips = [d["ip"] for d in devices if d.get("blocked")]
        
        # Define a proper ACL block inside the included file
        acl_content = "// LocalNet managed — do not edit manually\n"
        acl_content += 'acl "localnet_blocked" {\n'
        if blocked_ips:
            acl_content += "\n".join(f"    {ip};" for ip in blocked_ips) + "\n"
        else:
            acl_content += "    none;\n"
        acl_content += "};\n"
        
        DEVICE_BLOCK_ACL.parent.mkdir(parents=True, exist_ok=True)
        DEVICE_BLOCK_ACL.write_text(acl_content)
        log(f"Block ACL updated ({len(blocked_ips)} blocked devices)", "info")
    except Exception as e:
        log(f"Block ACL write error: {e}", "error")

def _ensure_blackhole_include():
    """Ensure named.conf.options includes the ACL and references it in blackhole."""
    opts_path = Path("/etc/bind/named.conf.options")
    if not opts_path.exists():
        return
    try:
        devices = db_list_devices()
        has_blocked = any(d.get("blocked") for d in devices)

        content = opts_path.read_text()
        
        include_stmt = f'include "{DEVICE_BLOCK_ACL}";\n'
        blackhole_stmt = '    blackhole { localnet_blocked; };\n'
        
        # 1. Clean up the old broken line and any previous configurations
        content = re.sub(r'^\s*blackhole\s*\{[^\}]*\}\s*;\s*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*include\s*"' + re.escape(str(DEVICE_BLOCK_ACL)) + r'"\s*;\s*\n?', '', content, flags=re.MULTILINE)
        
        # 2. Add it back properly only if there are blocked devices
        if has_blocked:
            # The include statement MUST be at the top level
            content = include_stmt + content
            
            # The blackhole statement MUST be inside the options block
            parts = content.rsplit('};', 1)
            if len(parts) == 2:
                # Use triple braces: {{ }} for a literal { }, plus the f-string {var}
                content = parts[0] + f"{blackhole_stmt}}};" + parts[1]
            else:
                content += f"\n{blackhole_stmt}\n"
                
        opts_path.write_text(content)
        log("Blackhole ACL configured safely in named.conf.options", "info")
    except Exception as e:
        log(f"Blackhole include error: {e}", "error")

def scan_query_log(max_lines: int = 5000) -> tuple[int, int]:
    """Parse the BIND9 query log and upsert newly discovered device IPs.
    Returns (new_devices, updated_devices)."""
    new_count = 0
    upd_count = 0

    # ------------------------------------------------------------------
    # Step 1: Try the BIND9 file log
    # ------------------------------------------------------------------
    if QUERY_LOG_PATH.exists():
        skip_ips = {"127.0.0.1", "::1", "0.0.0.0"}
        server_ip = get_local_ip()
        if server_ip:
            skip_ips.add(server_ip)
        # BIND9 query log formats (both old and new):
        # Old:  DD-Mon-YYYY HH:MM:SS.mmm client 192.168.1.42#PORT (host): ...
        # New:  DD-Mon-YYYY HH:MM:SS.mmm client @0xADDR 192.168.1.42#PORT (host): ...
        pattern = re.compile(r'client\s+(?:@\S+\s+)?([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})#(\d+)')
        try:
            existing_ips = {d["ip"] for d in db_list_devices()}
            with open(QUERY_LOG_PATH, "r", errors="replace") as f:
                lines = f.readlines()[-max_lines:]
            seen_this_scan: set[str] = set()
            for line in lines:
                m = pattern.search(line)
                if not m:
                    continue
                ip = m.group(1)
                if ip in skip_ips or ip in seen_this_scan:
                    continue
                seen_this_scan.add(ip)
                is_new = ip not in existing_ips
                existing_ips.add(ip)
                db_upsert_device(ip)
                if is_new:
                    new_count += 1
                else:
                    upd_count += 1
        except Exception as e:
            log(f"Query log scan error: {e}", "error")

    # ------------------------------------------------------------------
    # Step 2: Also scan the ARP / neighbor table — reliable regardless
    #         of whether BIND9 query logging is working
    # ------------------------------------------------------------------
    try:
        new_count_arp, upd_count_arp = _scan_arp_table()
        new_count += new_count_arp
        upd_count += upd_count_arp
    except Exception as e:
        log(f"ARP scan error: {e}", "error")

    # ------------------------------------------------------------------
    # Step 3: Try DHCP leases for MAC enrichment
    # ------------------------------------------------------------------
    try:
        _enrich_from_dhcp()
    except Exception:
        pass

    return new_count, upd_count


def _scan_arp_table() -> tuple[int, int]:
    """Discover devices from the kernel ARP/neighbour table."""
    new_count = 0
    upd_count = 0
    skip_ips = {"127.0.0.1", "::1", "0.0.0.0"}
    server_ip = get_local_ip()
    if server_ip:
        skip_ips.add(server_ip)
    existing = {d["ip"]: d for d in db_list_devices()}

    # Try `ip -j neigh show` first (JSON, most reliable)
    entries: list[dict] = []
    try:
        r = subprocess.run(["ip", "-j", "neigh", "show"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            neigh = json.loads(r.stdout or "[]")
            for n in neigh:
                ip  = n.get("dst", "")
                mac = n.get("lladdr", "")
                if ip and ":" not in ip:   # skip IPv6
                    entries.append({"ip": ip, "mac": mac})
    except Exception:
        pass

    # Fallback: parse `arp -n` text output
    if not entries:
        try:
            r = subprocess.run(["arp", "-n"],
                               capture_output=True, text=True, timeout=5)
            for line in r.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    ip  = parts[0]
                    mac = parts[2] if parts[2] != "(incomplete)" else ""
                    if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                        entries.append({"ip": ip, "mac": mac})
        except Exception:
            pass

    for e in entries:
        ip  = e["ip"]
        mac = e.get("mac", "")
        if ip in skip_ips:
            continue
        is_new = ip not in existing
        result = db_upsert_device(ip, mac=mac)
        # If we got a MAC and the existing record doesn't have one, update it
        if mac and not is_new and not existing[ip].get("mac"):
            db_update_device(result.get("id", 0) or existing[ip]["id"], {"mac": mac})
        if is_new:
            new_count += 1
        else:
            upd_count += 1

    return new_count, upd_count


def _enrich_from_dhcp():
    """Read DHCP leases and backfill MAC + hostname into device records."""
    lease_file = Path("/var/lib/dhcp/dhcpd.leases")
    if not lease_file.exists():
        return
    devices_by_ip = {d["ip"]: d for d in db_list_devices()}
    try:
        text = lease_file.read_text()
        blocks = re.findall(r'lease ([\d.]+) \{([^}]+)\}', text, re.DOTALL)
        seen: dict[str, dict] = {}
        for ip, body in blocks:
            mac_m    = re.search(r'hardware ethernet ([0-9a-f:]+);', body)
            host_m   = re.search(r'client-hostname "([^"]+)";', body)
            bind_m   = re.search(r'binding state (\w+);', body)
            if bind_m and bind_m.group(1) == "active":
                seen[ip] = {
                    "mac":      mac_m.group(1)  if mac_m   else "",
                    "hostname": host_m.group(1) if host_m  else "",
                }
        for ip, info in seen.items():
            if ip in devices_by_ip:
                d = devices_by_ip[ip]
                updates: dict = {}
                if info["mac"] and not d.get("mac"):
                    updates["mac"] = info["mac"]
                if info["hostname"] and not d.get("hostname"):
                    updates["hostname"] = info["hostname"]
                if updates:
                    db_update_device(d["id"], updates)
    except Exception:
        pass

# Background scanner — runs every 30 s when tracking is enabled
_tracking_active = False
_tracking_thread = None

def _tracking_worker():
    global _tracking_active
    # Brief initial delay so BIND9 reload has time to complete
    time.sleep(3)
    while _tracking_active:
        with _device_scan_lock:
            try:
                new_devs, upd_devs = scan_query_log()
                if new_devs:
                    log(f"Device tracking: {new_devs} new device(s) discovered", "success")
                elif upd_devs:
                    log(f"Device tracking: {upd_devs} existing device(s) updated", "info")
            except Exception as e:
                log(f"Tracking worker error: {e}", "error")
        for _ in range(30):   # 30-second interval
            if not _tracking_active:
                break
            time.sleep(1)

def start_device_tracking():
    global _tracking_active, _tracking_thread
    if _tracking_active and _tracking_thread and _tracking_thread.is_alive():
        return
    _tracking_active = True
    _tracking_thread = threading.Thread(target=_tracking_worker, daemon=True)
    _tracking_thread.start()
    log("Device tracking started", "success")

def stop_device_tracking():
    global _tracking_active
    _tracking_active = False
    log("Device tracking stopped", "info")

# ─── Logging ──────────────────────────────────────────────────────────────────
def log(msg: str, level: str = "info"):
    entry = {"t": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level}
    log_history.append(entry)
    if len(log_history) > 1000:
        log_history.pop(0)
    for q in subscribers:
        try:
            q.put_nowait(entry)
        except Exception:
            pass

# ─── Helpers ──────────────────────────────────────────────────────────────────
def is_root() -> bool:
    return os.geteuid() == 0

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""

def get_interfaces() -> list:
    try:
        r = subprocess.run(['ip', '-j', 'addr'], capture_output=True, text=True, timeout=3)
        ifaces = json.loads(r.stdout)
        result = []
        skip = ('lo', 'docker0', 'br-')
        for iface in ifaces:
            name = iface.get('ifname', '')
            if any(name.startswith(s) for s in skip) or name.startswith('veth'):
                continue
            for addr in iface.get('addr_info', []):
                if addr.get('family') == 'inet':
                    result.append({
                        "name": name,
                        "ip": addr['local'],
                        "prefix": addr.get('prefixlen', 24),
                        "state": iface.get('operstate', 'UNKNOWN'),
                    })
        return result
    except Exception:
        ip = get_local_ip()
        return [{"name": "eth0", "ip": ip, "prefix": 24, "state": "UP"}] if ip else []

def find_reverse_file(domain: str) -> str:
    matches = [f for f in glob.glob("/etc/bind/db.*.*.*") if domain not in f]
    return matches[0] if matches else ""

def parse_zone_records(domain: str) -> list:
    zone_file = f"/etc/bind/db.{domain}"
    records = []
    if not Path(zone_file).exists():
        return records
    try:
        with open(zone_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';') or line.startswith('$'):
                    continue
                if any(k in line for k in ('SOA', 'NS ', '@')):
                    continue
                parts = line.split()
                if 'IN' in parts:
                    idx = parts.index('IN')
                    if idx >= 0 and idx + 2 < len(parts):
                        rtype = parts[idx + 1]
                        if rtype in ('A', 'CNAME', 'MX', 'TXT', 'AAAA'):
                            records.append({
                                "host": parts[0],
                                "type": rtype,
                                "value": ' '.join(parts[idx + 2:]),
                            })
    except Exception as e:
        log(f"Error reading zone file: {e}", "error")
    return records

def list_nginx_proxies() -> list:
    proxies = []
    enabled = Path('/etc/nginx/sites-enabled')
    avail   = Path('/etc/nginx/sites-available')
    if not enabled.exists():
        return proxies
    for link in enabled.iterdir():
        if link.name == 'default':
            continue
        src = avail / link.name
        if src.exists():
            try:
                content = src.read_text()
                port_m = re.search(r'proxy_pass http://[\d.]+:(\d+)', content)
                tmpl_m = re.search(r'# template: (\w+)', content)
                proxies.append({
                    "domain":   link.name,
                    "port":     port_m.group(1) if port_m else '?',
                    "template": tmpl_m.group(1) if tmpl_m else 'basic',
                })
            except Exception:
                pass
    return proxies

def list_certs() -> list:
    if not CERT_DIR.exists():
        return []
    return [
        {"name": f.stem, "path": str(f)}
        for f in CERT_DIR.glob("*.pem")
        if not f.name.endswith("-key.pem")
    ]

# ─── Backup System ───────────────────────────────────────────────────────────
def create_backup(label: str = "auto") -> str | None:
    """Zip /etc/bind and /etc/nginx before destructive ops. Returns zip path."""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = re.sub(r'[^a-z0-9_]', '_', label.lower())[:40]
        zip_path = str(BACKUP_DIR / f"backup_{ts}_{safe_label}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for src_dir in ["/etc/bind", "/etc/nginx"]:
                p = Path(src_dir)
                if p.exists():
                    for f in p.rglob("*"):
                        if f.is_file():
                            try:
                                zf.write(f, arcname=str(f))
                            except Exception:
                                pass
        db_add_backup(zip_path, label)
        log(f"✔ Backup saved: {zip_path}", "success")
        return zip_path
    except Exception as e:
        log(f"Backup failed: {e}", "error")
        return None

def restore_backup(zip_path: str) -> bool:
    """Restore /etc/bind and /etc/nginx from a backup zip."""
    try:
        p = Path(zip_path)
        if not p.exists():
            log(f"Backup not found: {zip_path}", "error")
            return False
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall("/")
        log(f"✔ Restored from {zip_path}", "success")
        return True
    except Exception as e:
        log(f"Restore failed: {e}", "error")
        return False

# ─── Script Runner ────────────────────────────────────────────────────────────
def run_script(script: str, label: str = "", backup: bool = True):
    def worker():
        if backup:
            create_backup(label or "pre_op")
        path = "/tmp/_localnet_v4.sh"
        Path(path).write_text(script)
        os.chmod(path, 0o755)
        if label:
            log(f"▶ {label}", "info")
        try:
            proc = subprocess.Popen(
                ["bash", path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in proc.stdout:
                s = line.rstrip()
                if s:
                    log(s)
            proc.wait()
            if proc.returncode == 0:
                log(f"✔ Complete: {label}", "success")
            else:
                log(f"✘ Failed (exit {proc.returncode}): {label}", "error")
        except Exception as e:
            log(f"Script error: {e}", "error")
    threading.Thread(target=worker, daemon=True).start()

def b64w(path: str, content: str) -> str:
    """Return bash line that base64-decodes content into path (avoids heredoc escaping)."""
    b64 = base64.b64encode(content.encode()).decode()
    return f"printf '%s' '{b64}' | base64 -d > '{path}'"

# ─── Nginx Templates ──────────────────────────────────────────────────────────
NGINX_TEMPLATES = {
    "basic": {
        "label": "Basic Proxy",
        "desc":  "Simple HTTP reverse proxy",
        "icon":  "⇌",
        "color": "#4a9eff",
    },
    "websocket": {
        "label": "WebSocket",
        "desc":  "WebSocket-capable (Grafana, Jupyter, etc.)",
        "icon":  "⚡",
        "color": "#a78bfa",
    },
    "homeassistant": {
        "label": "Home Assistant",
        "desc":  "Long-poll + WebSocket for HA",
        "icon":  "⌂",
        "color": "#34d399",
    },
    "nextcloud": {
        "label": "Nextcloud",
        "desc":  "Large uploads, CalDAV/CardDAV",
        "icon":  "☁",
        "color": "#60a5fa",
    },
    "loadbalancer": {
        "label": "Load Balancer",
        "desc":  "Round-robin multiple upstreams",
        "icon":  "⚖",
        "color": "#fbbf24",
    },
}

# Uses plain .replace() so $host etc. stay literal — no f-string $ conflicts.
NGINX_CONFIGS = {
    "basic": """\
# template: basic
server {
    listen 80;
    server_name DOMAIN;
    location / {
        proxy_pass http://UPIP:PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}""",
    "websocket": """\
# template: websocket
server {
    listen 80;
    server_name DOMAIN;
    location / {
        proxy_pass http://UPIP:PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}""",
    "homeassistant": """\
# template: homeassistant
server {
    listen 80;
    server_name DOMAIN;
    location / {
        proxy_pass http://UPIP:PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600;
        proxy_send_timeout 3600;
    }
    location /api/websocket {
        proxy_pass http://UPIP:PORT/api/websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}""",
    "nextcloud": """\
# template: nextcloud
server {
    listen 80;
    server_name DOMAIN;
    client_max_body_size 10G;
    proxy_request_buffering off;
    location / {
        proxy_pass http://UPIP:PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_send_timeout 300;
        proxy_buffering off;
    }
    location /.well-known/carddav { return 301 $scheme://$host/remote.php/dav; }
    location /.well-known/caldav  { return 301 $scheme://$host/remote.php/dav; }
}""",
    "loadbalancer": """\
# template: loadbalancer
upstream SAFENAME_backend {
UPSTREAM_LINES
    keepalive 32;
}
server {
    listen 80;
    server_name DOMAIN;
    location / {
        proxy_pass http://SAFENAME_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}""",
}

def build_nginx_config(template, domain, upstream_ip, port, extras=None):
    extras = extras or {}
    cfg = NGINX_CONFIGS.get(template, NGINX_CONFIGS["basic"])
    cfg = cfg.replace("DOMAIN", domain).replace("UPIP", upstream_ip).replace("PORT", str(port))
    if template == "loadbalancer":
        raw = extras.get("upstreams", f"{upstream_ip}:{port}")
        lines = "\n".join(f"    server {u.strip()};" for u in raw.splitlines() if u.strip())
        safe = re.sub(r'[^a-z0-9]', '_', domain.lower())
        cfg = cfg.replace("UPSTREAM_LINES", lines).replace("SAFENAME", safe)
    return cfg

# ─── API: Status & Config ─────────────────────────────────────────────────────
@app.route('/api/status')
def api_status():
    svcs = ['bind9', 'nginx', 'systemd-resolved']
    status = {}
    for s in svcs:
        try:
            r = subprocess.run(['systemctl', 'is-active', s],
                               capture_output=True, text=True, timeout=3)
            status[s] = r.stdout.strip()
        except Exception:
            status[s] = 'unknown'
    cfg = load_config()
    resolv = ""
    try:
        resolv = Path('/etc/resolv.conf').read_text()[:300]
    except Exception:
        pass
    return jsonify({
        "services":      status,
        "record_count":  len(parse_zone_records(cfg['domain'])),
        "proxy_count":   len(list_nginx_proxies()),
        "cert_count":    len(list_certs()),
        "resolv":        resolv,
        "is_root":       is_root(),
        "server_ip":     get_local_ip(),
        "domain":        cfg['domain'],
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'GET':
        cfg = load_config()
        cfg['server_ip'] = cfg.get('server_ip') or get_local_ip()
        cfg['interfaces'] = get_interfaces()
        return jsonify(cfg)
    data = request.json or {}
    cfg = load_config()
    for k in DEFAULT_CONFIG:
        if k in data:
            cfg[k] = data[k]
    save_config(cfg)
    log("Configuration saved.", "success")
    return jsonify({"ok": True})

@app.route('/api/network/interfaces')
def api_interfaces():
    return jsonify(get_interfaces())

# ─── API: DNS ─────────────────────────────────────────────────────────────────
@app.route('/api/dns/install', methods=['POST'])
def api_dns_install():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data    = request.json or {}
    cfg     = load_config()
    domain  = data.get('domain', cfg['domain']).strip()
    vpn     = data.get('vpn_safe', cfg['vpn_safe'])
    ip      = data.get('server_ip') or get_local_ip()
    fwds    = data.get('forwarders', cfg.get('forwarders', ['1.1.1.2', '1.0.0.2']))

    cfg.update({"domain": domain, "vpn_safe": vpn, "server_ip": ip})
    save_config(cfg)

    p      = ip.split('.')
    o1,o2,o3,o4 = p
    subnet    = f"{o1}.{o2}.{o3}.0/24"
    rev_zone  = f"{o3}.{o2}.{o1}.in-addr.arpa"
    rev_file  = f"/etc/bind/db.{o1}.{o2}.{o3}"
    zone_file = f"/etc/bind/db.{domain}"
    fwd_mode  = "first" if vpn else "only"
    fwd_lines = "\n        ".join(f"{f};" for f in fwds)

    opts = f"""acl "trusted_network" {{
    127.0.0.1;
    {subnet};
}};
options {{
    directory "/var/cache/bind";
    allow-query     {{ "trusted_network"; }};
    allow-recursion {{ "trusted_network"; }};
    allow-transfer  {{ none; }};
    recursion yes;
    forwarders {{ {fwd_lines} }};
    forward {fwd_mode};
    dnssec-validation auto;
    listen-on {{ 127.0.0.1; {ip}; }};
    listen-on-v6 {{ none; }};
}};"""

    zones = f"""zone "{domain}" {{
    type master;
    file "{zone_file}";
}};
zone "{rev_zone}" {{
    type master;
    file "{rev_file}";
}};"""

    fzone = f"""$TTL 86400
@   IN  SOA   ns1.{domain}. admin.{domain}. (
              SERIAL ; Serial
              3600   ; Refresh
              900    ; Retry
              604800 ; Expire
              86400 ); Minimum TTL
@       IN  NS    ns1.{domain}.
ns1     IN  A     {ip}
"""
    rzone = f"""$TTL 86400
@   IN  SOA   ns1.{domain}. admin.{domain}. (
              SERIAL ; Serial
              3600   ; Refresh
              900    ; Retry
              604800 ; Expire
              86400 ); Minimum TTL
@    IN  NS    ns1.{domain}.
{o4}  IN  PTR   ns1.{domain}.
"""
    # New Resolved Configuration String
    resolved_conf = f"[Resolve]\nDNS=127.0.0.1\nDomains=~{domain}\n"

    script = f"""#!/bin/bash
set -e
echo "[1/8] Installing BIND9..."
apt-get update -qq && apt-get install -y bind9 bind9utils dnsutils

echo "[2/8] Writing named.conf.options..."
{b64w('/etc/bind/named.conf.options', opts)}

echo "[3/8] Writing zone declarations..."
{b64w('/etc/bind/named.conf.local', zones)}

echo "[4/8] Writing forward zone..."
SERIAL=$(date +%s)
{b64w(zone_file, fzone)}
sed -i "s/SERIAL/$SERIAL/" '{zone_file}'

echo "[5/8] Writing reverse zone..."
{b64w(rev_file, rzone)}
sed -i "s/SERIAL/$SERIAL/" '{rev_file}'

echo "[6/8] Validating and starting BIND9..."
named-checkconf
named-checkzone "{domain}" "{zone_file}"
named-checkzone "{rev_zone}" "{rev_file}"
systemctl enable named
systemctl restart named

echo "[7/8] Configuring systemd-resolved routing..."
mkdir -p /etc/systemd/resolved.conf.d/
{b64w('/etc/systemd/resolved.conf.d/localnet.conf', resolved_conf)}
systemctl daemon-reload
systemctl restart systemd-resolved

echo "[8/8] Finalizing Resolver..."
resolvectl flush-caches
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

echo "✔ DNS installed — domain: .{domain}  server: {ip}"
"""
    run_script(script, f"Install BIND9 (.{domain})")
    return jsonify({"ok": True})

@app.route('/api/dns/remove', methods=['POST'])
def api_dns_remove():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
systemctl stop bind9 2>/dev/null || true
systemctl disable bind9 2>/dev/null || true
apt-get purge -y bind9 bind9utils bind9-doc dnsutils 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true
rm -rf /etc/bind /var/cache/bind /var/lib/bind
rm -f /etc/systemd/resolved.conf.d/localnet.conf
systemctl daemon-reload
systemctl restart systemd-resolved 2>/dev/null || true
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
echo "✔ BIND9 removed. Internet DNS restored."
"""
    run_script(script, "Remove BIND9")
    return jsonify({"ok": True})

@app.route('/api/dns/records')
def api_dns_records():
    cfg = load_config()
    return jsonify(parse_zone_records(cfg['domain']))

@app.route('/api/dns/records/a', methods=['POST'])
def api_add_a():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data     = request.json or {}
    cfg      = load_config()
    domain   = cfg['domain']
    host     = data['host'].strip()
    ip       = data['ip'].strip()
    last     = ip.split('.')[-1]
    zone_file = f"/etc/bind/db.{domain}"
    rev_file  = find_reverse_file(domain)

    rev_line  = f"echo '{last}    IN  PTR {host}.{domain}.' >> '{rev_file}'" if rev_file else "true"
    rev_ser   = f"sed -i 's/[0-9]{{10}} ; Serial/'$SERIAL' ; Serial/' '{rev_file}'" if rev_file else "true"

    script = f"""#!/bin/bash
echo '{host}    IN  A   {ip}' >> '{zone_file}'
{rev_line}
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
{rev_ser}
named-checkconf && systemctl reload bind9
echo "Added: {host}.{domain} → {ip}"
"""
    run_script(script, f"Add A record: {host} → {ip}")
    return jsonify({"ok": True})

@app.route('/api/dns/records/cname', methods=['POST'])
def api_add_cname():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data     = request.json or {}
    cfg      = load_config()
    domain   = cfg['domain']
    alias    = data['alias'].strip()
    target   = data['target'].strip()
    zone_file = f"/etc/bind/db.{domain}"

    script = f"""#!/bin/bash
echo '{alias}    IN  CNAME {target}.{domain}.' >> '{zone_file}'
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
named-checkconf && systemctl reload named
echo "Added CNAME: {alias}.{domain} → {target}.{domain}"
"""
    run_script(script, f"Add CNAME: {alias} → {target}")
    return jsonify({"ok": True})

@app.route('/api/dns/records/<host>', methods=['DELETE'])
def api_remove_record(host):
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    cfg      = load_config()
    domain   = cfg['domain']
    zone_file = f"/etc/bind/db.{domain}"
    rev_file  = find_reverse_file(domain)

    rev_del = f"sed -i '/PTR {host}.{domain}./d' '{rev_file}'" if rev_file else "true"
    rev_ser = f"sed -i 's/[0-9]{{10}} ; Serial/'$SERIAL' ; Serial/' '{rev_file}'" if rev_file else "true"

    script = f"""#!/bin/bash
sed -i '/^{host}/d' '{zone_file}'
{rev_del}
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
{rev_ser}
named-checkconf && systemctl reload named
echo "Removed: {host}"
"""
    run_script(script, f"Remove record: {host}")
    return jsonify({"ok": True})

@app.route('/api/dns/test', methods=['POST'])
def api_dns_test():
    data   = request.json or {}
    name   = data.get('name', '').strip()
    server = data.get('server') or get_local_ip()
    try:
        r = subprocess.run(['dig', f'@{server}', name, '+short', '+time=2'],
                           capture_output=True, text=True, timeout=6)
        result = r.stdout.strip() or "(no answer)"
        log(f"dig @{server} {name}  →  {result}", "info")
        return jsonify({"result": result, "ok": True})
    except Exception as e:
        return jsonify({"result": f"Error: {e}", "ok": False})

# ─── API: Nginx ───────────────────────────────────────────────────────────────
@app.route('/api/nginx/install', methods=['POST'])
def api_nginx_install():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
apt-get update -qq && apt-get install -y nginx
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx && systemctl enable nginx
echo "✔ Nginx installed and running"
"""
    run_script(script, "Install Nginx")
    return jsonify({"ok": True})

@app.route('/api/nginx/uninstall', methods=['POST'])
def api_nginx_uninstall():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
systemctl stop nginx || true
apt-get purge -y nginx nginx-common nginx-full || true
apt-get autoremove -y || true
rm -rf /etc/nginx /var/log/nginx
echo "✔ Nginx removed"
"""
    run_script(script, "Remove Nginx")
    return jsonify({"ok": True})

@app.route('/api/nginx/proxies')
def api_proxies():
    return jsonify(list_nginx_proxies())

@app.route('/api/nginx/proxies', methods=['POST'])
def api_add_proxy():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data        = request.json or {}
    domain      = data['domain'].strip()
    template    = data.get('template', 'basic')
    upstream_ip = data.get('upstream_ip', '127.0.0.1').strip()
    port        = str(data.get('port', '80')).strip()
    extras      = data.get('extras', {})

    config_str = build_nginx_config(template, domain, upstream_ip, port, extras)
    script = f"""#!/bin/bash
{b64w(f'/etc/nginx/sites-available/{domain}', config_str)}
ln -sf '/etc/nginx/sites-available/{domain}' '/etc/nginx/sites-enabled/'
nginx -t && systemctl reload nginx
echo "✔ Proxy: {domain} → {upstream_ip}:{port} [{template}]"
"""
    run_script(script, f"Add proxy: {domain}")
    return jsonify({"ok": True})

@app.route('/api/nginx/proxies/<domain>', methods=['DELETE'])
def api_remove_proxy(domain):
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = f"""#!/bin/bash
rm -f '/etc/nginx/sites-enabled/{domain}'
rm -f '/etc/nginx/sites-available/{domain}'
systemctl reload nginx
echo "✔ Removed proxy: {domain}"
"""
    run_script(script, f"Remove proxy: {domain}")
    return jsonify({"ok": True})

@app.route('/api/nginx/templates')
def api_nginx_templates():
    return jsonify(NGINX_TEMPLATES)

# ─── API: SSL ─────────────────────────────────────────────────────────────────
@app.route('/api/ssl/mkcert/install', methods=['POST'])
def api_mkcert_install():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = f"""#!/bin/bash
echo "Installing dependencies..."
apt-get update -qq && apt-get install -y libnss3-tools wget
ARCH=$(dpkg --print-architecture)
case $ARCH in
    amd64) MA=linux-amd64 ;;
    arm64) MA=linux-arm64 ;;
    armhf) MA=linux-arm ;;
    *)     MA=linux-amd64 ;;
esac
echo "Fetching latest mkcert release..."
VER=$(wget -qO- https://api.github.com/repos/FiloSottile/mkcert/releases/latest | grep tag_name | cut -d'"' -f4)
wget -qO /usr/local/bin/mkcert "https://github.com/FiloSottile/mkcert/releases/download/$VER/mkcert-$VER-$MA"
chmod +x /usr/local/bin/mkcert
mkdir -p '{CA_DIR}'
CAROOT='{CA_DIR}' mkcert -install
echo "✔ mkcert installed — local CA ready at {CA_DIR}"
echo "  Import {CA_DIR}/rootCA.pem into your browser to trust certs."
"""
    run_script(script, "Install mkcert")
    return jsonify({"ok": True})

@app.route('/api/ssl/mkcert/cert', methods=['POST'])
def api_mkcert_cert():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
        
    data   = request.json or {}
    cfg    = load_config()
    
    # Use the provided domain or fall back to the TLD from config
    raw_domain = data.get('domain', '').strip() or cfg.get('domain', 'localnet')
    # Sanitize filename (replace * with 'wildcard') for safer filesystem handling
    file_name = raw_domain.replace('*', 'wildcard')
    tld = cfg.get('domain', 'localnet')
    
    CERT_DIR.mkdir(parents=True, exist_ok=True)

    script = f"""#!/bin/bash
set -e
cd '{CERT_DIR}'

# 1. Generate the certificate including the wildcard and TLD for maximum compatibility
CAROOT='{CA_DIR}' mkcert \\
    -cert-file "{file_name}.pem" \\
    -key-file  "{file_name}-key.pem" \\
    "{raw_domain}" "*.{tld}" "{tld}"

echo "✔ Certificate: {CERT_DIR}/{file_name}.pem"
echo "   Key:         {CERT_DIR}/{file_name}-key.pem"

# 2. Automated Nginx Injection
# Check for a site config matching the domain or the TLD
NGINX_CONF="/etc/nginx/sites-available/{raw_domain}"
if [ ! -f "$NGINX_CONF" ]; then
    NGINX_CONF="/etc/nginx/sites-available/{tld}"
fi

if [ -f "$NGINX_CONF" ]; then
    echo "Found Nginx config at $NGINX_CONF. Checking SSL status..."
    
    if ! grep -q "ssl_certificate" "$NGINX_CONF"; then
        echo "Injecting SSL directives after server_name..."
        
        # We target the line containing 'server_name' and append our SSL block below it
        # The 'a' command in sed appends text AFTER the matched line
        sed -i '/server_name/a \    listen 443 ssl;\\n    ssl_certificate {CERT_DIR}/{file_name}.pem;\\n    ssl_certificate_key {CERT_DIR}/{file_name}-key.pem;' "$NGINX_CONF"
        
        if nginx -t; then
            systemctl reload nginx
            echo "✔ Nginx SSL configuration applied and reloaded."
        else
            echo "✘ Nginx config test failed. Manual check required."
            exit 1
        fi
    else
        echo "ℹ SSL already configured in $NGINX_CONF. Skipping injection."
    fi
else
    echo "ℹ No matching Nginx config found in sites-available. Skipping auto-config."
fi
"""
    run_script(script, f"Generate cert & auto-configure: {raw_domain}")
    return jsonify({"ok": True})

@app.route('/api/ssl/rootca')
def api_get_root_ca():
    ca_path = CA_DIR / "rootCA.pem"
    if not ca_path.exists():
        return "Root CA not found. Please run 'Install mkcert' first.", 404
    return send_file(ca_path, as_attachment=True, download_name="LocalNet-Root-CA.pem")

@app.route('/api/ssl/certs')
def api_list_certs():
    return jsonify(list_certs())

@app.route('/api/ssl/certs/<domain>', methods=['DELETE'])
def api_delete_cert(domain):
    if not is_root():
        return jsonify({"error": "Root required"}), 403

    file_name = domain.replace('*', 'wildcard')
    cert_path = CERT_DIR / f"{file_name}.pem"
    key_path  = CERT_DIR / f"{file_name}-key.pem"

    script = f"""#!/bin/bash
# A. Remove the certificate files
rm -f "{cert_path}" "{key_path}"
echo "✔ Removed cert files for {domain}"

# B. Cleanup Nginx config
NGINX_CONF="/etc/nginx/sites-available/{domain}"

if [ -f "$NGINX_CONF" ]; then
    echo "Cleaning SSL directives from $NGINX_CONF..."
    
    # We use a pattern match to delete any line starting with 'ssl_' 
    # and the specific listen 443 line.
    sed -i '/listen 443 ssl;/d' "$NGINX_CONF"
    sed -i '/ssl_/d' "$NGINX_CONF"
    
    # C. Verify and Reload
    if nginx -t; then
        systemctl reload nginx
        echo "✔ Nginx cleaned and reloaded successfully"
    else
        echo "⚠️ Nginx cleanup failed validation. Manual check: $NGINX_CONF"
        exit 1
    fi
else
    echo "ℹ No config found at $NGINX_CONF. Files deleted, config skipped."
fi
"""
    run_script(script, f"Delete cert & cleanup Nginx: {domain}")
    return jsonify({"ok": True})

# ─── API: Service Control ─────────────────────────────────────────────────────
@app.route('/api/service/reload', methods=['POST'])
def api_service_reload():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    svc = (request.json or {}).get('service', '')
    if svc not in ('bind9', 'nginx', 'systemd-resolved'):
        return jsonify({"error": "Unknown service"}), 400
    action = "restart" if svc == "systemd-resolved" else "reload"
    run_script(f"systemctl {action} {svc} && echo '✔ {svc} {action}ed'", f"{action} {svc}")
    return jsonify({"ok": True})

# ─── API: SSE Log Stream ──────────────────────────────────────────────────────
@app.route('/api/logs/stream')
def log_stream():
    q = Queue()
    subscribers.append(q)
    def generate():
        for entry in log_history[-80:]:
            yield f"data: {json.dumps(entry)}\n\n"
        try:
            while True:
                try:
                    entry = q.get(timeout=20)
                    yield f"data: {json.dumps(entry)}\n\n"
                except Empty:
                    yield f"data: {json.dumps({'type':'ping'})}\n\n"
        finally:
            try:
                subscribers.remove(q)
            except ValueError:
                pass
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )

# ─── Auth Routes ─────────────────────────────────────────────────────────────
@app.before_request
def require_auth():
    exempt = ('login_page', 'static')
    if request.endpoint in exempt:
        return
    if not session.get("authed"):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Unauthorized"}), 401
        return redirect("/login")

@app.route('/login', methods=['GET', 'POST'], endpoint='login_page')
def login():
    err = ""
    if request.method == 'POST':
        pw = request.form.get("password", "")
        if check_pw(pw):
            session["authed"] = True
            cfg = load_config()
            # If using default password, store its hash now to lock it in
            if not cfg.get("password_hash"):
                cfg["password_hash"] = hash_pw(DEFAULT_PASSWORD)
                save_config(cfg)
            return redirect("/")
        err = "Invalid password"
    err_html = f'<div class="login-err">{err}</div>' if err else ''
    return LOGIN_PAGE.replace("__ERROR_HTML__", err_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

@app.route('/api/auth/change-password', methods=['POST'])
def api_change_password():
    data = request.json or {}
    cur  = data.get("current", "")
    new_pw = data.get("new", "")
    if not check_pw(cur):
        return jsonify({"error": "Current password incorrect"}), 403
    if len(new_pw) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    cfg = load_config()
    cfg["password_hash"] = hash_pw(new_pw)
    save_config(cfg)
    log("Password changed", "success")
    return jsonify({"ok": True})

# ─── API: Extra DNS Record Types ─────────────────────────────────────────────
@app.route('/api/dns/records/txt', methods=['POST'])
def api_add_txt():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data      = request.json or {}
    cfg       = load_config()
    domain    = cfg['domain']
    host      = data['host'].strip()
    value     = data['value'].strip()
    zone_file = f"/etc/bind/db.{domain}"
    # TXT values must be quoted
    if not value.startswith('"'):
        value = f'"{value}"'
    script = f"""#!/bin/bash
echo '{host}    IN  TXT  {value}' >> '{zone_file}'
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
named-checkconf && systemctl reload named
echo "Added TXT: {host} = {value}"
"""
    run_script(script, f"Add TXT: {host}", backup=False)
    return jsonify({"ok": True})

@app.route('/api/dns/records/srv', methods=['POST'])
def api_add_srv():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data      = request.json or {}
    cfg       = load_config()
    domain    = cfg['domain']
    service   = data['service'].strip()   # e.g. _http
    proto     = data['proto'].strip()     # e.g. _tcp
    priority  = data.get('priority', 10)
    weight    = data.get('weight', 5)
    port      = data['port']
    target    = data['target'].strip()
    zone_file = f"/etc/bind/db.{domain}"
    host      = f"{service}.{proto}.{domain}."
    script = f"""#!/bin/bash
echo '{service}.{proto}  IN  SRV  {priority} {weight} {port} {target}.{domain}.' >> '{zone_file}'
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
named-checkconf && systemctl reload named
echo "Added SRV: {service}.{proto} → {target}:{port}"
"""
    run_script(script, f"Add SRV: {service}.{proto}", backup=False)
    return jsonify({"ok": True})

@app.route('/api/dns/records/wildcard', methods=['POST'])
def api_add_wildcard():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data      = request.json or {}
    cfg       = load_config()
    domain    = cfg['domain']
    ip        = data['ip'].strip()
    zone_file = f"/etc/bind/db.{domain}"
    script = f"""#!/bin/bash
echo '*    IN  A  {ip}' >> '{zone_file}'
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
named-checkconf && systemctl reload named
echo "Added wildcard: *.{domain} → {ip}"
"""
    run_script(script, f"Add wildcard *.{domain} → {ip}", backup=False)
    return jsonify({"ok": True})

@app.route('/api/dns/notes', methods=['POST'])
def api_set_record_note():
    data = request.json or {}
    cfg  = load_config()
    db_set_note("record_notes", "host", data.get("host",""), data.get("note",""),
                "domain", cfg['domain'])
    return jsonify({"ok": True})

# ─── API: Device Manager ──────────────────────────────────────────────────────
@app.route('/api/devices', methods=['GET'])
def api_devices_list():
    return jsonify(db_list_devices())

@app.route('/api/devices', methods=['POST'])
def api_devices_add():
    data = request.json or {}
    ip   = data.get("ip", "").strip()
    if not ip:
        return jsonify({"error": "IP required"}), 400
    result = db_upsert_device(
        ip,
        hostname=data.get("hostname", ""),
        mac=data.get("mac", "")
    )
    if data.get("label"):
        db_update_device(result["id"], {"label": data["label"]})
    if data.get("notes"):
        db_update_device(result["id"], {"notes": data["notes"]})
    log(f"Device manually added: {ip}", "info")
    return jsonify({"ok": True, **result})

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def api_devices_update(device_id):
    data = request.json or {}
    allowed = {"label", "hostname", "mac", "notes"}
    fields  = {k: v for k, v in data.items() if k in allowed}
    if not fields:
        return jsonify({"error": "No valid fields"}), 400
    db_update_device(device_id, fields)
    return jsonify({"ok": True})

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def api_devices_remove(device_id):
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    db_remove_device(device_id)
    log(f"Device removed: {device.get('ip')} ({device.get('label') or 'unlabeled'})", "info")
    return jsonify({"ok": True})

@app.route('/api/devices/<int:device_id>/block', methods=['POST'])
def api_devices_block(device_id):
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    db_update_device(device_id, {"blocked": 1})
    _write_block_acl()
    _ensure_blackhole_include()
    run_script("named-checkconf && systemctl reload named && echo '✔ Device blocked'",
               f"Block device {device['ip']}", backup=False)
    log(f"DNS blocked: {device['ip']} ({device.get('label') or 'unlabeled'})", "warn")
    return jsonify({"ok": True})

@app.route('/api/devices/<int:device_id>/unblock', methods=['POST'])
def api_devices_unblock(device_id):
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    db_update_device(device_id, {"blocked": 0})
    _write_block_acl()
    _ensure_blackhole_include() # <--- ADD THIS LINE HERE
    
    run_script("named-checkconf && systemctl reload named && echo '✔ Device unblocked'",
               f"Unblock device {device['ip']}", backup=False)
    log(f"DNS unblocked: {device['ip']} ({device.get('label') or 'unlabeled'})", "success")
    return jsonify({"ok": True})

@app.route('/api/devices/<int:device_id>/register', methods=['POST'])
def api_devices_register(device_id):
    """Add (or update) an A record in BIND9 for this device."""
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    data     = request.json or {}
    cfg      = load_config()
    domain   = cfg['domain']
    hostname = (data.get("hostname") or device.get("hostname") or "").strip()
    if not hostname:
        return jsonify({"error": "Hostname required"}), 400
    ip        = device['ip']
    last      = ip.split('.')[-1]
    zone_file = f"/etc/bind/db.{domain}"
    rev_file  = find_reverse_file(domain)
    rev_line  = f"echo '{last}    IN  PTR {hostname}.{domain}.' >> '{rev_file}'" if rev_file else "true"
    rev_ser   = f"sed -i 's/[0-9]{{10}} ; Serial/'$SERIAL' ; Serial/' '{rev_file}'" if rev_file else "true"
    safe_host = re.sub(r'[^a-z0-9\-]', '-', hostname.lower())
    script = f"""#!/bin/bash
# Remove any existing A record for this host first
sed -i '/^{safe_host}[[:space:]]/d' '{zone_file}'
echo '{safe_host}    IN  A   {ip}' >> '{zone_file}'
{rev_line}
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
{rev_ser}
named-checkconf && systemctl reload named
echo "✔ Registered: {safe_host}.{domain} → {ip}"
"""
    run_script(script, f"Register device: {safe_host} → {ip}", backup=False)
    db_update_device(device_id, {"hostname": safe_host, "dns_registered": 1})
    return jsonify({"ok": True, "hostname": safe_host})

@app.route('/api/devices/<int:device_id>/unregister', methods=['POST'])
def api_devices_unregister(device_id):
    """Remove the device's A record from BIND9."""
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    cfg       = load_config()
    domain    = cfg['domain']
    hostname  = device.get("hostname", "").strip()
    if not hostname:
        return jsonify({"error": "No hostname registered for this device"}), 400
    zone_file = f"/etc/bind/db.{domain}"
    rev_file  = find_reverse_file(domain)
    rev_del   = f"sed -i '/PTR {hostname}.{domain}./d' '{rev_file}'" if rev_file else "true"
    rev_ser   = f"sed -i 's/[0-9]{{10}} ; Serial/'$SERIAL' ; Serial/' '{rev_file}'" if rev_file else "true"
    script = f"""#!/bin/bash
sed -i '/^{hostname}[[:space:]]/d' '{zone_file}'
{rev_del}
SERIAL=$(date +%s)
sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" '{zone_file}'
{rev_ser}
named-checkconf && systemctl reload named
echo "✔ DNS record removed: {hostname}.{domain}"
"""
    run_script(script, f"Unregister device: {hostname}", backup=False)
    db_update_device(device_id, {"dns_registered": 0})
    return jsonify({"ok": True})

@app.route('/api/devices/<int:device_id>/ping', methods=['POST'])
def api_devices_ping(device_id):
    device = db_get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    ip = device['ip']
    try:
        r = subprocess.run(
            ['ping', '-c', '3', '-W', '1', ip],
            capture_output=True, text=True, timeout=8
        )
        alive  = r.returncode == 0
        output = r.stdout.strip() or r.stderr.strip()
        # Extract round-trip summary if available
        rtt_m = re.search(r'rtt min/avg/max/mdev = ([\d./]+)', output)
        rtt   = rtt_m.group(1) if rtt_m else None
        return jsonify({"ok": True, "alive": alive, "output": output, "rtt": rtt})
    except Exception as e:
        return jsonify({"ok": False, "alive": False, "output": str(e), "rtt": None})

@app.route('/api/devices/tracking/enable', methods=['POST'])
def api_devices_tracking_enable():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    logging_conf = """\
logging {
    channel localnet_query_log {
        file "/var/log/named/queries.log" versions 5 size 20m;
        severity dynamic;
        print-time yes;
        print-severity no;
        print-category no;
    };
    category queries { localnet_query_log; };
};
"""
    # Use b64 to safely append the logging block
    log_conf_b64 = base64.b64encode(logging_conf.encode()).decode()
    script = f"""#!/bin/bash
mkdir -p /var/log/named
chown bind:bind /var/log/named 2>/dev/null || chown named:named /var/log/named 2>/dev/null || true
chmod 755 /var/log/named

if ! grep -q 'localnet_query_log' /etc/bind/named.conf.local 2>/dev/null; then
    printf '%s' '{log_conf_b64}' | base64 -d >> /etc/bind/named.conf.local
    echo "Logging config appended to named.conf.local."
else
    echo "Logging config already present — skipping."
fi

named-checkconf && systemctl reload named
echo "✔ BIND9 query logging enabled — queries will appear in {QUERY_LOG_PATH}"
"""
    run_script(script, "Enable BIND9 query logging", backup=False)
    start_device_tracking()
    return jsonify({"ok": True, "tracking": True})

@app.route('/api/devices/tracking/disable', methods=['POST'])
def api_devices_tracking_disable():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    stop_device_tracking()
    script = """#!/bin/bash
sed -i '/localnet_query_log/,/^};$/d' /etc/bind/named.conf.local 2>/dev/null || true
named-checkconf && systemctl reload named 2>/dev/null || true
echo "✔ BIND9 query logging disabled"
"""
    run_script(script, "Disable BIND9 query logging", backup=False)
    return jsonify({"ok": True, "tracking": False})

@app.route('/api/devices/tracking/status', methods=['GET'])
def api_devices_tracking_status():
    query_log_exists = QUERY_LOG_PATH.exists()
    conf_has_logging = False
    for p in [Path("/etc/bind/named.conf.local"), Path("/etc/bind/named.conf")]:
        try:
            if "localnet_query_log" in p.read_text():
                conf_has_logging = True
                break
        except Exception:
            pass

    # Diagnostic info about the log file
    log_info: dict = {"size_bytes": 0, "line_count": 0, "last_line": ""}
    if query_log_exists:
        try:
            stat = QUERY_LOG_PATH.stat()
            log_info["size_bytes"] = stat.st_size
            with open(QUERY_LOG_PATH, "r", errors="replace") as f:
                lines = f.readlines()
            log_info["line_count"] = len(lines)
            # Return the last non-empty line as a sample
            for line in reversed(lines):
                if line.strip():
                    log_info["last_line"] = line.strip()[:200]
                    break
        except Exception:
            pass

    return jsonify({
        "tracking_active":  _tracking_active,
        "conf_has_logging": conf_has_logging,
        "query_log_exists": query_log_exists,
        "query_log_path":   str(QUERY_LOG_PATH),
        "log_info":         log_info,
    })

@app.route('/api/devices/scan', methods=['POST'])
def api_devices_scan():
    """Manual one-shot scan: query log + ARP + DHCP."""
    with _device_scan_lock:
        new_devs, upd_devs = scan_query_log()
    msg = f"Scan complete — {new_devs} new, {upd_devs} updated"
    log(msg, "success" if new_devs else "info")
    return jsonify({"ok": True, "new": new_devs, "updated": upd_devs})

# ─── API: DHCP ────────────────────────────────────────────────────────────────
@app.route('/api/dhcp/install', methods=['POST'])
def api_dhcp_install():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data    = request.json or {}
    cfg     = load_config()
    ip      = data.get('server_ip') or cfg.get('server_ip') or get_local_ip()
    domain  = cfg['domain']
    parts   = ip.split('.')
    subnet  = f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    netmask = "255.255.255.0"
    router  = data.get('router', f"{parts[0]}.{parts[1]}.{parts[2]}.1")
    range_s = data.get('range_start', f"{parts[0]}.{parts[1]}.{parts[2]}.100")
    range_e = data.get('range_end',   f"{parts[0]}.{parts[1]}.{parts[2]}.200")
    lease   = data.get('lease_time', 3600)

    dhcp_conf = f"""# LocalNet managed DHCP config
default-lease-time {lease};
max-lease-time {lease * 2};
authoritative;

subnet {subnet} netmask {netmask} {{
    range {range_s} {range_e};
    option domain-name-servers {ip};
    option domain-name "{domain}";
    option routers {router};
    option broadcast-address {parts[0]}.{parts[1]}.{parts[2]}.255;
    default-lease-time {lease};
    max-lease-time {lease * 2};
}}
"""
    script = f"""#!/bin/bash
set -e
echo "[1/3] Installing isc-dhcp-server..."
apt-get update -qq && apt-get install -y isc-dhcp-server

echo "[2/3] Writing DHCP config..."
{b64w('/etc/dhcp/dhcpd.conf', dhcp_conf)}

echo "[3/3] Starting DHCP server..."
systemctl enable isc-dhcp-server
systemctl restart isc-dhcp-server
echo "✔ DHCP server running — range: {range_s} – {range_e}"
echo "  DNS: {ip}   Domain: {domain}   Router: {router}"
"""
    run_script(script, "Install DHCP server")
    return jsonify({"ok": True})

@app.route('/api/dhcp/remove', methods=['POST'])
def api_dhcp_remove():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
systemctl stop isc-dhcp-server 2>/dev/null || true
systemctl disable isc-dhcp-server 2>/dev/null || true
apt-get purge -y isc-dhcp-server 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true
echo "✔ DHCP server removed"
"""
    run_script(script, "Remove DHCP server")
    return jsonify({"ok": True})

@app.route('/api/dhcp/leases')
def api_dhcp_leases():
    leases = []
    lease_file = Path("/var/lib/dhcp/dhcpd.leases")
    if not lease_file.exists():
        return jsonify([])
    try:
        text = lease_file.read_text()
        blocks = re.findall(r'lease ([\d.]+) \{([^}]+)\}', text, re.DOTALL)
        seen = {}
        for ip, body in blocks:
            mac_m    = re.search(r'hardware ethernet ([0-9a-f:]+);', body)
            host_m   = re.search(r'client-hostname "([^"]+)";', body)
            start_m  = re.search(r'starts \d+ ([^;]+);', body)
            end_m    = re.search(r'ends \d+ ([^;]+);', body)
            bind_m   = re.search(r'binding state (\w+);', body)
            state    = bind_m.group(1) if bind_m else 'unknown'
            seen[ip] = {
                "ip":       ip,
                "mac":      mac_m.group(1)  if mac_m    else '',
                "hostname": host_m.group(1) if host_m   else '',
                "starts":   start_m.group(1) if start_m else '',
                "ends":     end_m.group(1)   if end_m   else '',
                "state":    state,
            }
        leases = [v for v in seen.values() if v['state'] == 'active']
    except Exception as e:
        log(f"Lease parse error: {e}", "error")
    return jsonify(leases)

@app.route('/api/dhcp/status')
def api_dhcp_status():
    try:
        r = subprocess.run(['systemctl','is-active','isc-dhcp-server'],
                           capture_output=True, text=True, timeout=3)
        return jsonify({"active": r.stdout.strip() == "active"})
    except Exception:
        return jsonify({"active": False})

# ─── API: Ad Blocking ─────────────────────────────────────────────────────────
@app.route('/api/adblock/enable', methods=['POST'])
def api_adblock_enable():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    cfg    = load_config()
    domain = cfg['domain']
    script = fr"""#!/bin/bash
set -e
echo "[1/4] Downloading StevenBlack hosts list..."
mkdir -p /etc/bind/adblock
wget -qO /tmp/sb_hosts.txt https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts

echo "[2/4] Building BIND9 RPZ zone..."
cat > /etc/bind/adblock/db.rpz.adblock << 'RPZHDR'
$TTL 60
@   IN  SOA localhost. root.localhost. (
    $(date +%s) 3600 900 604800 60)
    IN  NS  localhost.
RPZHDR

grep '^0\.0\.0\.0 ' /tmp/sb_hosts.txt | \
    awk '{{print $2}}' | \
    grep -v '^0\.0\.0\.0$' | \
    sort -u | \
    while read d; do
        echo "$d    CNAME ."
        echo "*.$d  CNAME ."
    done >> /etc/bind/adblock/db.rpz.adblock

COUNT=$(grep -c 'CNAME' /etc/bind/adblock/db.rpz.adblock || echo 0)
echo "  Generated $COUNT RPZ entries"

echo "[3/4] Adding RPZ zone to BIND9..."
# Add to named.conf.local if not already present
grep -q 'rpz.adblock' /etc/bind/named.conf.local 2>/dev/null || cat >> /etc/bind/named.conf.local << 'ZONEEOF'
zone "rpz.adblock" {{
    type master;
    file "/etc/bind/adblock/db.rpz.adblock";
}};
ZONEEOF

# Add response-policy to options if not present
if ! grep -q 'response-policy' /etc/bind/named.conf.options 2>/dev/null; then
    # Append response-policy before closing brace
    head -n -2 /etc/bind/named.conf.options > /tmp/_opts_tmp.txt
    echo '    response-policy {{ zone "rpz.adblock"; }};' >> /tmp/_opts_tmp.txt
    echo '}};' >> /tmp/_opts_tmp.txt
    mv /tmp/_opts_tmp.txt /etc/bind/named.conf.options
fi


echo "[4/4] Reloading BIND9..."
named-checkconf && systemctl reload named
rm -f /tmp/sb_hosts.txt
echo "✔ Ad blocking enabled"
"""
    run_script(script, "Enable ad blocking (StevenBlack)")
    cfg["adblock_enabled"] = True
    save_config(cfg)
    return jsonify({"ok": True})

@app.route('/api/adblock/disable', methods=['POST'])
def api_adblock_disable():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
# Remove RPZ zone declaration
sed -i '/rpz.adblock/,/^};$/d' /etc/bind/named.conf.local 2>/dev/null || true
# Remove response-policy line from options
sed -i '/response-policy.*rpz.adblock/d' /etc/bind/named.conf.options 2>/dev/null || true
rm -rf /etc/bind/adblock
named-checkconf && systemctl reload named
echo "✔ Ad blocking disabled"
"""
    run_script(script, "Disable ad blocking")
    cfg = load_config()
    cfg["adblock_enabled"] = False
    save_config(cfg)
    return jsonify({"ok": True})

@app.route('/api/adblock/status')
def api_adblock_status():
    cfg = load_config()
    rpz = Path("/etc/bind/adblock/db.rpz.adblock")
    count = 0
    if rpz.exists():
        try:
            count = rpz.read_text().count("CNAME")
        except Exception:
            pass
    return jsonify({"enabled": cfg.get("adblock_enabled", False), "entry_count": count})

# ─── API: Backups ─────────────────────────────────────────────────────────────
@app.route('/api/backups')
def api_list_backups():
    bkps = db_list_backups()
    # Also scan dir in case DB is out of sync
    if BACKUP_DIR.exists():
        paths_in_db = {b['path'] for b in bkps}
        for f in sorted(BACKUP_DIR.glob("*.zip"), reverse=True)[:20]:
            if str(f) not in paths_in_db:
                bkps.append({"path": str(f), "label": f.stem, "created_at": ""})
    return jsonify(bkps)

@app.route('/api/backups/create', methods=['POST'])
def api_create_backup():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    label = (request.json or {}).get("label", "manual")
    path  = create_backup(label)
    return jsonify({"ok": bool(path), "path": path})

@app.route('/api/backups/restore', methods=['POST'])
def api_restore_backup():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    path = (request.json or {}).get("path", "")
    if not path or not Path(path).exists():
        return jsonify({"error": "Backup not found"}), 404
    ok = restore_backup(path)
    if ok:
        run_script("named-checkconf && systemctl restart named && systemctl restart nginx 2>/dev/null || true && echo '✔ Services restarted after restore'",
                   "Restart after restore", backup=False)
    return jsonify({"ok": ok})

@app.route('/api/backups/delete', methods=['POST'])
def api_delete_backup():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    path = (request.json or {}).get("path", "")
    try:
        Path(path).unlink(missing_ok=True)
        with db_connect() as con:
            con.execute("DELETE FROM backups WHERE path=?", (path,))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── API: System Logs (journalctl) ────────────────────────────────────────────
@app.route('/api/logs/journal')
def api_journal_stream():
    svc_map = {
        'bind9':   'named',
        'nginx':   'nginx',
        'dhcp':    'isc-dhcp-server',
        'resolved':'systemd-resolved',
        'system':  'localnet',
    }
    svc_key = request.args.get('service', 'bind9')
    svc = svc_map.get(svc_key, 'named')
    tail = request.args.get('tail', '100')

    def generate():
        try:
            proc = subprocess.Popen(
                ['journalctl', '-fu', svc, '--no-pager', '-n', str(tail), '--output=short'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            try:
                for line in proc.stdout:
                    payload = json.dumps({"msg": line.rstrip()})
                    yield f"data: {payload}\n\n"
            finally:
                proc.kill()
                proc.wait()
        except Exception as e:
            yield f"data: {json.dumps({'msg': f'Error: {e}'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )

# ─── API: Certbot / Let's Encrypt ────────────────────────────────────────────
@app.route('/api/ssl/certbot/install', methods=['POST'])
def api_certbot_install():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    script = """#!/bin/bash
set -e
echo "[1/2] Installing certbot..."
apt-get update -qq && apt-get install -y certbot python3-certbot-dns-rfc2136
echo "[2/2] certbot installed. Use the cert generation form to issue certificates."
echo "✔ Certbot ready"
"""
    run_script(script, "Install Certbot", backup=False)
    return jsonify({"ok": True})

@app.route('/api/ssl/certbot/cert', methods=['POST'])
def api_certbot_cert():
    if not is_root():
        return jsonify({"error": "Root required"}), 403
    data    = request.json or {}
    email   = data.get('email','').strip()
    domain  = data.get('domain','').strip()
    cfg     = load_config()
    server_ip = cfg.get('server_ip') or get_local_ip()
    if not email or not domain:
        return jsonify({"error": "Email and domain required"}), 400

    # TSIG key for DNS-01 challenge via BIND9
    tsig_script = f"""#!/bin/bash
set -e
echo "[1/4] Generating TSIG key for DNS-01..."
mkdir -p /etc/localnet/certbot
tsig-keygen localnet-certbot-key > /etc/localnet/certbot/tsig.key
KEY_SECRET=$(grep secret /etc/localnet/certbot/tsig.key | awk '{{print $2}}' | tr -d '";')

echo "[2/4] Writing rfc2136.ini..."
cat > /etc/localnet/certbot/rfc2136.ini << RFCEOF
dns_rfc2136_server = {server_ip}
dns_rfc2136_port = 53
dns_rfc2136_name = localnet-certbot-key
dns_rfc2136_secret = $KEY_SECRET
dns_rfc2136_algorithm = HMAC-SHA256
RFCEOF
chmod 600 /etc/localnet/certbot/rfc2136.ini

echo "[3/4] Requesting certificate for {domain}..."
certbot certonly \
    --dns-rfc2136 \
    --dns-rfc2136-credentials /etc/localnet/certbot/rfc2136.ini \
    --email {email} \
    --agree-tos \
    --non-interactive \
    -d "{domain}"

echo "[4/4] Certificate issued!"
echo "  Cert: /etc/letsencrypt/live/{domain}/fullchain.pem"
echo "  Key:  /etc/letsencrypt/live/{domain}/privkey.pem"
echo "✔ Let's Encrypt cert ready — globally browser-trusted."
"""
    run_script(tsig_script, f"Certbot cert: {domain}", backup=False)
    return jsonify({"ok": True})

@app.route('/api/ssl/letsencrypt/certs')
def api_le_certs():
    certs = []
    le_dir = Path("/etc/letsencrypt/live")
    if le_dir.exists():
        for d in le_dir.iterdir():
            if d.is_dir() and not d.name.startswith("README"):
                cert_f = d / "fullchain.pem"
                key_f  = d / "privkey.pem"
                certs.append({
                    "name": d.name,
                    "cert": str(cert_f),
                    "key":  str(key_f),
                    "exists": cert_f.exists(),
                })
    return jsonify(certs)

# ─── Proxy Notes ──────────────────────────────────────────────────────────────
@app.route('/api/nginx/notes', methods=['POST'])
def api_set_proxy_note():
    data = request.json or {}
    db_set_note("proxy_notes", "domain", data.get("domain",""), data.get("note",""))
    return jsonify({"ok": True})

@app.route('/')
def index():
    return HTML_PAGE

# ─── Frontend ─────────────────────────────────────────────────────────────────
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LocalNet Manager</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg0:     #080b11;
  --bg1:     #0d1018;
  --bg2:     #121620;
  --bg3:     #181d2a;
  --bg4:     #1e2435;
  --border:  #232b3e;
  --border2: #2d3850;
  --text:    #c2ceea;
  --dim:     #4e5d7a;
  --dim2:    #374158;
  --blue:    #4a9eff;
  --cyan:    #00d4ff;
  --green:   #00e676;
  --amber:   #ffb300;
  --red:     #ff4d6a;
  --purple:  #a78bfa;
  --teal:    #34d399;
  --font:    'Barlow', sans-serif;
  --mono:    'Fira Code', monospace;
  --cond:    'Barlow Condensed', sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }
body { background: var(--bg0); color: var(--text); font-family: var(--font); font-size: 14px; display: flex; flex-direction: column; }

/* ─── Layout ─────────────────────────────────────── */
#app { display: flex; flex: 1; overflow: hidden; }
#sidebar {
  width: 210px; min-width: 210px;
  background: var(--bg1);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  user-select: none;
}
#main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#topbar {
  height: 52px; min-height: 52px;
  background: var(--bg1);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 24px;
  gap: 12px;
}
#content { flex: 1; overflow-y: auto; padding: 28px 28px 12px; }
#log-panel {
  height: 190px; min-height: 190px;
  background: var(--bg0);
  border-top: 1px solid var(--border);
  display: flex; flex-direction: column;
  transition: height .25s ease;
}
#log-panel.collapsed { height: 34px; min-height: 34px; }

/* ─── Sidebar ────────────────────────────────────── */
.sidebar-logo {
  padding: 20px 18px 14px;
  border-bottom: 1px solid var(--border);
}
.logo-mark {
  font-family: var(--cond); font-size: 20px; font-weight: 700;
  color: var(--cyan); letter-spacing: .5px;
  display: flex; align-items: center; gap: 8px;
}
.logo-hex { font-size: 22px; }
.logo-sub { font-size: 10px; color: var(--dim); font-family: var(--mono); letter-spacing: 2px; margin-top: 2px; }

.nav-section { padding: 10px 0; flex: 1; }
.nav-label { font-size: 10px; font-weight: 600; color: var(--dim); letter-spacing: 2px; font-family: var(--cond); padding: 8px 18px 4px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 18px; cursor: pointer;
  color: var(--dim); font-size: 13.5px; font-weight: 500;
  border-left: 2px solid transparent;
  transition: all .15s;
}
.nav-item:hover { color: var(--text); background: var(--bg2); }
.nav-item.active { color: var(--cyan); border-left-color: var(--cyan); background: rgba(0,212,255,.06); }
.nav-icon { font-size: 15px; width: 18px; text-align: center; }

.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid var(--border);
  font-size: 11px; color: var(--dim);
  display: flex; align-items: center; justify-content: space-between;
}
.root-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--dim2); display: inline-block; margin-right: 6px; }
.root-dot.ok { background: var(--green); box-shadow: 0 0 6px var(--green); }

/* ─── Topbar ─────────────────────────────────────── */
#page-title { font-family: var(--cond); font-size: 18px; font-weight: 600; color: var(--text); flex: 1; }
.chip {
  padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: 600;
  font-family: var(--mono); letter-spacing: .5px;
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--dim);
}
.chip.up   { color: var(--green); border-color: rgba(0,230,118,.3); background: rgba(0,230,118,.06); }
.chip.down { color: var(--red);   border-color: rgba(255,77,106,.3); background: rgba(255,77,106,.06); }

/* ─── Cards ──────────────────────────────────────── */
.card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 6px; padding: 20px 22px; margin-bottom: 18px;
}
.card-title {
  font-family: var(--cond); font-size: 15px; font-weight: 600;
  color: var(--text); margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.card-title .ct-icon { font-size: 17px; }
.card-sub { font-size: 12px; color: var(--dim); margin-bottom: 16px; line-height: 1.6; }

.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 18px; }

/* service status cards */
.svc-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 6px; padding: 18px 20px;
  display: flex; align-items: center; gap: 14px;
}
.svc-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--dim2); flex-shrink: 0;
  transition: background .3s, box-shadow .3s;
}
.svc-dot.active { background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 2s infinite; }
.svc-dot.inactive { background: var(--dim2); }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

.svc-info { flex: 1; }
.svc-name { font-weight: 600; font-size: 13px; margin-bottom: 2px; }
.svc-state { font-size: 11px; color: var(--dim); font-family: var(--mono); }
.svc-btn {
  padding: 4px 12px; font-size: 11px; border-radius: 3px;
  border: 1px solid var(--border2); background: transparent;
  color: var(--dim); cursor: pointer; font-family: var(--mono);
  transition: all .15s;
}
.svc-btn:hover { border-color: var(--cyan); color: var(--cyan); }

/* stat cards */
.stat-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 6px; padding: 18px 20px; text-align: center;
}
.stat-num { font-family: var(--cond); font-size: 36px; font-weight: 700; color: var(--cyan); line-height: 1; }
.stat-label { font-size: 11px; color: var(--dim); margin-top: 4px; letter-spacing: 1px; font-weight: 600; font-family: var(--cond); }

/* ─── Forms ──────────────────────────────────────── */
.form-row { display: flex; flex-direction: column; gap: 4px; margin-bottom: 14px; }
.form-row label { font-size: 11px; color: var(--dim); font-weight: 600; letter-spacing: .8px; font-family: var(--cond); }
input, select, textarea {
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--text); font-family: var(--mono); font-size: 13px;
  padding: 8px 12px; border-radius: 4px; outline: none;
  transition: border-color .15s;
  width: 100%;
}
input:focus, select:focus, textarea:focus { border-color: var(--cyan); }
input::placeholder { color: var(--dim2); }
textarea { min-height: 80px; resize: vertical; }
select option { background: var(--bg3); }

.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }

/* toggle */
.toggle-wrap { display: flex; align-items: center; gap: 10px; }
.toggle {
  position: relative; width: 40px; height: 22px;
  background: var(--bg4); border: 1px solid var(--border2);
  border-radius: 11px; cursor: pointer; transition: background .2s;
  flex-shrink: 0;
}
.toggle.on { background: var(--cyan); border-color: var(--cyan); }
.toggle::after {
  content: ''; position: absolute;
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--dim); top: 2px; left: 2px;
  transition: transform .2s, background .2s;
}
.toggle.on::after { transform: translateX(18px); background: var(--bg0); }
.toggle-label { font-size: 13px; color: var(--text); }
.toggle-desc { font-size: 11px; color: var(--dim); }

/* ─── Buttons ────────────────────────────────────── */
.btn-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }
button, .btn {
  padding: 8px 18px; border-radius: 4px; font-family: var(--font);
  font-size: 13px; font-weight: 500; cursor: pointer;
  border: none; transition: all .15s; white-space: nowrap;
}
.btn-primary { background: var(--blue); color: #fff; }
.btn-primary:hover { background: #5aadff; }
.btn-success { background: rgba(0,230,118,.15); color: var(--green); border: 1px solid rgba(0,230,118,.3); }
.btn-success:hover { background: rgba(0,230,118,.25); }
.btn-danger  { background: rgba(255,77,106,.12); color: var(--red); border: 1px solid rgba(255,77,106,.3); }
.btn-danger:hover  { background: rgba(255,77,106,.22); }
.btn-ghost  { background: transparent; color: var(--dim); border: 1px solid var(--border); }
.btn-ghost:hover  { border-color: var(--border2); color: var(--text); }
.btn-amber  { background: rgba(255,179,0,.12); color: var(--amber); border: 1px solid rgba(255,179,0,.3); }
.btn-amber:hover  { background: rgba(255,179,0,.22); }
button:disabled { opacity: .4; cursor: not-allowed; }

/* ─── Tabs ───────────────────────────────────────── */
.tabs { display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
.tab {
  padding: 10px 20px; font-size: 13px; font-weight: 500;
  color: var(--dim); cursor: pointer; border-bottom: 2px solid transparent;
  transition: all .15s; margin-bottom: -1px;
}
.tab:hover { color: var(--text); }
.tab.active { color: var(--cyan); border-bottom-color: var(--cyan); }

/* ─── Table ──────────────────────────────────────── */
.tbl-wrap { overflow-x: auto; border-radius: 6px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
thead tr { background: var(--bg3); }
th { padding: 10px 14px; text-align: left; font-size: 10px; font-weight: 700; color: var(--dim); letter-spacing: 1.5px; font-family: var(--cond); border-bottom: 1px solid var(--border); }
td { padding: 10px 14px; font-size: 13px; border-bottom: 1px solid var(--border); }
tr:last-child td { border-bottom: none; }
tbody tr:hover { background: rgba(255,255,255,.02); }
.mono { font-family: var(--mono); font-size: 12px; }
.type-badge {
  display: inline-block; padding: 2px 7px; border-radius: 3px;
  font-size: 10px; font-weight: 700; font-family: var(--mono);
}
.type-A    { background: rgba(74,158,255,.15); color: var(--blue); }
.type-CNAME{ background: rgba(167,139,250,.15); color: var(--purple); }
.type-MX   { background: rgba(255,179,0,.15);   color: var(--amber); }
.tmpl-badge {
  display: inline-block; padding: 2px 8px; border-radius: 3px;
  font-size: 10px; font-weight: 600; font-family: var(--cond);
}
.tmpl-basic        { background: rgba(74,158,255,.15); color: var(--blue); }
.tmpl-websocket    { background: rgba(167,139,250,.15); color: var(--purple); }
.tmpl-homeassistant{ background: rgba(52,211,153,.15);  color: var(--teal); }
.tmpl-nextcloud    { background: rgba(96,165,250,.15);  color: #60a5fa; }
.tmpl-loadbalancer { background: rgba(251,191,36,.15);  color: var(--amber); }

.del-btn {
  padding: 3px 10px; font-size: 11px; border-radius: 3px;
  background: transparent; border: 1px solid rgba(255,77,106,.25);
  color: rgba(255,77,106,.7); cursor: pointer; font-family: var(--mono);
  transition: all .15s;
}
.del-btn:hover { background: rgba(255,77,106,.12); color: var(--red); border-color: var(--red); }

/* ─── Template Cards ─────────────────────────────── */
.tmpl-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.tmpl-card {
  background: var(--bg3); border: 2px solid var(--border);
  border-radius: 6px; padding: 14px 16px; cursor: pointer;
  transition: all .15s;
}
.tmpl-card:hover { border-color: var(--border2); }
.tmpl-card.selected { border-color: var(--cyan); background: rgba(0,212,255,.05); }
.tmpl-card-icon { font-size: 22px; margin-bottom: 6px; }
.tmpl-card-name { font-weight: 600; font-size: 13px; margin-bottom: 3px; }
.tmpl-card-desc { font-size: 11px; color: var(--dim); line-height: 1.5; }

/* ─── VPN Diagram ────────────────────────────────── */
.vpn-diagram {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 6px; padding: 16px 20px; margin: 14px 0;
  font-family: var(--mono); font-size: 12px; line-height: 1.9;
}
.vpn-diagram .green { color: var(--green); }
.vpn-diagram .dim   { color: var(--dim); }
.vpn-diagram .cyan  { color: var(--cyan); }
.vpn-diagram .red   { color: var(--red); }

/* ─── Log Panel ──────────────────────────────────── */
#log-header {
  display: flex; align-items: center; padding: 0 14px;
  height: 34px; min-height: 34px;
  border-bottom: 1px solid var(--border); gap: 10px;
}
.log-title { font-family: var(--mono); font-size: 10px; font-weight: 500; color: var(--dim); letter-spacing: 2px; flex: 1; }
.log-toggle-btn, .log-clear-btn {
  padding: 2px 10px; font-size: 11px; background: transparent;
  border: 1px solid var(--border); border-radius: 3px; color: var(--dim);
  cursor: pointer; font-family: var(--mono);
}
.log-toggle-btn:hover, .log-clear-btn:hover { color: var(--text); border-color: var(--border2); }
#log-body { flex: 1; overflow-y: auto; padding: 8px 14px; }
.log-line { font-family: var(--mono); font-size: 12px; line-height: 1.7; display: flex; gap: 10px; }
.log-time { color: var(--dim2); flex-shrink: 0; }
.log-msg { white-space: pre-wrap; word-break: break-all; }
.log-line.info    .log-msg { color: #8899bb; }
.log-line.success .log-msg { color: var(--green); }
.log-line.error   .log-msg { color: var(--red); }
.log-line.warn    .log-msg { color: var(--amber); }

/* ─── Toast ──────────────────────────────────────── */
#toasts { position: fixed; bottom: 210px; right: 20px; z-index: 100; display: flex; flex-direction: column; gap: 8px; }
.toast {
  padding: 10px 16px; border-radius: 5px; font-size: 13px; font-weight: 500;
  background: var(--bg3); border: 1px solid var(--border);
  animation: slideIn .2s ease; max-width: 320px;
}
.toast.success { border-color: rgba(0,230,118,.4); color: var(--green); }
.toast.error   { border-color: rgba(255,77,106,.4); color: var(--red); }
.toast.info    { border-color: rgba(0,212,255,.4);  color: var(--cyan); }
@keyframes slideIn { from{transform:translateX(20px);opacity:0} to{transform:translateX(0);opacity:1} }

/* ─── Misc ───────────────────────────────────────── */
.section-title { font-family: var(--cond); font-size: 16px; font-weight: 600; color: var(--text); margin-bottom: 14px; }
.inline-code { font-family: var(--mono); font-size: 12px; background: var(--bg3); padding: 2px 7px; border-radius: 3px; border: 1px solid var(--border); }
.text-dim { color: var(--dim); }
.text-green { color: var(--green); }
.text-red   { color: var(--red); }
.divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
.resolv-preview { font-family: var(--mono); font-size: 11px; color: var(--dim); background: var(--bg3); padding: 12px 14px; border-radius: 4px; border: 1px solid var(--border); white-space: pre-wrap; line-height: 1.7; }
.resolv-preview .hl { color: var(--green); }
.empty-state { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 13px; }
.empty-icon { font-size: 36px; margin-bottom: 10px; }
#content::-webkit-scrollbar { width: 5px; }
#content::-webkit-scrollbar-track { background: transparent; }
#content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
#log-body::-webkit-scrollbar { width: 4px; }
#log-body::-webkit-scrollbar-thumb { background: var(--border); }
.dig-result { font-family: var(--mono); font-size: 13px; color: var(--green); background: var(--bg3); padding: 10px 14px; border-radius: 4px; border: 1px solid var(--border); min-height: 36px; margin-top: 10px; }
.info-box { background: rgba(0,212,255,.05); border: 1px solid rgba(0,212,255,.2); border-radius: 5px; padding: 12px 16px; font-size: 12px; line-height: 1.7; color: var(--dim); margin: 12px 0; }
.info-box strong { color: var(--cyan); }
.cert-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--bg3); border-radius: 4px; border: 1px solid var(--border); margin-bottom: 8px; }
.cert-name { font-family: var(--mono); font-size: 12px; color: var(--green); }
.cert-path { font-family: var(--mono); font-size: 11px; color: var(--dim); }
/* ─── Journal Viewer ─────────────────────────────── */
#journal-box {
  background: var(--bg0); border: 1px solid var(--border);
  border-radius: 4px; font-family: var(--mono); font-size: 11.5px;
  color: #7ecf9f; padding: 12px 14px; height: 320px;
  overflow-y: auto; line-height: 1.7; white-space: pre-wrap; word-break: break-all;
}
#journal-box::-webkit-scrollbar { width: 4px; }
#journal-box::-webkit-scrollbar-thumb { background: var(--border); }
.jline-err  { color: var(--red); }
.jline-warn { color: var(--amber); }
.jline-ok   { color: var(--green); }
/* ─── Adblock ────────────────────────────────────── */
.adblock-hero {
  text-align: center; padding: 28px 20px;
  background: var(--bg3); border-radius: 6px;
  border: 1px solid var(--border); margin-bottom: 18px;
}
.adblock-count { font-family: var(--cond); font-size: 52px; font-weight: 700; color: var(--green); line-height: 1; }
.adblock-label { font-size: 12px; color: var(--dim); margin-top: 4px; letter-spacing: 1px; font-family: var(--cond); }
/* ─── Backup rows ────────────────────────────────── */
.backup-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; background: var(--bg3);
  border-radius: 4px; border: 1px solid var(--border); margin-bottom: 6px;
}
.backup-row-info { flex: 1; }
.backup-name { font-family: var(--mono); font-size: 12px; color: var(--text); }
.backup-date { font-size: 11px; color: var(--dim); margin-top: 2px; }
/* ─── DHCP Leases ────────────────────────────────── */
.lease-active { color: var(--green); }
.lease-expired { color: var(--dim); }
/* ─── Password Form ──────────────────────────────── */
.pw-card { max-width: 420px; }
</style>
</head>
<body>

<div id="app">
  <aside id="sidebar">
    <div class="sidebar-logo">
      <div class="logo-mark"><span class="logo-hex">⥯</span> LocalNet</div>
      <div class="logo-sub">v4 &nbsp;·&nbsp; MANAGER</div>
    </div>
    <div class="nav-section" style="overflow-y:auto">
      <div class="nav-label">OVERVIEW</div>
      <div class="nav-item active" data-page="dashboard" onclick="navigate('dashboard')">
        <span class="nav-icon">◈</span> Dashboard
      </div>
      <div class="nav-label">SERVICES</div>
      <div class="nav-item" data-page="dns" onclick="navigate('dns')">
        <span class="nav-icon">◎</span> DNS
      </div>
      <div class="nav-item" data-page="nginx" onclick="navigate('nginx')">
        <span class="nav-icon">⇌</span> Nginx Proxy
      </div>
      <div class="nav-item" data-page="dhcp" onclick="navigate('dhcp')">
        <span class="nav-icon">⊹</span> DHCP
      </div>
      <div class="nav-item" data-page="ssl" onclick="navigate('ssl')">
        <span class="nav-icon">◉</span> SSL / TLS
      </div>
      <div class="nav-item" data-page="adblock" onclick="navigate('adblock')">
        <span class="nav-icon">⊘</span> Ad Blocking
      </div>
      <div class="nav-label">SYSTEM</div>
      <div class="nav-item" data-page="backups" onclick="navigate('backups')">
        <span class="nav-icon">⊟</span> Backups
      </div>
      <div class="nav-item" data-page="logs" onclick="navigate('logs')">
        <span class="nav-icon">≡</span> System Logs
      </div>
      <div class="nav-item" data-page="network" onclick="navigate('network')">
        <span class="nav-icon">⊞</span> Network
      </div>
      <div class="nav-item" data-page="settings" onclick="navigate('settings')">
        <span class="nav-icon">⊙</span> Settings
      </div>
    </div>
    <div class="sidebar-footer">
      <span><span class="root-dot" id="root-dot"></span><span id="root-label">checking...</span></span>
      <a href="/logout" style="font-family:var(--mono);font-size:10px;color:var(--dim);text-decoration:none" title="Logout">⏻ :8091</a>
    </div>
  </aside>

  <div id="main">
    <header id="topbar">
      <div id="page-title">Dashboard</div>
      <div style="display:flex;gap:8px;align-items:center" id="status-chips"></div>
    </header>
    <div id="content">
      <div class="empty-state"><div class="empty-icon">⬡</div>Loading...</div>
    </div>
  </div>
</div>

<div id="log-panel">
  <div id="log-header">
    <span class="log-title">OUTPUT LOG</span>
    <button class="log-clear-btn" onclick="clearLog()">Clear</button>
    <button class="log-toggle-btn" id="log-toggle-btn" onclick="toggleLog()">▼ Collapse</button>
  </div>
  <div id="log-body"></div>
</div>

<div id="toasts"></div>

<script>
// ─── State ────────────────────────────────────────────────────────────────
const S = {
  page: 'dashboard',
  status: {},
  cfg: {},
  logOpen: true,
  selectedTemplate: 'basic',
  activeTab: {},
};

// ─── API ──────────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = { method, headers: {'Content-Type':'application/json'} };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const r = await fetch('/api' + path, opts);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || 'API error');
  return j;
}

function toast(msg, type='info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

async function confirmAction(msg) {
  return window.confirm(msg);
}

// ─── Navigation ───────────────────────────────────────────────────────────
function navigate(page) {
  S.page = page;
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
  const titles = {
    dashboard:'Dashboard', dns:'DNS Server', nginx:'Nginx Proxy',
    dhcp:'DHCP Server', ssl:'SSL / TLS', adblock:'Ad Blocking',
    backups:'Backups & Restore', logs:'System Logs',
    network:'Network Interfaces', settings:'Settings'
  };
  document.getElementById('page-title').textContent = titles[page] || page;
  renderPage();
}

function renderPage() {
  const fns = {
    dashboard:pgDashboard, dns:pgDNS, nginx:pgNginx,
    dhcp:pgDHCP, ssl:pgSSL, adblock:pgAdBlock,
    backups:pgBackups, logs:pgLogs,
    network:pgNetwork, settings:pgSettings
  };
  const fn = fns[S.page];
  if (fn) fn();
}

// ─── Status Refresh ───────────────────────────────────────────────────────
async function refreshStatus() {
  try {
    S.status = await api('GET','/status');
    const svcs = S.status.services || {};
    const chips = document.getElementById('status-chips');
    if (chips) {
      chips.innerHTML = ['bind9','nginx'].map(s => {
        const up = svcs[s] === 'active';
        return `<span class="chip ${up?'up':'down'}">${s==='bind9'?'BIND9':'NGINX'} ${up?'▲':'▼'}</span>`;
      }).join('');
    }
    const dot = document.getElementById('root-dot');
    const lbl = document.getElementById('root-label');
    if (dot && lbl) {
      dot.className = 'root-dot' + (S.status.is_root ? ' ok' : '');
      lbl.textContent = S.status.is_root ? 'root' : 'no root';
    }
    if (S.page === 'dashboard') pgDashboard();
  } catch(e) {}
}

// ─── Log Panel ────────────────────────────────────────────────────────────
function addLog(entry) {
  if (entry.type === 'ping') return;
  const body = document.getElementById('log-body');
  if (!body) return;
  const line = document.createElement('div');
  line.className = `log-line ${entry.level||'info'}`;
  line.innerHTML = `<span class="log-time">${entry.t}</span><span class="log-msg">${escHtml(entry.msg)}</span>`;
  body.appendChild(line);
  if (body.children.length > 400) body.removeChild(body.firstChild);
  body.scrollTop = body.scrollHeight;
}
function clearLog() { document.getElementById('log-body').innerHTML = ''; }
function toggleLog() {
  S.logOpen = !S.logOpen;
  document.getElementById('log-panel').classList.toggle('collapsed', !S.logOpen);
  document.getElementById('log-toggle-btn').textContent = S.logOpen ? '▼ Collapse' : '▲ Expand';
  document.getElementById('toasts').style.bottom = S.logOpen ? '210px' : '50px';
}

// ─── SSE ──────────────────────────────────────────────────────────────────
(function initSSE() {
  const es = new EventSource('/api/logs/stream');
  es.onmessage = e => { try { addLog(JSON.parse(e.data)); } catch(err) {} };
  es.onerror   = () => setTimeout(initSSE, 5000);
})();

// ─── Helpers ─────────────────────────────────────────────────────────────
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function tabBar(id, tabs, active) {
  return `<div class="tabs">${tabs.map(([k,l]) => `<div class="tab ${k===active?'active':''}" onclick="setTab('${id}','${k}')">${l}</div>`).join('')}</div>`;
}
function setTab(id, tab) {
  S.activeTab[id] = tab;
  renderPage();
}
function getTab(id, def) { return S.activeTab[id] || def; }

function svcCard(name, key, label) {
  const svcs = S.status.services || {};
  const up = svcs[key] === 'active';
  return `
  <div class="svc-card">
    <div class="svc-dot ${up?'active':'inactive'}"></div>
    <div class="svc-info">
      <div class="svc-name">${name}</div>
      <div class="svc-state">${svcs[key]||'unknown'}</div>
    </div>
    <button class="svc-btn" onclick="reloadSvc('${key}')">↺ reload</button>
  </div>`;
}

async function reloadSvc(svc) {
  try {
    await api('POST','/service/reload',{service:svc});
    toast(`${svc} reload triggered`, 'info');
  } catch(e) { toast(e.message,'error'); }
}

// ─── Dashboard ────────────────────────────────────────────────────────────
function pgDashboard() {
  const st = S.status;
  const domain = st.domain || 'localnet';
  const resolv = (st.resolv||'').split('\\n').map(l=>{
    if(l.startsWith('nameserver')) return `<span style="color:var(--green)">${escHtml(l)}</span>`;
    if(l.startsWith('#')) return `<span style="color:var(--dim2)">${escHtml(l)}</span>`;
    return escHtml(l);
  }).join('\\n');

  document.getElementById('content').innerHTML = `
  <div class="grid-3">
    ${svcCard('BIND9 DNS','bind9','bind9')}
    ${svcCard('Nginx','nginx','nginx')}
    ${svcCard('systemd-resolved','systemd-resolved','resolved')}
  </div>
  <div class="grid-3">
    <div class="stat-card">
      <div class="stat-num">${st.record_count??'–'}</div>
      <div class="stat-label">DNS RECORDS</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">${st.proxy_count??'–'}</div>
      <div class="stat-label">NGINX PROXIES</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">${st.cert_count??'–'}</div>
      <div class="stat-label">SSL CERTS</div>
    </div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="ct-icon">◎</span> Active Domain</div>
      <div style="font-family:var(--mono);font-size:22px;color:var(--cyan);margin-bottom:6px">.${domain}</div>
      <div style="font-size:12px;color:var(--dim)">Server IP: <span style="color:var(--text)">${st.server_ip||'–'}</span></div>
      <div class="btn-row" style="margin-top:14px">
        <button class="btn btn-ghost" onclick="navigate('dns')">Manage DNS →</button>
        <button class="btn btn-ghost" onclick="navigate('nginx')">Manage Proxies →</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title"><span class="ct-icon">◉</span> /etc/resolv.conf</div>
      <div class="resolv-preview">${resolv||'<span style="color:var(--dim2)">Not readable</span>'}</div>
    </div>
  </div>`;
}

// ─── DNS Page ─────────────────────────────────────────────────────────────
async function pgDNS() {
  const tab = getTab('dns', 'setup');
  let html = tabBar('dns',[['setup','Setup'],['records','Records'],['test','Test']],tab);
  if (tab === 'setup') html += await dnsSetupHtml();
  else if (tab === 'records') html += await dnsRecordsHtml();
  else html += dnsTestHtml();
  document.getElementById('content').innerHTML = html;
  if (tab === 'setup') initDNSSetup();
  else if (tab === 'records') initDNSRecords();
  else initDNSTest();
}

async function dnsSetupHtml() {
  const cfg = await api('GET','/config');
  S.cfg = cfg;
  const ifaces = cfg.interfaces || [];
  const fwds = (cfg.forwarders||['1.1.1.2','1.0.0.2']).join(', ');
  const vpn = cfg.vpn_safe !== false;
  return `
  <div class="card">
    <div class="card-title"><span class="ct-icon">◎</span> BIND9 DNS Server</div>
    <div class="card-sub">Configure and install a local authoritative DNS server. The domain you set here becomes your private TLD — all devices on your LAN can resolve hostnames under it.</div>
    <div class="form-grid-3">
      <div class="form-row">
        <label>DOMAIN (TLD)</label>
        <input id="dns-domain" value="${escHtml(cfg.domain||'localnet')}" placeholder="localnet">
      </div>
      <div class="form-row">
        <label>SERVER IP</label>
        <select id="dns-ip">
          ${ifaces.map(i=>`<option value="${i.ip}" ${i.ip===cfg.server_ip?'selected':''}>${i.name} — ${i.ip}</option>`).join('')}
        </select>
      </div>
      <div class="form-row">
        <label>FORWARDERS (comma-separated)</label>
        <input id="dns-fwds" value="${escHtml(fwds)}" placeholder="1.1.1.2, 1.0.0.2">
      </div>
    </div>
    <div class="form-row">
      <label>VPN COMPATIBILITY</label>
      <div class="toggle-wrap">
        <div class="toggle ${vpn?'on':''}" id="vpn-toggle" onclick="toggleVPN()"></div>
        <div>
          <div class="toggle-label">VPN-compatible mode ${vpn?'<span style="color:var(--green)">ON</span>':'<span style="color:var(--dim)">OFF</span>'}</div>
          <div class="toggle-desc">Routes through systemd-resolved so VPN clients can still inject their own DNS</div>
        </div>
      </div>
    </div>
    <div class="vpn-diagram">
      <div><span class="cyan">resolv.conf</span> → <span class="green">127.0.0.53</span> (systemd-resolved stub)</div>
      <div class="dim">    ├── *.${escHtml(cfg.domain||'localnet')} → <span class="cyan">127.0.0.1</span> (BIND9)   <span class="green">✔ local names</span></div>
      <div class="dim">    └── everything else → upstream / VPN DNS          <span class="green">✔ VPN works</span></div>
    </div>
    <div class="btn-row">
      <button class="btn btn-primary" onclick="installDNS()">⬡ Install DNS Server</button>
      <button class="btn btn-danger" onclick="removeDNS()">✕ Remove DNS</button>
    </div>
  </div>`;
}

let vpnState = true;
function toggleVPN() {
  vpnState = !vpnState;
  const el = document.getElementById('vpn-toggle');
  if (el) el.className = 'toggle ' + (vpnState?'on':'');
}
function initDNSSetup() {
  vpnState = S.cfg.vpn_safe !== false;
}
async function installDNS() {
  if (!await confirmAction('Install BIND9 DNS server? This will modify system network configuration.')) return;
  const domain = document.getElementById('dns-domain')?.value?.trim();
  const ip     = document.getElementById('dns-ip')?.value;
  const fwdRaw = document.getElementById('dns-fwds')?.value || '1.1.1.2, 1.0.0.2';
  const fwds   = fwdRaw.split(',').map(s=>s.trim()).filter(Boolean);
  try {
    await api('POST','/dns/install',{domain,server_ip:ip,vpn_safe:vpnState,forwarders:fwds});
    toast('DNS install started — watch the log', 'info');
  } catch(e) { toast(e.message,'error'); }
}
async function removeDNS() {
  if (!await confirmAction('Completely remove BIND9 and all DNS configuration?')) return;
  try {
    await api('POST','/dns/remove');
    toast('DNS removal started', 'info');
  } catch(e) { toast(e.message,'error'); }
}

async function dnsRecordsHtml() {
  let records = [];
  try { records = await api('GET','/dns/records'); } catch(e) {}
  const rows = records.length
    ? records.map(r=>`
      <tr>
        <td class="mono">${escHtml(r.host)}</td>
        <td><span class="type-badge type-${r.type}">${r.type}</span></td>
        <td class="mono">${escHtml(r.value)}</td>
        <td><button class="del-btn" onclick="removeRecord('${escHtml(r.host)}')">✕</button></td>
      </tr>`).join('')
    : `<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">◎</div>No records yet. DNS may not be installed.</div></td></tr>`;
  return `
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Add A Record</div>
      <div class="form-grid-2">
        <div class="form-row"><label>HOSTNAME</label><input id="a-host" placeholder="nas"></div>
        <div class="form-row"><label>IP ADDRESS</label><input id="a-ip" placeholder="192.168.1.20"></div>
      </div>
      <button class="btn btn-primary" onclick="addA()">+ Add A Record</button>
    </div>
    <div class="card">
      <div class="card-title">Add CNAME</div>
      <div class="form-grid-2">
        <div class="form-row"><label>ALIAS</label><input id="cn-alias" placeholder="movies"></div>
        <div class="form-row"><label>TARGET HOST</label><input id="cn-target" placeholder="ns1"></div>
      </div>
      <button class="btn btn-primary" onclick="addCname()">+ Add CNAME</button>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Zone Records</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>HOSTNAME</th><th>TYPE</th><th>VALUE</th><th></th></tr></thead>
        <tbody id="records-tbody">${rows}</tbody>
      </table>
    </div>
  </div>`;
}
function initDNSRecords() {}

async function addA() {
  const host = document.getElementById('a-host')?.value?.trim();
  const ip   = document.getElementById('a-ip')?.value?.trim();
  if (!host || !ip) { toast('Enter hostname and IP','error'); return; }
  try {
    await api('POST','/dns/records/a',{host,ip});
    toast(`Adding ${host} → ${ip}`, 'info');
    setTimeout(()=>{ S.activeTab['dns']='records'; pgDNS(); }, 1800);
  } catch(e) { toast(e.message,'error'); }
}
async function addCname() {
  const alias  = document.getElementById('cn-alias')?.value?.trim();
  const target = document.getElementById('cn-target')?.value?.trim();
  if (!alias || !target) { toast('Enter alias and target','error'); return; }
  try {
    await api('POST','/dns/records/cname',{alias,target});
    toast(`Adding CNAME ${alias} → ${target}`, 'info');
    setTimeout(()=>{ S.activeTab['dns']='records'; pgDNS(); }, 1800);
  } catch(e) { toast(e.message,'error'); }
}
async function removeRecord(host) {
  if (!await confirmAction(`Remove all records for '${host}'?`)) return;
  try {
    await api('DELETE',`/dns/records/${host}`);
    toast(`Removed ${host}`, 'info');
    setTimeout(()=>pgDNS(), 1500);
  } catch(e) { toast(e.message,'error'); }
}

function dnsTestHtml() {
  return `
  <div class="card">
    <div class="card-title">DNS Lookup Test</div>
    <div class="card-sub">Run a dig query against your BIND9 server to verify records resolve correctly.</div>
    <div class="form-grid-2">
      <div class="form-row"><label>LOOKUP NAME</label><input id="test-name" placeholder="nas.localnet"></div>
      <div class="form-row"><label>DNS SERVER IP</label><input id="test-server" placeholder="${S.status.server_ip||'auto'}"></div>
    </div>
    <button class="btn btn-amber" onclick="runTest()">↗ Run Lookup</button>
    <div class="dig-result" id="dig-result" style="display:none"></div>
  </div>`;
}
function initDNSTest() {}
async function runTest() {
  const name   = document.getElementById('test-name')?.value?.trim();
  const server = document.getElementById('test-server')?.value?.trim() || undefined;
  if (!name) { toast('Enter a hostname to test','error'); return; }
  const res = document.getElementById('dig-result');
  res.style.display = 'block';
  res.textContent = 'querying...';
  try {
    const r = await api('POST','/dns/test',{name,server});
    res.textContent = r.result;
    res.style.color = r.ok ? 'var(--green)' : 'var(--amber)';
  } catch(e) { res.textContent = e.message; res.style.color='var(--red)'; }
}

// ─── Nginx Page ───────────────────────────────────────────────────────────
async function pgNginx() {
  const tab = getTab('nginx','proxies');
  let html = tabBar('nginx',[['proxies','Proxies'],['add','Add Proxy'],['manage','Install / Remove']],tab);
  if (tab === 'proxies') html += await nginxProxiesHtml();
  else if (tab === 'add') html += nginxAddHtml();
  else html += nginxManageHtml();
  document.getElementById('content').innerHTML = html;
  if (tab === 'add') initNginxAdd();
}

async function nginxProxiesHtml() {
  let proxies = [];
  try { proxies = await api('GET','/nginx/proxies'); } catch(e) {}
  const rows = proxies.length
    ? proxies.map(p=>`
      <tr>
        <td class="mono">${escHtml(p.domain)}</td>
        <td class="mono">:${p.port}</td>
        <td><span class="tmpl-badge tmpl-${p.template}">${p.template}</span></td>
        <td><button class="del-btn" onclick="removeProxy('${escHtml(p.domain)}')">✕</button></td>
      </tr>`).join('')
    : `<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">⇌</div>No proxies configured.</div></td></tr>`;
  return `
  <div class="card">
    <div class="card-title">Active Proxies</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>DOMAIN</th><th>PORT</th><th>TEMPLATE</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <div class="btn-row" style="margin-top:16px">
      <button class="btn btn-primary" onclick="setTab('nginx','add');pgNginx()">+ Add Proxy</button>
    </div>
  </div>`;
}

const TMPL_INFO = {
  basic:         {icon:'⇌',name:'Basic Proxy',desc:'Simple HTTP reverse proxy to a local port',color:'var(--blue)'},
  websocket:     {icon:'⚡',name:'WebSocket',desc:'WebSocket + upgrade headers (Grafana, Jupyter)',color:'var(--purple)'},
  homeassistant: {icon:'⌂',name:'Home Assistant',desc:'Long-poll + WebSocket, 3600s timeout',color:'var(--teal)'},
  nextcloud:     {icon:'☁',name:'Nextcloud',desc:'10GB upload, CalDAV/CardDAV redirects',color:'#60a5fa'},
  loadbalancer:  {icon:'⚖',name:'Load Balancer',desc:'Round-robin across multiple upstreams',color:'var(--amber)'},
};

function nginxAddHtml() {
  const tmplCards = Object.entries(TMPL_INFO).map(([k,t])=>`
    <div class="tmpl-card ${S.selectedTemplate===k?'selected':''}" onclick="selectTmpl('${k}')">
      <div class="tmpl-card-icon" style="color:${t.color}">${t.icon}</div>
      <div class="tmpl-card-name">${t.name}</div>
      <div class="tmpl-card-desc">${t.desc}</div>
    </div>`).join('');
  const isLB = S.selectedTemplate === 'loadbalancer';
  return `
  <div class="card">
    <div class="card-title">Select Template</div>
    <div class="tmpl-grid">${tmplCards}</div>
    <hr class="divider">
    <div class="card-title">Configure Proxy</div>
    <div class="form-row"><label>DOMAIN NAME</label><input id="ng-domain" placeholder="movies.localnet"></div>
    ${isLB ? `
    <div class="form-row"><label>UPSTREAM SERVERS (one per line: ip:port)</label><textarea id="ng-upstreams" placeholder="192.168.1.10:8096\n192.168.1.11:8096"></textarea></div>
    ` : `
    <div class="form-grid-2">
      <div class="form-row"><label>UPSTREAM IP</label><input id="ng-ip" placeholder="127.0.0.1"></div>
      <div class="form-row"><label>PORT</label><input id="ng-port" placeholder="8096"></div>
    </div>`}
    <button class="btn btn-primary" onclick="addProxy()">+ Add Proxy</button>
  </div>`;
}
function initNginxAdd() {}
function selectTmpl(k) {
  S.selectedTemplate = k;
  pgNginx();
}
async function addProxy() {
  const domain = document.getElementById('ng-domain')?.value?.trim();
  const isLB   = S.selectedTemplate === 'loadbalancer';
  if (!domain) { toast('Enter a domain name','error'); return; }
  const body = { domain, template: S.selectedTemplate };
  if (isLB) {
    body.upstream_ip = '127.0.0.1'; body.port = '80';
    body.extras = { upstreams: document.getElementById('ng-upstreams')?.value||'' };
  } else {
    body.upstream_ip = document.getElementById('ng-ip')?.value?.trim() || '127.0.0.1';
    body.port        = document.getElementById('ng-port')?.value?.trim() || '80';
  }
  try {
    await api('POST','/nginx/proxies', body);
    toast(`Proxy for ${domain} being configured`, 'info');
    S.activeTab['nginx'] = 'proxies';
    setTimeout(pgNginx, 1800);
  } catch(e) { toast(e.message,'error'); }
}
async function removeProxy(domain) {
  if (!await confirmAction(`Remove proxy for '${domain}'?`)) return;
  try {
    await api('DELETE',`/nginx/proxies/${domain}`);
    toast(`Removed ${domain}`, 'info');
    setTimeout(pgNginx, 1500);
  } catch(e) { toast(e.message,'error'); }
}
function nginxManageHtml() {
  return `
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="ct-icon">⇌</span> Install Nginx</div>
      <div class="card-sub">Installs Nginx, removes the default welcome page, and starts the service.</div>
      <div class="btn-row">
        <button class="btn btn-success" onclick="installNginx()">⬡ Install Nginx</button>
        <button class="btn btn-danger"  onclick="uninstallNginx()">✕ Uninstall</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title"><span class="ct-icon">◈</span> Service Control</div>
      <div class="card-sub">Reload or restart Nginx after manual config edits.</div>
      <div class="btn-row">
        <button class="btn btn-ghost" onclick="reloadSvc('nginx')">↺ Reload Nginx</button>
      </div>
    </div>
  </div>`;
}
async function installNginx() {
  if (!await confirmAction('Install Nginx?')) return;
  try { await api('POST','/nginx/install'); toast('Nginx install started','info'); } catch(e) { toast(e.message,'error'); }
}
async function uninstallNginx() {
  if (!await confirmAction('Completely remove Nginx and all configs?')) return;
  try { await api('POST','/nginx/uninstall'); toast('Nginx removal started','info'); } catch(e) { toast(e.message,'error'); }
}

// ─── SSL Page ─────────────────────────────────────────────────────────────
async function pgSSL() {
  let certs = [];
  try { certs = await api('GET','/ssl/certs'); } catch(e) {}
// Update: Included the Delete button in the mapping
  const certList = certs.length
    ? certs.map(c => `
      <div class="cert-item" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div class="cert-name">${escHtml(c.name)}.pem</div>
          <div class="cert-path">${escHtml(c.path)}</div>
        </div>
        <button class="btn btn-amber" 
                onclick="deleteCert('${escHtml(c.name)}')" 
                title="Delete Certificate" 
                style="padding: 2px 8px; font-size: 12px; cursor: pointer;">✕</button>
      </div>`).join('')
    : `<div class="empty-state" style="padding:20px"><div class="empty-icon">◉</div>No certs yet</div>`;
  document.getElementById('content').innerHTML = `
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="ct-icon">◉</span> mkcert — Local CA</div>
      <div class="card-sub">Creates a local Certificate Authority trusted by your machine. Generate valid TLS certs for <span class="inline-code">*.localnet</span> or any private domain without browser warnings.</div>
      <div class="info-box"><strong>How it works:</strong> mkcert installs a root CA into your OS and browser trust stores. Any cert it signs is trusted automatically. No Let's Encrypt, no public DNS required.</div>
      <div class="btn-row">
      <button class="btn btn-success" onclick="installMkcert()">⬡ Install mkcert</button>
      </div>
      <hr class="divider">
      <div class="card-title" style="margin-bottom:10px">Generate Certificate</div>
      <div class="form-row">
        <label>DOMAIN (leave blank for wildcard *.localnet)</label>
        <input id="cert-domain" placeholder="*.localnet  or  nas.localnet">
      </div>
      <button class="btn btn-primary" onclick="genCert()">+ Generate Cert</button>
    </div>
    <div class="card">
      <div class="card-title"><span class="ct-icon">◈</span> Issued Certificates</div>
      ${certList}
      <hr class="divider">
      <div class="card-title" style="margin-bottom:8px">Add SSL to Nginx</div>
      <div class="card-sub" style="font-family:var(--mono);font-size:11px;line-height:2">
        listen 443 ssl;<br>
        ssl_certificate     /etc/localnet/certs/DOMAIN.pem;<br>
        ssl_certificate_key /etc/localnet/certs/DOMAIN-key.pem;
      </div>
      <div class="info-box" style="margin-top:12px"><strong>Browser trust:</strong> Import <span class="inline-code">/etc/localnet/ca/rootCA.pem</span> into your browser's CA store once — all generated certs will be trusted automatically.</div>
      
    </div>
  </div>`;
}
async function installMkcert() {
  if (!await confirmAction('Install mkcert and create a local CA?')) return;
  try { await api('POST','/ssl/mkcert/install'); toast('mkcert install started','info'); } catch(e) { toast(e.message,'error'); }
}
async function genCert() {
  const domain = document.getElementById('cert-domain')?.value?.trim() || '';
  try {
    await api('POST','/ssl/mkcert/cert',{domain});
    toast('Cert generation started — check the log','info');
    setTimeout(pgSSL, 3000);
  } catch(e) { toast(e.message,'error'); }
}
async function downloadRootCA() {
    // This triggers the browser download manager directly
    window.location.href = '/api/ssl/rootca';
}

async function deleteCert(domain) {
  // Always good to confirm before deleting cryptographic files
  if (!confirm(`Are you sure you want to delete the certificate for ${domain}?`)) return;
  
  try {
    await api('DELETE', `/ssl/certs/${domain}`);
    toast(`Deleted certificate for ${domain}`, 'success');
    pgSSL(); // Re-run the function to refresh the list immediately
  } catch (e) {
    toast(e.message, 'error');
  }
}

// ─── Network Page ─────────────────────────────────────────────────────────
async function pgNetwork() {
  let ifaces = [];
  try { ifaces = await api('GET','/network/interfaces'); } catch(e) {}
  const rows = ifaces.map(i=>`
    <tr>
      <td class="mono">${escHtml(i.name)}</td>
      <td class="mono">${escHtml(i.ip)}</td>
      <td class="mono">/${i.prefix}</td>
      <td><span class="type-badge ${i.state==='UP'?'type-A':'type-MX'}">${i.state}</span></td>
      <td class="mono" style="color:var(--dim)">${escHtml(i.ip.split('.').slice(0,3).join('.'))}.0/${i.prefix}</td>
    </tr>`).join('') || `<tr><td colspan="5"><div class="empty-state">No interfaces found</div></td></tr>`;

  document.getElementById('content').innerHTML = `
  <div class="card">
    <div class="card-title"><span class="ct-icon">⊞</span> Detected Network Interfaces</div>
    <div class="card-sub">All non-loopback IPv4 interfaces. The IP you select during DNS setup determines which interface BIND9 listens on and which subnet is trusted.</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>INTERFACE</th><th>IP ADDRESS</th><th>PREFIX</th><th>STATE</th><th>SUBNET</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </div>
  <div class="info-box">
    <strong>Multi-subnet / VLAN tip:</strong> To serve multiple subnets, add them to the <span class="inline-code">trusted_network</span> ACL in <span class="inline-code">/etc/bind/named.conf.options</span> and reload BIND9. Each additional subnet needs a separate reverse zone declared in <span class="inline-code">named.conf.local</span>.
  </div>`;
}

// ─── Settings Page ────────────────────────────────────────────────────────
async function pgSettings() {
  const cfg = await api('GET','/config');
  S.cfg = cfg;
  const fwds = (cfg.forwarders||['1.1.1.2','1.0.0.2']).join(', ');
  document.getElementById('content').innerHTML = `
  <div class="card">
    <div class="card-title"><span class="ct-icon">⊙</span> General Settings</div>
    <div class="card-sub">These are saved to disk and pre-filled in install dialogs. Changing them here does not modify a running DNS installation — re-run Install to apply.</div>
    <div class="form-grid-2">
      <div class="form-row"><label>DEFAULT DOMAIN (TLD)</label><input id="s-domain" value="${escHtml(cfg.domain||'localnet')}"></div>
      <div class="form-row"><label>DNS FORWARDERS</label><input id="s-fwds" value="${escHtml(fwds)}" placeholder="1.1.1.2, 1.0.0.2"></div>
    </div>
    <div class="form-row">
      <label>VPN-COMPATIBLE MODE DEFAULT</label>
      <div class="toggle-wrap" style="margin-top:6px">
        <div class="toggle ${cfg.vpn_safe?'on':''}" id="s-vpn-toggle" onclick="this.classList.toggle('on')"></div>
        <span class="toggle-label">Route through systemd-resolved (recommended)</span>
      </div>
    </div>
    <div class="btn-row">
      <button class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="ct-icon">◈</span> Quick Service Controls</div>
    <div class="btn-row">
      <button class="btn btn-ghost" onclick="reloadSvc('bind9')">↺ Reload BIND9</button>
      <button class="btn btn-ghost" onclick="reloadSvc('nginx')">↺ Reload Nginx</button>
      <button class="btn btn-ghost" onclick="reloadSvc('systemd-resolved')">↺ Restart resolved</button>
    </div>
  </div>`;
}
async function saveSettings() {
  const domain = document.getElementById('s-domain')?.value?.trim();
  const fwdRaw = document.getElementById('s-fwds')?.value || '';
  const fwds   = fwdRaw.split(',').map(s=>s.trim()).filter(Boolean);
  const vpn    = document.getElementById('s-vpn-toggle')?.classList.contains('on');
  try {
    await api('POST','/config',{domain,forwarders:fwds,vpn_safe:vpn});
    toast('Settings saved', 'success');
  } catch(e) { toast(e.message,'error'); }
}

// ─── DNS Records Tab: add TXT / SRV / Wildcard ───────────────────────────
async function dnsRecordsHtml_v4() {
  let records = [];
  try { records = await api('GET','/dns/records'); } catch(e) {}
  const tab = getTab('dnsrec','a');
  const recTabs = tabBar('dnsrec',[['a','A / CNAME'],['txt','TXT'],['srv','SRV'],['wildcard','Wildcard']],tab);
  let formHtml = '';
  if (tab === 'a') {
    formHtml = `
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Add A Record</div>
        <div class="form-grid-2">
          <div class="form-row"><label>HOSTNAME</label><input id="a-host" placeholder="nas"></div>
          <div class="form-row"><label>IP ADDRESS</label><input id="a-ip" placeholder="192.168.1.20"></div>
        </div>
        <button class="btn btn-primary" onclick="addA()">+ Add A Record</button>
      </div>
      <div class="card">
        <div class="card-title">Add CNAME</div>
        <div class="form-grid-2">
          <div class="form-row"><label>ALIAS</label><input id="cn-alias" placeholder="movies"></div>
          <div class="form-row"><label>TARGET HOST</label><input id="cn-target" placeholder="ns1"></div>
        </div>
        <button class="btn btn-primary" onclick="addCname()">+ Add CNAME</button>
      </div>
    </div>`;
  } else if (tab === 'txt') {
    formHtml = `
    <div class="card">
      <div class="card-title">Add TXT Record</div>
      <div class="card-sub">Used for domain verification, SPF records, and ACME DNS-01 challenges. Values are auto-quoted.</div>
      <div class="form-grid-2">
        <div class="form-row"><label>HOSTNAME (@ for root)</label><input id="txt-host" placeholder="@"></div>
        <div class="form-row"><label>VALUE</label><input id="txt-val" placeholder="v=spf1 include:example.com ~all"></div>
      </div>
      <button class="btn btn-primary" onclick="addTXT()">+ Add TXT Record</button>
    </div>`;
  } else if (tab === 'srv') {
    formHtml = `
    <div class="card">
      <div class="card-title">Add SRV Record</div>
      <div class="card-sub">Service locator records. Format: <span class="inline-code">_service._proto → target:port</span></div>
      <div class="form-grid-3">
        <div class="form-row"><label>SERVICE (e.g. _http)</label><input id="srv-svc" placeholder="_http"></div>
        <div class="form-row"><label>PROTO (e.g. _tcp)</label><input id="srv-proto" placeholder="_tcp"></div>
        <div class="form-row"><label>PORT</label><input id="srv-port" placeholder="8080"></div>
      </div>
      <div class="form-grid-3">
        <div class="form-row"><label>TARGET HOST</label><input id="srv-target" placeholder="nas"></div>
        <div class="form-row"><label>PRIORITY</label><input id="srv-prio" placeholder="10"></div>
        <div class="form-row"><label>WEIGHT</label><input id="srv-weight" placeholder="5"></div>
      </div>
      <button class="btn btn-primary" onclick="addSRV()">+ Add SRV Record</button>
    </div>`;
  } else if (tab === 'wildcard') {
    formHtml = `
    <div class="card">
      <div class="card-title">Add Wildcard A Record</div>
      <div class="card-sub">Creates <span class="inline-code">*.domain → IP</span> so any subdomain resolves to this IP. Useful for catch-all Nginx configs.</div>
      <div class="form-row" style="max-width:260px">
        <label>IP ADDRESS</label><input id="wc-ip" placeholder="192.168.1.10">
      </div>
      <button class="btn btn-amber" onclick="addWildcard()">+ Add Wildcard</button>
    </div>`;
  }
  const rows = records.length
    ? records.map(r=>`
      <tr>
        <td class="mono">${escHtml(r.host)}</td>
        <td><span class="type-badge type-${r.type}">${r.type}</span></td>
        <td class="mono" style="max-width:280px;overflow:hidden;text-overflow:ellipsis">${escHtml(r.value)}</td>
        <td><button class="del-btn" onclick="removeRecord('${escHtml(r.host)}')">✕</button></td>
      </tr>`).join('')
    : `<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">◎</div>No records yet.</div></td></tr>`;
  return recTabs + formHtml + `
  <div class="card" style="margin-top:4px">
    <div class="card-title">Zone Records</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>HOSTNAME</th><th>TYPE</th><th>VALUE</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </div>`;
}

async function addTXT() {
  const host = document.getElementById('txt-host')?.value?.trim();
  const val  = document.getElementById('txt-val')?.value?.trim();
  if (!host || !val) { toast('Enter hostname and value','error'); return; }
  try {
    await api('POST','/dns/records/txt',{host,value:val});
    toast(`TXT record queued`, 'info');
    setTimeout(()=>{ S.activeTab['dns']='records'; pgDNS(); }, 1800);
  } catch(e) { toast(e.message,'error'); }
}
async function addSRV() {
  const svc    = document.getElementById('srv-svc')?.value?.trim();
  const proto  = document.getElementById('srv-proto')?.value?.trim();
  const port   = document.getElementById('srv-port')?.value?.trim();
  const target = document.getElementById('srv-target')?.value?.trim();
  const prio   = document.getElementById('srv-prio')?.value?.trim() || '10';
  const weight = document.getElementById('srv-weight')?.value?.trim() || '5';
  if (!svc||!proto||!port||!target) { toast('Fill all SRV fields','error'); return; }
  try {
    await api('POST','/dns/records/srv',{service:svc,proto,port,target,priority:parseInt(prio),weight:parseInt(weight)});
    toast('SRV record queued','info');
    setTimeout(()=>{ S.activeTab['dns']='records'; pgDNS(); }, 1800);
  } catch(e) { toast(e.message,'error'); }
}
async function addWildcard() {
  const ip = document.getElementById('wc-ip')?.value?.trim();
  if (!ip) { toast('Enter IP address','error'); return; }
  if (!await confirmAction(`Add wildcard *.${S.status.domain||'localnet'} → ${ip}?`)) return;
  try {
    await api('POST','/dns/records/wildcard',{ip});
    toast('Wildcard record queued','info');
    setTimeout(()=>{ S.activeTab['dns']='records'; pgDNS(); }, 1800);
  } catch(e) { toast(e.message,'error'); }
}

// ─── DHCP Page ────────────────────────────────────────────────────────────
async function pgDHCP() {
  let leases = [], dhcpActive = false;
  try { leases = await api('GET','/dhcp/leases'); } catch(e) {}
  try { const s = await api('GET','/dhcp/status'); dhcpActive = s.active; } catch(e) {}
  const tab = getTab('dhcp','config');
  let html = tabBar('dhcp',[['config','Configure'],['leases','Active Leases']],tab);
  if (tab === 'config') {
    const ip = S.status.server_ip || '';
    const p  = ip.split('.');
    const prefix = p.length === 4 ? p.slice(0,3).join('.') : '192.168.1';
    html += `
    <div class="card">
      <div class="card-title"><span class="ct-icon">⊹</span> DHCP Server (isc-dhcp-server)</div>
      <div class="card-sub">Assigns IP addresses to network devices automatically and registers their hostnames in BIND9. The DHCP server should run on the same machine as your DNS server.</div>
      <div class="info-box" style="margin-bottom:16px">
        <strong>Status:</strong> isc-dhcp-server is currently
        <span style="color:${dhcpActive?'var(--green)':'var(--dim)'}">${dhcpActive?'running ▲':'stopped ▼'}</span>
      </div>
      <div class="form-grid-3">
        <div class="form-row"><label>RANGE START</label><input id="dhcp-rs" value="${prefix}.100"></div>
        <div class="form-row"><label>RANGE END</label><input id="dhcp-re" value="${prefix}.200"></div>
        <div class="form-row"><label>ROUTER / GATEWAY</label><input id="dhcp-gw" value="${prefix}.1"></div>
      </div>
      <div class="form-grid-2">
        <div class="form-row"><label>LEASE TIME (seconds)</label><input id="dhcp-lt" value="3600"></div>
        <div class="form-row"><label>SERVER IP (DNS)</label><input id="dhcp-ip" value="${ip}"></div>
      </div>
      <div class="btn-row">
        <button class="btn btn-success" onclick="installDHCP()">⊹ Install &amp; Configure DHCP</button>
        <button class="btn btn-danger"  onclick="removeDHCP()">✕ Remove DHCP</button>
        ${dhcpActive ? '<button class="btn btn-ghost" onclick="reloadSvc(\\'isc-dhcp-server\\')">↺ Restart</button>' : ''}
      </div>
    </div>`;
  } else {
    const rows = leases.length
      ? leases.map(l=>`
        <tr>
          <td class="mono lease-active">${escHtml(l.ip)}</td>
          <td class="mono">${escHtml(l.mac)}</td>
          <td class="mono">${escHtml(l.hostname)||'<span style="color:var(--dim2)">unknown</span>'}</td>
          <td style="font-size:11px;color:var(--dim)">${escHtml(l.ends)}</td>
          <td><span class="type-badge type-A">${l.state}</span></td>
        </tr>`).join('')
      : `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">⊹</div>No active leases — DHCP may not be running.</div></td></tr>`;
    html += `
    <div class="card">
      <div class="card-title">Active DHCP Leases</div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>IP</th><th>MAC</th><th>HOSTNAME</th><th>EXPIRES</th><th>STATE</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <div class="btn-row" style="margin-top:14px">
        <button class="btn btn-ghost" onclick="setTab('dhcp','leases');pgDHCP()">↺ Refresh</button>
      </div>
    </div>`;
  }
  document.getElementById('content').innerHTML = html;
}
async function installDHCP() {
  if (!await confirmAction('Install isc-dhcp-server and apply config?')) return;
  const body = {
    range_start: document.getElementById('dhcp-rs')?.value?.trim(),
    range_end:   document.getElementById('dhcp-re')?.value?.trim(),
    router:      document.getElementById('dhcp-gw')?.value?.trim(),
    lease_time:  parseInt(document.getElementById('dhcp-lt')?.value||'3600'),
    server_ip:   document.getElementById('dhcp-ip')?.value?.trim(),
  };
  try { await api('POST','/dhcp/install',body); toast('DHCP install started','info'); }
  catch(e) { toast(e.message,'error'); }
}
async function removeDHCP() {
  if (!await confirmAction('Remove isc-dhcp-server?')) return;
  try { await api('POST','/dhcp/remove'); toast('DHCP removal started','info'); }
  catch(e) { toast(e.message,'error'); }
}

// ─── Ad Blocking Page ─────────────────────────────────────────────────────
async function pgAdBlock() {
  let abStatus = { enabled: false, entry_count: 0 };
  try { abStatus = await api('GET','/adblock/status'); } catch(e) {}
  const enabled = abStatus.enabled;
  const count   = abStatus.entry_count || 0;
  document.getElementById('content').innerHTML = `
  <div class="adblock-hero">
    <div class="adblock-count" style="color:${enabled?'var(--green)':'var(--dim2)'}">${count.toLocaleString()}</div>
    <div class="adblock-label">BLOCKED DOMAINS</div>
    <div style="margin-top:12px;font-size:12px;color:${enabled?'var(--green)':'var(--dim)'}">
      ${enabled ? '⬡ Ad blocking is ACTIVE' : '○ Ad blocking is OFF'}
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="ct-icon">⊘</span> BIND9 RPZ Ad Blocking</div>
    <div class="card-sub">
      Downloads the <strong style="color:var(--text)">StevenBlack unified hosts list</strong> and injects it as a BIND9 Response Policy Zone (RPZ).
      Blocked domains return NXDOMAIN — no separate proxy needed, works at the DNS layer for every device on your network.
    </div>
    <div class="info-box">
      <strong>How it works:</strong> A zone file named <span class="inline-code">rpz.adblock</span> is created in
      <span class="inline-code">/etc/bind/adblock/</span> with CNAME "." entries for every ad/tracker domain.
      BIND9's <span class="inline-code">response-policy</span> directive intercepts queries and returns NXDOMAIN before
      they ever reach the internet. Updates are applied by re-enabling (re-downloads the list).
    </div>
    <div class="btn-row">
      ${enabled
        ? '<button class="btn btn-danger" onclick="disableAdBlock()">⊘ Disable Ad Blocking</button>'
        : '<button class="btn btn-success" onclick="enableAdBlock()">⬡ Enable Ad Blocking</button>'}
      ${enabled ? '<button class="btn btn-amber" onclick="enableAdBlock()">↺ Update List</button>' : ''}
    </div>
  </div>
  <div class="card">
    <div class="card-title">Source</div>
    <div class="card-sub">
      Uses <strong style="color:var(--text)">StevenBlack/hosts</strong> (unified list with extensions for ads, malware, and fakenews).
      Typically blocks 100,000–200,000 domains. Updated list is fetched fresh each time you enable.
    </div>
    <div style="font-family:var(--mono);font-size:11px;color:var(--dim);margin-top:8px">
      https://github.com/StevenBlack/hosts
    </div>
  </div>`;
}
async function enableAdBlock() {
  if (!await confirmAction('Enable ad blocking? This downloads the blocklist and modifies BIND9.')) return;
  try { await api('POST','/adblock/enable'); toast('Ad blocking being enabled — watch log','info'); setTimeout(pgAdBlock,3000); }
  catch(e) { toast(e.message,'error'); }
}
async function disableAdBlock() {
  if (!await confirmAction('Disable ad blocking?')) return;
  try { await api('POST','/adblock/disable'); toast('Ad blocking disabled','info'); setTimeout(pgAdBlock,2000); }
  catch(e) { toast(e.message,'error'); }
}

// ─── Backups Page ─────────────────────────────────────────────────────────
async function pgBackups() {
  let backups = [];
  try { backups = await api('GET','/backups'); } catch(e) {}
  const rows = backups.length
    ? backups.map(b=>`
      <div class="backup-row">
        <div class="backup-row-info">
          <div class="backup-name">${escHtml(b.label || b.path.split('/').pop())}</div>
          <div class="backup-date">${escHtml(b.created_at || '')}  &nbsp; ${escHtml(b.path)}</div>
        </div>
        <button class="btn btn-ghost" style="font-size:11px;padding:4px 10px" onclick="restoreBackup('${escHtml(b.path)}')">↺ Restore</button>
        <button class="del-btn" onclick="deleteBackup('${escHtml(b.path)}')">✕</button>
      </div>`).join('')
    : '<div class="empty-state"><div class="empty-icon">⊟</div>No backups yet. Backups are created automatically before every operation.</div>';
  document.getElementById('content').innerHTML = `
  <div class="card">
    <div class="card-title"><span class="ct-icon">⊟</span> Configuration Backups</div>
    <div class="card-sub">
      A snapshot of <span class="inline-code">/etc/bind</span> and <span class="inline-code">/etc/nginx</span> is created automatically
      before every install, remove, or modify operation. Use Restore to roll back a broken config.
    </div>
    <div class="btn-row" style="margin-bottom:16px">
      <button class="btn btn-primary" onclick="createBackup()">+ Create Snapshot Now</button>
      <button class="btn btn-ghost"   onclick="pgBackups()">↺ Refresh</button>
    </div>
    ${rows}
  </div>
  <div class="info-box">
    <strong>Storage:</strong> Backups are saved to <span class="inline-code">/etc/localnet/backups/</span>.
    After restoring, BIND9 and Nginx are restarted automatically to apply the restored configuration.
  </div>`;
}
async function createBackup() {
  try {
    const r = await api('POST','/backups/create',{label:'manual'});
    toast(r.ok ? 'Backup created' : 'Backup failed', r.ok ? 'success' : 'error');
    setTimeout(pgBackups, 1500);
  } catch(e) { toast(e.message,'error'); }
}
async function restoreBackup(path) {
  if (!await confirmAction('Restore this backup? BIND9 and Nginx will be restarted.')) return;
  try {
    await api('POST','/backups/restore',{path});
    toast('Restore started — watch the log','info');
  } catch(e) { toast(e.message,'error'); }
}
async function deleteBackup(path) {
  if (!await confirmAction('Delete this backup?')) return;
  try {
    await api('POST','/backups/delete',{path});
    toast('Backup deleted','info');
    setTimeout(pgBackups, 800);
  } catch(e) { toast(e.message,'error'); }
}

// ─── System Logs Page ─────────────────────────────────────────────────────
let journalES = null;
function pgLogs() {
  const svc = getTab('logs','bind9');
  const svcs = [['bind9','BIND9'],['nginx','Nginx'],['dhcp','DHCP'],['resolved','Resolved']];
  const tabHtml = `<div class="tabs">${svcs.map(([k,l])=>`<div class="tab ${k===svc?'active':''}" onclick="setLogsTab('${k}')">${l}</div>`).join('')}</div>`;
  document.getElementById('content').innerHTML = `
  ${tabHtml}
  <div class="card">
    <div class="card-title" style="margin-bottom:8px">
      <span class="ct-icon">≡</span> Live Journal — ${svcs.find(s=>s[0]===svc)?.[1]||svc}
      <button class="btn btn-ghost" style="font-size:11px;padding:4px 10px;margin-left:auto" onclick="clearJournal()">Clear</button>
    </div>
    <div id="journal-box">Connecting to journal stream...</div>
  </div>`;
  startJournalStream(svc);
}
function setLogsTab(svc) {
  S.activeTab['logs'] = svc;
  stopJournalStream();
  pgLogs();
}
function stopJournalStream() {
  if (journalES) { try { journalES.close(); } catch(e) {} journalES = null; }
}
function startJournalStream(svc) {
  stopJournalStream();
  const box = document.getElementById('journal-box');
  if (!box) return;
  box.textContent = '';
  journalES = new EventSource(`/api/logs/journal?service=${svc}&tail=120`);
  journalES.onmessage = e => {
    try {
      const d = JSON.parse(e.data);
      const line = document.createElement('div');
      const t = d.msg || '';
      if (/error|fail|crit/i.test(t)) line.className = 'jline-err';
      else if (/warn/i.test(t)) line.className = 'jline-warn';
      else if (/ok|success|start/i.test(t)) line.className = 'jline-ok';
      line.textContent = t;
      box.appendChild(line);
      if (box.children.length > 600) box.removeChild(box.firstChild);
      box.scrollTop = box.scrollHeight;
    } catch(err) {}
  };
  journalES.onerror = () => {
    const box = document.getElementById('journal-box');
    if (box) { const l = document.createElement('div'); l.className='jline-warn'; l.textContent='[stream disconnected]'; box.appendChild(l); }
  };
}
function clearJournal() {
  const box = document.getElementById('journal-box');
  if (box) box.textContent = '';
}

// ─── SSL Page — add Certbot section ───────────────────────────────────────
async function pgSSL() {
  const tab = getTab('ssl','mkcert');
  let html = tabBar('ssl', [["mkcert", "mkcert (Local CA)"], ["certbot", "Let's Encrypt"]], tab);
  if (tab === 'mkcert') {
    let certs = [];
    try { certs = await api('GET','/ssl/certs'); } catch(e) {}
  // Update: Included the Delete button in the mapping
  const certList = certs.length
    ? certs.map(c => `
      <div class="cert-item" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div class="cert-name">${escHtml(c.name)}.pem</div>
          <div class="cert-path">${escHtml(c.path)}</div>
        </div>
        <button class="btn btn-ghost" 
                onclick="deleteCert('${escHtml(c.name)}')" 
                title="Delete Certificate" 
                style="padding: 2px 8px; font-size: 12px; cursor: pointer;">✕</button>
      </div>`).join('')
    : `<div class="empty-state" style="padding:20px"><div class="empty-icon">◉</div>No certs yet</div>`;
    html += `
    <div class="grid-2">
      <div class="card">
        <div class="card-title"><span class="ct-icon">◉</span> mkcert — Local CA</div>
        <div class="card-sub">Creates a local Certificate Authority trusted by your machine. Generate valid TLS certs for <span class="inline-code">*.localnet</span> without browser warnings.</div>
        <div class="info-box"><strong>How it works:</strong> mkcert installs a root CA into your OS and browser trust stores. Any cert it signs is trusted automatically on this machine. No port 80 needed.</div>
        <div class="btn-row"><button class="btn btn-success" onclick="installMkcert()">⬡ Install mkcert</button></div>
        <hr class="divider">
        <div class="card-title" style="margin-bottom:10px">Generate Certificate</div>
        <div class="form-row"><label>DOMAIN (blank = wildcard)</label><input id="cert-domain" placeholder="*.localnet  or  nas.localnet"></div>
        <button class="btn btn-primary" onclick="genCert()">+ Generate Cert</button>
      </div>
      <div class="card">
        <div class="card-title"><span class="ct-icon">◈</span> Issued mkcert Certs</div>
        ${certList}
        <hr class="divider">
        <div class="card-title" style="margin-bottom:8px">Add to Nginx</div>
        <div class="card-sub" style="font-family:var(--mono);font-size:11px;line-height:2">
          listen 443 ssl;<br>
          ssl_certificate     /etc/localnet/certs/DOMAIN.pem;<br>
          ssl_certificate_key /etc/localnet/certs/DOMAIN-key.pem;
        </div>
        <div class="info-box" style="margin-top:12px"><strong>Browser trust:</strong> Import <span class="inline-code">/etc/localnet/ca/rootCA.pem</span> into your browser's CA store once. (Usually found in privacy settings) <p /><a onclick="downloadRootCA()"><strong>Click here to download 'Root CA'</strong></a></div>
      </div>
    </div>`;
  } else {
    let leCerts = [];
    try { leCerts = await api('GET','/ssl/letsencrypt/certs'); } catch(e) {}
    const leList = leCerts.length
      ? leCerts.map(c=>`<div class="cert-item"><div><div class="cert-name">${escHtml(c.name)}</div><div class="cert-path">${escHtml(c.cert)}</div></div><span style="font-size:11px;color:${c.exists?'var(--green)':'var(--dim)'}">${c.exists?'✔ valid':'✘ missing'}</span></div>`).join('')
      : `<div class="empty-state" style="padding:20px"><div class="empty-icon">◉</div>No Let's Encrypt certs yet</div>`;
    html += `
    <div class="grid-2">
      <div class="card">
        <div class="card-title"><span class="ct-icon">◉</span> Certbot + DNS-01</div>
        <div class="card-sub">Issues globally browser-trusted Let's Encrypt certificates using the DNS-01 ACME challenge via your local BIND9. No port 80 or public IP required.</div>
        <div class="info-box">
          <strong>How it works:</strong> Certbot uses a TSIG key to write a temporary TXT record into your BIND9 zone, proves domain ownership to Let's Encrypt, then removes it.
          The resulting cert is globally trusted — no CA import needed on any device.<br><br>
          <strong>Requirement:</strong> Your domain must be publicly resolvable (real domain you own) for Let's Encrypt to validate it.
        </div>
        <div class="btn-row"><button class="btn btn-success" onclick="installCertbot()">⬡ Install Certbot</button></div>
        <hr class="divider">
        <div class="card-title" style="margin-bottom:10px">Request Certificate</div>
        <div class="form-row"><label>EMAIL (Let's Encrypt account)</label><input id="le-email" placeholder="you@example.com"></div>
        <div class="form-row"><label>DOMAIN</label><input id="le-domain" placeholder="*.yourdomain.com"></div>
        <button class="btn btn-primary" onclick="requestLECert()">+ Request via DNS-01</button>
      </div>
      <div class="card">
        <div class="card-title"><span class="ct-icon">◈</span> Let's Encrypt Certs</div>
        ${leList}
        <hr class="divider">
        <div class="card-title" style="margin-bottom:8px">Add to Nginx</div>
        <div class="card-sub" style="font-family:var(--mono);font-size:11px;line-height:2">
          listen 443 ssl;<br>
          ssl_certificate     /etc/letsencrypt/live/DOMAIN/fullchain.pem;<br>
          ssl_certificate_key /etc/letsencrypt/live/DOMAIN/privkey.pem;
        </div>
      </div>
    </div>`;
  }
  document.getElementById('content').innerHTML = html;
}
async function installCertbot() {
  if (!await confirmAction('Install certbot and python3-certbot-dns-rfc2136?')) return;
  try { await api('POST','/ssl/certbot/install'); toast('Certbot install started','info'); } catch(e) { toast(e.message,'error'); }
}
async function requestLECert() {
  const email  = document.getElementById('le-email')?.value?.trim();
  const domain = document.getElementById('le-domain')?.value?.trim();
  if (!email||!domain) { toast('Email and domain required','error'); return; }
  if (!await confirmAction(`Request Let's Encrypt cert for ${domain}?`)) return;
  try {
    await api('POST','/ssl/certbot/cert',{email,domain});
    toast('Cert request started — watch the log','info');
    setTimeout(()=>{ S.activeTab['ssl']='certbot'; pgSSL(); }, 4000);
  } catch(e) { toast(e.message,'error'); }
}

// ─── Settings Page — add password change ──────────────────────────────────
async function pgSettings() {
  const cfg = await api('GET','/config');
  S.cfg = cfg;
  const fwds = (cfg.forwarders||['1.1.1.2','1.0.0.2']).join(', ');
  document.getElementById('content').innerHTML = `
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="ct-icon">⊙</span> General Settings</div>
      <div class="card-sub">Changing these does not modify a running DNS install — re-run Install to apply.</div>
      <div class="form-row"><label>DEFAULT DOMAIN (TLD)</label><input id="s-domain" value="${escHtml(cfg.domain||'localnet')}"></div>
      <div class="form-row"><label>DNS FORWARDERS</label><input id="s-fwds" value="${escHtml(fwds)}" placeholder="1.1.1.2, 1.0.0.2"></div>
      <div class="form-row">
        <label>VPN-COMPATIBLE MODE</label>
        <div class="toggle-wrap" style="margin-top:6px">
          <div class="toggle ${cfg.vpn_safe?'on':''}" id="s-vpn-toggle" onclick="this.classList.toggle('on')"></div>
          <span class="toggle-label">Route through systemd-resolved</span>
        </div>
      </div>
      <div class="btn-row"><button class="btn btn-primary" onclick="saveSettings()">Save Settings</button></div>
    </div>
    <div class="card pw-card">
      <div class="card-title"><span class="ct-icon">◉</span> Change Password</div>
      <div class="card-sub">Default password on first run is <span class="inline-code">localnet</span>. Change it immediately.</div>
      <div class="form-row"><label>CURRENT PASSWORD</label><input type="password" id="pw-cur" placeholder="current password"></div>
      <div class="form-row"><label>NEW PASSWORD</label><input type="password" id="pw-new" placeholder="min 6 characters"></div>
      <div class="form-row"><label>CONFIRM NEW PASSWORD</label><input type="password" id="pw-conf" placeholder="repeat new password"></div>
      <div class="btn-row"><button class="btn btn-amber" onclick="changePW()">Change Password</button></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="ct-icon">◈</span> Quick Service Controls</div>
    <div class="btn-row">
      <button class="btn btn-ghost" onclick="reloadSvc('bind9')">↺ Reload BIND9</button>
      <button class="btn btn-ghost" onclick="reloadSvc('nginx')">↺ Reload Nginx</button>
      <button class="btn btn-ghost" onclick="reloadSvc('systemd-resolved')">↺ Restart resolved</button>
    </div>
  </div>`;
}
async function saveSettings() {
  const domain = document.getElementById('s-domain')?.value?.trim();
  const fwdRaw = document.getElementById('s-fwds')?.value || '';
  const fwds   = fwdRaw.split(',').map(s=>s.trim()).filter(Boolean);
  const vpn    = document.getElementById('s-vpn-toggle')?.classList.contains('on');
  try {
    await api('POST','/config',{domain,forwarders:fwds,vpn_safe:vpn});
    toast('Settings saved', 'success');
  } catch(e) { toast(e.message,'error'); }
}
async function changePW() {
  const cur  = document.getElementById('pw-cur')?.value || '';
  const nw   = document.getElementById('pw-new')?.value || '';
  const conf = document.getElementById('pw-conf')?.value || '';
  if (nw !== conf) { toast('New passwords do not match','error'); return; }
  if (nw.length < 6) { toast('Password must be at least 6 characters','error'); return; }
  try {
    await api('POST','/auth/change-password',{current:cur,new:nw});
    toast('Password changed successfully','success');
    document.getElementById('pw-cur').value = '';
    document.getElementById('pw-new').value = '';
    document.getElementById('pw-conf').value = '';
  } catch(e) { toast(e.message,'error'); }
}

// ─── Device Manager ───────────────────────────────────────────────────────
let _dmDevices = [];
let _dmEditId  = null;

async function dnsDeviceManagerHtml() {
  let devices = [], tracking = {};
  try { devices = await api('GET','/devices'); } catch(e){}
  try { tracking = await api('GET','/devices/tracking/status'); } catch(e){}
  _dmDevices = devices;

  const trackOn  = tracking.tracking_active || tracking.conf_has_logging;
  const trackBadge = trackOn
    ? `<span style="color:var(--green);font-size:11px">● ACTIVE</span>`
    : `<span style="color:var(--dim);font-size:11px">○ OFF</span>`;

  // Diagnostic detail about the BIND9 query log
  const li = tracking.log_info || {};
  let diagHtml = '';
  if (tracking.query_log_exists) {
    const kb = li.size_bytes ? (li.size_bytes/1024).toFixed(1)+'KB' : '0 KB';
    diagHtml = `<div style="margin-top:8px;font-family:var(--mono);font-size:10px;color:var(--dim)">
      Log: <span class="inline-code">${escHtml(tracking.query_log_path||'')}</span> &nbsp;·&nbsp;
      ${li.line_count||0} lines &nbsp;·&nbsp; ${kb}
      ${li.last_line ? `<br>Last entry: <span style="color:var(--dim2)">${escHtml(li.last_line)}</span>` : ''}
    </div>`;
  } else if (trackOn) {
    diagHtml = `<div style="margin-top:8px;font-size:11px;color:var(--amber,#fbbf24)">
      ⚠ Log file not found at <span class="inline-code">${escHtml(tracking.query_log_path||'')}</span> —
      BIND9 may still be reloading, or may be writing to syslog instead.
      <strong>Scan Now</strong> still works (it reads ARP + DHCP). Check the Logs tab for BIND9 errors.
    </div>`;
  }

  const rows = devices.length ? devices.map(d => {
    const label    = escHtml(d.label || d.hostname || d.ip);
    const ip       = escHtml(d.ip);
    const mac      = escHtml(d.mac || '—');
    const lastSeen = escHtml((d.last_seen||'').replace('T',' ').slice(0,16));
    const queries  = d.query_count || 0;
    const blocked  = d.blocked;
    const regd     = d.dns_registered;
    const hostname = escHtml(d.hostname || '');
    const notes    = escHtml(d.notes || '');

    const blockBtn = blocked
      ? `<button class="btn btn-success" style="padding:3px 8px;font-size:11px" onclick="dmUnblock(${d.id})">✔ Unblock</button>`
      : `<button class="btn btn-danger"  style="padding:3px 8px;font-size:11px" onclick="dmBlock(${d.id})">⊘ Block DNS</button>`;

    const regBtn = regd
      ? `<button class="btn btn-amber"   style="padding:3px 8px;font-size:11px" onclick="dmUnregister(${d.id})">⊖ Unregister</button>`
      : `<button class="btn btn-primary" style="padding:3px 8px;font-size:11px" onclick="dmRegisterModal(${d.id})">⊕ Register</button>`;

    return `<tr class="${blocked ? 'dm-row-blocked' : ''}">
      <td>
        <div style="font-weight:600;color:var(--fg)">${label}</div>
        ${hostname && hostname !== d.ip ? `<div style="font-size:10px;color:var(--dim);font-family:var(--mono)">${hostname}</div>` : ''}
        ${notes ? `<div style="font-size:10px;color:var(--dim2);margin-top:2px">${notes}</div>` : ''}
      </td>
      <td class="mono">${ip}</td>
      <td class="mono" style="font-size:11px">${mac}</td>
      <td style="font-size:11px;color:var(--dim)">${lastSeen}</td>
      <td style="font-size:11px;text-align:center">${queries}</td>
      <td>
        ${blocked ? '<span class="type-badge type-MX" style="font-size:10px">BLOCKED</span>' :
          regd    ? '<span class="type-badge type-A"  style="font-size:10px">REGISTERED</span>' :
                    '<span style="color:var(--dim2);font-size:10px">—</span>'}
      </td>
      <td>
        <div style="display:flex;gap:4px;flex-wrap:wrap;align-items:center">
          ${blockBtn}
          ${regBtn}
          <button class="btn btn-ghost" style="padding:3px 8px;font-size:11px" onclick="dmPing(${d.id},'${ip}')">◎ Ping</button>
          <button class="btn btn-ghost" style="padding:3px 8px;font-size:11px" onclick="dmEditModal(${d.id})">✎ Edit</button>
          <button class="del-btn" onclick="dmRemove(${d.id})" title="Remove device">✕</button>
        </div>
      </td>
    </tr>`;
  }).join('') : `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">⊡</div>
    No devices discovered yet.<br><span style="font-size:11px;color:var(--dim)">Enable tracking to auto-discover devices from DNS queries, or add manually below.</span>
    </div></td></tr>`;

  return `
  <!-- Tracking Control Card -->
  <div class="card">
    <div class="card-title"><span class="ct-icon">◉</span> DNS Query Tracking &nbsp;${trackBadge}</div>
    <div class="card-sub">
      Device discovery uses three sources: BIND9 query logs, the network ARP table, and DHCP leases.
      The ARP table is scanned on every pass regardless of whether BIND9 logging is enabled —
      so <strong>Scan Now</strong> will find devices that have communicated on the network even without tracking active.
    </div>
    ${diagHtml}
    <div class="info-box" style="margin-top:10px">
      <strong>How DNS controls work:</strong>
      Registered devices get an A record in your local zone.
      Blocked devices have their IP added to BIND9's <span class="inline-code">blackhole</span> ACL —
      their DNS queries are silently dropped, effectively cutting off internet access for anything
      that depends on DNS resolution.
    </div>
    <div class="btn-row">
      ${trackOn
        ? `<button class="btn btn-danger"  onclick="dmTrackingDisable()">⊘ Disable Tracking</button>
           <button class="btn btn-ghost"   onclick="dmScan()">↺ Scan Now</button>`
        : `<button class="btn btn-success" onclick="dmTrackingEnable()">⬡ Enable Tracking</button>
           <button class="btn btn-ghost"   onclick="dmScan()">↺ Scan Now (ARP)</button>`
      }
    </div>
  </div>

  <!-- Device Table -->
  <div class="card" style="margin-top:4px">
    <div class="card-title"><span class="ct-icon">⊞</span> Discovered Devices (${devices.length})</div>
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr>
            <th>LABEL / NAME</th><th>IP ADDRESS</th><th>MAC</th>
            <th>LAST SEEN</th><th style="text-align:center">QUERIES</th><th>STATUS</th><th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </div>

  <!-- Add Device Manually -->
  <div class="card" style="margin-top:4px">
    <div class="card-title"><span class="ct-icon">⊕</span> Add Device Manually</div>
    <div class="form-grid-3">
      <div class="form-row"><label>IP ADDRESS</label><input id="dm-add-ip" placeholder="192.168.1.42"></div>
      <div class="form-row"><label>LABEL</label><input id="dm-add-label" placeholder="Living Room TV"></div>
      <div class="form-row"><label>HOSTNAME</label><input id="dm-add-host" placeholder="tv"></div>
    </div>
    <div class="form-grid-2">
      <div class="form-row"><label>MAC ADDRESS (optional)</label><input id="dm-add-mac" placeholder="aa:bb:cc:dd:ee:ff"></div>
      <div class="form-row"><label>NOTES (optional)</label><input id="dm-add-notes" placeholder="Smart TV in living room"></div>
    </div>
    <button class="btn btn-primary" onclick="dmAddManual()">+ Add Device</button>
  </div>

  <!-- Edit Modal (hidden) -->
  <div id="dm-edit-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:900;align-items:center;justify-content:center">
    <div class="card" style="width:420px;max-width:95vw;z-index:901">
      <div class="card-title">✎ Edit Device</div>
      <div class="form-row"><label>LABEL</label><input id="dm-ed-label" placeholder="My Device"></div>
      <div class="form-row"><label>HOSTNAME</label><input id="dm-ed-hostname" placeholder="mydevice"></div>
      <div class="form-row"><label>MAC ADDRESS</label><input id="dm-ed-mac" placeholder="aa:bb:cc:dd:ee:ff"></div>
      <div class="form-row"><label>NOTES</label><textarea id="dm-ed-notes" rows="2" style="width:100%;background:var(--input-bg);border:1px solid var(--border);color:var(--fg);padding:8px;border-radius:4px;font-family:var(--mono);font-size:12px;resize:vertical"></textarea></div>
      <div class="btn-row">
        <button class="btn btn-primary" onclick="dmEditSave()">Save</button>
        <button class="btn btn-ghost"   onclick="dmCloseModal()">Cancel</button>
      </div>
    </div>
  </div>

  <!-- Register Modal (hidden) -->
  <div id="dm-reg-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:900;align-items:center;justify-content:center">
    <div class="card" style="width:380px;max-width:95vw;z-index:901">
      <div class="card-title">⊕ Register DNS Hostname</div>
      <div class="card-sub">Creates an A record in your local zone pointing this device's IP to the hostname you choose.</div>
      <div class="form-row"><label>HOSTNAME</label><input id="dm-reg-hostname" placeholder="tv"></div>
      <div id="dm-reg-preview" style="font-size:11px;color:var(--dim);margin-top:4px"></div>
      <div class="btn-row" style="margin-top:12px">
        <button class="btn btn-primary" onclick="dmRegisterSave()">Register</button>
        <button class="btn btn-ghost"   onclick="dmCloseRegModal()">Cancel</button>
      </div>
    </div>
  </div>

  <style>
    .dm-row-blocked td { opacity:.6; }
    #dm-edit-modal.open,
    #dm-reg-modal.open  { display:flex !important; }
  </style>`;
}

// ─── Device Manager Actions ──────────────────────────────────────────────
async function dmTrackingEnable() {
  if (!await confirmAction('Enable BIND9 query logging? This adds a logging block to named.conf.local and reloads BIND9.')) return;
  try {
    await api('POST','/devices/tracking/enable');
    toast('Device tracking enabled — BIND9 reloading', 'success');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 2500);
  } catch(e) { toast(e.message,'error'); }
}
async function dmTrackingDisable() {
  if (!await confirmAction('Disable device tracking and remove BIND9 query logging?')) return;
  try {
    await api('POST','/devices/tracking/disable');
    toast('Device tracking disabled', 'info');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 1500);
  } catch(e) { toast(e.message,'error'); }
}
async function dmScan() {
  toast('Scanning ARP table and query log…', 'info');
  try {
    const r = await api('POST','/devices/scan');
    const msg = r.new
      ? `Found ${r.new} new device(s), ${r.updated} updated`
      : r.updated
        ? `${r.updated} existing device(s) refreshed (no new ones)`
        : 'Scan complete — no devices found yet. Are any devices on the network?';
    toast(msg, r.new ? 'success' : 'info');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 1000);
  } catch(e) { toast(e.message,'error'); }
}
async function dmBlock(id) {
  const d = _dmDevices.find(x=>x.id===id);
  const name = d ? (d.label||d.hostname||d.ip) : id;
  if (!await confirmAction(`Block all DNS queries from "${name}"? This will cut off their internet access.`)) return;
  try {
    await api('POST',`/devices/${id}/block`);
    toast(`DNS blocked for ${name}`, 'warn');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 2000);
  } catch(e) { toast(e.message,'error'); }
}
async function dmUnblock(id) {
  const d = _dmDevices.find(x=>x.id===id);
  const name = d ? (d.label||d.hostname||d.ip) : id;
  try {
    await api('POST',`/devices/${id}/unblock`);
    toast(`DNS unblocked for ${name}`, 'success');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 2000);
  } catch(e) { toast(e.message,'error'); }
}
async function dmPing(id, ip) {
  toast(`Pinging ${ip}…`, 'info');
  try {
    const r = await api('POST',`/devices/${id}/ping`);
    if (r.alive) {
      toast(`${ip} is reachable${r.rtt ? ' — RTT: ' + r.rtt + ' ms' : ''}`, 'success');
    } else {
      toast(`${ip} did not respond`, 'warn');
    }
  } catch(e) { toast(e.message,'error'); }
}
async function dmRemove(id) {
  const d = _dmDevices.find(x=>x.id===id);
  const name = d ? (d.label||d.hostname||d.ip) : id;
  if (!await confirmAction(`Remove "${name}" from the device registry? DNS records are not removed automatically.`)) return;
  try {
    await api('DELETE',`/devices/${id}`);
    toast(`Device removed: ${name}`, 'info');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 800);
  } catch(e) { toast(e.message,'error'); }
}
async function dmAddManual() {
  const ip    = document.getElementById('dm-add-ip')?.value?.trim();
  const label = document.getElementById('dm-add-label')?.value?.trim();
  const host  = document.getElementById('dm-add-host')?.value?.trim();
  const mac   = document.getElementById('dm-add-mac')?.value?.trim();
  const notes = document.getElementById('dm-add-notes')?.value?.trim();
  if (!ip) { toast('IP address required','error'); return; }
  try {
    await api('POST','/devices',{ip,label,hostname:host,mac,notes});
    toast(`Device ${label||ip} added`, 'success');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 600);
  } catch(e) { toast(e.message,'error'); }
}
function dmEditModal(id) {
  const d = _dmDevices.find(x=>x.id===id);
  if (!d) return;
  _dmEditId = id;
  document.getElementById('dm-ed-label').value    = d.label    || '';
  document.getElementById('dm-ed-hostname').value = d.hostname || '';
  document.getElementById('dm-ed-mac').value      = d.mac      || '';
  document.getElementById('dm-ed-notes').value    = d.notes    || '';
  document.getElementById('dm-edit-modal').classList.add('open');
}
function dmCloseModal() {
  document.getElementById('dm-edit-modal').classList.remove('open');
  _dmEditId = null;
}
async function dmEditSave() {
  if (!_dmEditId) return;
  const label    = document.getElementById('dm-ed-label').value.trim();
  const hostname = document.getElementById('dm-ed-hostname').value.trim();
  const mac      = document.getElementById('dm-ed-mac').value.trim();
  const notes    = document.getElementById('dm-ed-notes').value.trim();
  try {
    await api('PUT',`/devices/${_dmEditId}`,{label,hostname,mac,notes});
    toast('Device updated','success');
    dmCloseModal();
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 500);
  } catch(e) { toast(e.message,'error'); }
}
function dmRegisterModal(id) {
  const d = _dmDevices.find(x=>x.id===id);
  if (!d) return;
  _dmEditId = id;
  const suggested = (d.hostname || (d.label||'').toLowerCase().replace(/[^a-z0-9]/g,'-').replace(/-+/g,'-') || '').slice(0,40);
  document.getElementById('dm-reg-hostname').value = suggested;
  document.getElementById('dm-reg-preview').textContent = suggested
    ? `Will create: ${suggested}.${S.status.domain||'localnet'} → ${d.ip}`
    : '';
  document.getElementById('dm-reg-modal').classList.add('open');
  document.getElementById('dm-reg-hostname').oninput = function() {
    const h = this.value.trim();
    document.getElementById('dm-reg-preview').textContent = h
      ? `Will create: ${h}.${S.status.domain||'localnet'} → ${d.ip}`
      : '';
  };
}
function dmCloseRegModal() {
  document.getElementById('dm-reg-modal').classList.remove('open');
  _dmEditId = null;
}
async function dmRegisterSave() {
  if (!_dmEditId) return;
  const hostname = document.getElementById('dm-reg-hostname').value.trim();
  if (!hostname) { toast('Hostname required','error'); return; }
  try {
    await api('POST',`/devices/${_dmEditId}/register`,{hostname});
    toast(`Registering ${hostname} in DNS…`, 'info');
    dmCloseRegModal();
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 2200);
  } catch(e) { toast(e.message,'error'); }
}
async function dmUnregister(id) {
  const d = _dmDevices.find(x=>x.id===id);
  const name = d ? (d.label||d.hostname||d.ip) : id;
  if (!await confirmAction(`Remove DNS record for "${name}"?`)) return;
  try {
    await api('POST',`/devices/${id}/unregister`);
    toast('DNS record removed', 'info');
    setTimeout(()=>{ S.activeTab['dns']='devices'; pgDNS(); }, 2000);
  } catch(e) { toast(e.message,'error'); }
}

// ─── DNS Page: wire up new records tab ────────────────────────────────────
async function pgDNS() {
  const tab = getTab('dns', 'setup');
  let html = tabBar('dns',[['setup','Setup'],['records','Records'],['devices','Device Manager'],['test','Test']],tab);
  if (tab === 'setup') html += await dnsSetupHtml();
  else if (tab === 'records') html += await dnsRecordsHtml_v4();
  else if (tab === 'devices') html += await dnsDeviceManagerHtml();
  else html += dnsTestHtml();
  document.getElementById('content').innerHTML = html;
  if (tab === 'setup') initDNSSetup();
}

// ─── Init ─────────────────────────────────────────────────────────────────
// Stop journal stream when navigating away
// 1. Capture the original function reference
const _origNavigate = navigate;

// 2. Redefine 'navigate' with your extra logic
navigate = function(page) {
    console.log("Intercepted navigation to:", page);
    
    // Stop logs if leaving the logs page
    if (page !== 'logs') {
        if (typeof stopJournalStream === 'function') stopJournalStream();
    }
    
    // 3. Call the original logic
    _origNavigate(page);
};
refreshStatus();
navigate('dashboard');
setInterval(refreshStatus, 8000);
</script>
</body>
</html>"""

# ─── Login Page HTML ──────────────────────────────────────────────────────────
LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LocalNet — Login</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700&family=Fira+Code&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#080b11;display:flex;align-items:center;justify-content:center;font-family:'Barlow',sans-serif}
.login-wrap{width:360px}
.login-logo{text-align:center;margin-bottom:32px}
.login-logo-mark{font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:700;color:#00d4ff;letter-spacing:.5px}
.login-logo-sub{font-size:11px;color:#4e5d7a;font-family:'Fira Code',monospace;letter-spacing:2px;margin-top:4px}
.login-card{background:#0d1018;border:1px solid #232b3e;border-radius:8px;padding:32px}
.login-card h2{font-family:'Barlow Condensed',sans-serif;font-size:18px;color:#c2ceea;margin-bottom:6px}
.login-card p{font-size:12px;color:#4e5d7a;margin-bottom:24px}
label{display:block;font-size:11px;font-weight:600;color:#4e5d7a;letter-spacing:.8px;font-family:'Barlow Condensed',sans-serif;margin-bottom:5px}
input[type=password]{width:100%;background:#181d2a;border:1px solid #232b3e;color:#c2ceea;font-family:'Fira Code',monospace;font-size:13px;padding:10px 12px;border-radius:4px;outline:none;margin-bottom:18px;transition:border-color .15s}
input[type=password]:focus{border-color:#00d4ff}
.login-btn{width:100%;padding:11px;background:#4a9eff;color:#fff;border:none;border-radius:4px;font-family:'Barlow',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:background .15s}
.login-btn:hover{background:#5aadff}
.login-err{background:rgba(255,77,106,.1);border:1px solid rgba(255,77,106,.3);color:#ff4d6a;font-size:12px;padding:9px 12px;border-radius:4px;margin-bottom:16px}
.login-hint{text-align:center;font-size:11px;color:#374158;margin-top:14px;font-family:'Fira Code',monospace}
</style>
</head>
<body>
<div class="login-wrap">
  <div class="login-logo">
    <div class="login-logo-mark">⬡ LocalNet Manager</div>
    <div class="login-logo-sub">v4 &nbsp;·&nbsp; SECURE ACCESS</div>
  </div>
  <div class="login-card">
    <h2>Sign in</h2>
    <p>Enter your LocalNet Manager password to continue.</p>
    __ERROR_HTML__
    <form method="POST" action="/login">
      <label>PASSWORD</label>
      <input type="password" name="password" placeholder="••••••••" autofocus>
      <button type="submit" class="login-btn">Sign In →</button>
    </form>
    <div class="login-hint">default: localnet &nbsp;·&nbsp; change in Settings</div>
  </div>
</div>
</body>
</html>"""

# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    db_init()
    init_app_secret()

    # Auto-resume device tracking if BIND9 query logging is already configured
    for _conf in [Path("/etc/bind/named.conf.local"), Path("/etc/bind/named.conf")]:
        try:
            if "localnet_query_log" in _conf.read_text():
                start_device_tracking()
                break
        except Exception:
            pass

    port = 8091
    host = '0.0.0.0'
    print(f"""
  ⬡  LocalNet Manager v4
  ─────────────────────────────
  Web UI:  http://localhost:{port}
  {"Root: YES ✔" if is_root() else "Root: NO — run with sudo for full functionality"}
  ─────────────────────────────
  Default password: localnet
  Change it in Settings after first login.
  Press Ctrl+C to stop.
""")
    log("LocalNet Manager v4 started", "success")
    log(f"Server IP: {get_local_ip() or '(not detected)'}")
    app.run(host=host, port=port, debug=False, threaded=True)