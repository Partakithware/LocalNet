# ⬡ LocalNet Manager

A clean, dark-themed Python GUI for running a private local DNS server and Nginx reverse proxy on your home or lab network — with **full VPN compatibility** built in.

Replaces a collection of shell scripts with a single desktop app. No browser required, no Docker, no cloud.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%2F%20Debian-orange?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Root](https://img.shields.io/badge/Requires-sudo-red?style=flat-square)

---

## What It Does

LocalNet Manager lets you run your own DNS server on your local machine so every device on your network can reach services by name instead of IP.

```
nas.localnet      →  192.168.1.20
movies.localnet   →  127.0.0.1:8096   (via Nginx proxy)
pi.localnet       →  192.168.1.50
```

All managed through a GUI — no terminal, no manual config file editing.

---

## Features

| Tab | What you can do |
|-----|----------------|
| **DNS Setup** | Install / uninstall BIND9, auto-detects your IP, VPN-safe mode toggle |
| **DNS Records** | Add A records, add CNAMEs, remove records, quick `dig` test |
| **Nginx** | Install / uninstall Nginx, add / remove reverse proxy configs |
| **System Status** | Live service health indicators, resolv.conf viewer, reload buttons |
| **Output Log** | Every command and its full output streams in real time |

---

## VPN-Compatible Mode

This is the most important feature and is **on by default**.

### The Problem

The standard way to set up a local DNS server points `/etc/resolv.conf` directly at `127.0.0.1` (BIND9). When a VPN connects, it tries to push its own DNS servers through NetworkManager — but the system ignores them because the nameserver is hardcoded to localhost. Result: **VPN DNS breaks**, split-tunnel stops working, and you often need to reinstall your VPN client to recover.

### The Fix

VPN-safe mode routes through `systemd-resolved` as the middle layer:

```
/etc/resolv.conf  →  127.0.0.53  (systemd-resolved stub)
                          │
                          ├── *.localnet  →  127.0.0.1 (BIND9)   ✔ your local names
                          └── everything else  →  VPN DNS / upstream   ✔ VPN works
```

A drop-in config at `/etc/systemd/resolved.conf.d/localnet.conf` tells resolved to only forward `.localnet` queries to BIND9. All other DNS — including whatever your VPN pushes — flows through resolved normally.

**Your `/etc/resolv.conf` ends up as a symlink to the resolved-managed stub:**

```
# This is /run/systemd/resolve/stub-resolv.conf managed by systemd-resolved(8).
nameserver 127.0.0.53
options edns0 trust-ad
search .
```

---

## Requirements

### System

| Requirement | Notes |
|-------------|-------|
| Ubuntu 22.04+ or Debian 11+ | `systemd-resolved` must be present |
| Python 3.8+ | Usually pre-installed |
| `tkinter` | See install note below |
| `sudo` / root access | Required for all DNS and Nginx operations |
| Internet connection | Required during BIND9 / Nginx install only |

### Python Libraries

LocalNet Manager uses **only the Python standard library** — no `pip install` needed.

| Module | Source |
|--------|--------|
| `tkinter` | Standard library (requires system package — see below) |
| `ttk` | Included with tkinter |
| `subprocess` | Standard library |
| `threading` | Standard library |
| `pathlib` | Standard library |
| `socket` | Standard library |
| `glob` | Standard library |
| `textwrap` | Standard library |
| `os` | Standard library |
| `datetime` | Standard library |

### Installing tkinter

`tkinter` ships with Python but requires a system package on Linux:

```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Verify it works
python3 -c "import tkinter; tkinter._test()"
```

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/Partakithware/LocalNet.git
cd LocalNet

# 2. Install tkinter if you haven't already
sudo apt install python3-tk

# 3. Run (root required)
sudo python3 localnet_manager.py
```

> **Why sudo?** The app writes to `/etc/bind/`, `/etc/nginx/`, `/etc/systemd/`, and controls systemd services. These all require root. The GUI itself will launch fine as your normal user but all action buttons will error without root.

---

## Usage

### 1 — Install DNS

1. Open the **DNS Setup** tab
2. Your local IP is auto-detected in the Server IP field
3. Leave **VPN-compatible mode** checked (recommended)
4. Click **Install & Configure DNS**
5. Watch the output log — it runs all 7 steps and reports success

### 2 — Add Your Devices

Switch to the **DNS Records** tab:

- **Add A Record** — give it a hostname (e.g. `nas`) and an IP (e.g. `192.168.1.20`). This creates both a forward record (`nas.localnet → 192.168.1.20`) and a reverse PTR record automatically.
- **Add CNAME** — create an alias pointing to an existing hostname (e.g. `movies → ns1`)
- **Remove Record** — deletes forward and reverse entries for a hostname
- **Quick DNS Test** — runs a `dig` lookup against your server to verify resolution

Every record change automatically updates the zone serial and reloads BIND9.

### 3 — Set Up Nginx (optional)

If you want browser-friendly names to route to local services running on specific ports:

1. Go to the **Nginx** tab
2. Click **Install Nginx**
3. Enter a domain (e.g. `movies.localnet`) and the port your service runs on (e.g. `8096`)
4. Click **Add Proxy**

You'll also need an A record pointing that domain to your server's IP (step 2 above).

### 4 — Point Your Router at the DNS Server

For all LAN devices to use your new DNS server automatically, log into your router and set the **DHCP DNS server** to the IP address shown in the DNS Setup tab. Devices will pick it up on their next DHCP lease renewal (or you can reconnect them manually).

### 5 — Monitor Services

The **System Status** tab shows live indicators for BIND9, Nginx, and systemd-resolved. Use the **Reload** buttons after manual config edits, or **Refresh Status** to update the indicators.

---

## What Gets Installed / Where

| Path | What it is |
|------|-----------|
| `/etc/bind/` | BIND9 config and zone files |
| `/etc/bind/named.conf.options` | ACL, forwarders, recursion settings |
| `/etc/bind/named.conf.local` | Forward and reverse zone declarations |
| `/etc/bind/db.localnet` | Forward zone (hostname → IP records) |
| `/etc/bind/db.x.x.x` | Reverse zone (IP → hostname PTR records) |
| `/etc/systemd/resolved.conf.d/localnet.conf` | Tells resolved to forward `.localnet` to BIND9 |
| `/etc/resolv.conf` | Symlinked to `/run/systemd/resolve/stub-resolv.conf` |
| `/etc/nginx/sites-available/<domain>` | Nginx proxy config per service |
| `/etc/nginx/sites-enabled/<domain>` | Symlink to activate the config |

---

## Uninstalling

### Remove DNS only
Go to **DNS Setup → Remove DNS (BIND9)**. This:
- Stops and purges BIND9
- Removes `/etc/bind/`, `/var/cache/bind/`, `/var/lib/bind/`
- Removes the resolved drop-in config
- Restores `/etc/resolv.conf` to the resolved stub (internet access preserved)

### Remove Nginx only
Go to **Nginx → Uninstall Nginx**. This purges Nginx and removes all config files.

### Both
Run both removals in either order.

---

## Upstream DNS Forwarders

By default, BIND9 is configured to forward non-local queries to **Cloudflare for Families**, which blocks known malware and phishing domains at the DNS level:

```
1.1.1.2   (Cloudflare for Families — primary)
1.0.0.2   (Cloudflare for Families — secondary)
```

To use standard Cloudflare or Google DNS instead, edit `/etc/bind/named.conf.options` and change the forwarder IPs, then reload BIND9 from the System Status tab.

---

## Troubleshooting

**The app opens but buttons do nothing / show errors**
Run with `sudo python3 localnet_manager.py`. Root is required.

**`ModuleNotFoundError: No module named 'tkinter'`**
```bash
sudo apt install python3-tk
```

**DNS resolves locally but not from other devices**
Your router's DHCP DNS setting still points elsewhere. Set it to this machine's IP.

**VPN stopped working after DNS install**
Make sure VPN-compatible mode was enabled. If you installed without it, re-run the install with the toggle checked — it will overwrite the configuration correctly.

**`dig` test returns no answer**
Check that BIND9 is running (System Status tab). If it shows inactive, check:
```bash
sudo journalctl -xe -u bind9
sudo named-checkconf
```

**Nginx config test fails on add proxy**
The domain you entered may already have a conflicting config. Remove it first, then re-add.

---

## License

MIT — do whatever you want with it.
