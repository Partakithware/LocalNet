#!/usr/bin/env python3
"""
LocalNet Manager — GUI for BIND9 DNS & Nginx management.
VPN-safe by default: uses systemd-resolved as the stub resolver so
VPN clients can still inject their own DNS without conflicts.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess, threading, os, glob, socket, textwrap
from datetime import datetime
from pathlib import Path

# ─── Constants ──────────────────────────────────────────────────────────────
DOMAIN     = "localnet"
ZONE_FILE  = f"/etc/bind/db.{DOMAIN}"
APP_TITLE  = "LocalNet Manager"
APP_W, APP_H = 900, 680

# ─── Palette (dark industrial) ───────────────────────────────────────────────
BG        = "#0f1117"
BG2       = "#181c27"
BG3       = "#1e2333"
SURFACE   = "#242938"
BORDER    = "#2e364d"
FG        = "#d4daf0"
FG_DIM    = "#6b748f"
ACCENT    = "#4f8ef7"
ACCENT2   = "#34c98e"
DANGER    = "#e05c5c"
WARN      = "#e8a950"
LOG_BG    = "#090c12"
LOG_FG    = "#7ecf9f"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10) if os.name == "nt" else ("DejaVu Sans", 10)
FONT_H    = ("Segoe UI", 11, "bold") if os.name == "nt" else ("DejaVu Sans", 11, "bold")
FONT_BIG  = ("Segoe UI", 13, "bold") if os.name == "nt" else ("DejaVu Sans", 13, "bold")

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""

def find_reverse_file() -> str:
    matches = glob.glob("/etc/bind/db.*.*.*")
    for m in matches:
        if "localnet" not in m:
            return m
    return ""

def is_root() -> bool:
    return os.geteuid() == 0

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

# ─── Main Application ─────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{APP_W}x{APP_H}")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(800, 600)

        self._build_style()
        self._build_layout()

        if not is_root():
            self.log("⚠  Not running as root — most actions will fail.\n"
                     "   Launch with: sudo python3 localnet_manager.py", color=WARN)
        else:
            self.log("✔  Running as root. All actions available.", color=ACCENT2)
        self.log(f"   Detected local IP: {get_local_ip() or '(not found)'}\n")
        self._refresh_status()

    # ─── Style ───────────────────────────────────────────────────────────────
    def _build_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook",             background=BG,  borderwidth=0)
        s.configure("TNotebook.Tab",         background=SURFACE, foreground=FG_DIM,
                                              padding=[16, 8], font=FONT_UI, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", BG2), ("active", BG3)],
              foreground=[("selected", ACCENT), ("active", FG)])
        s.configure("TFrame",                background=BG2)
        s.configure("TLabel",                background=BG2, foreground=FG, font=FONT_UI)
        s.configure("TEntry",                fieldbackground=SURFACE, foreground=FG,
                                              insertcolor=FG, borderwidth=1, relief="flat")
        s.configure("TCombobox",             fieldbackground=SURFACE, foreground=FG,
                                              background=SURFACE)
        s.configure("TCheckbutton",          background=BG2, foreground=FG, font=FONT_UI)
        s.configure("TLabelframe",           background=BG2, foreground=FG_DIM, font=FONT_UI,
                                              bordercolor=BORDER, relief="flat")
        s.configure("TLabelframe.Label",     background=BG2, foreground=FG_DIM)
        s.configure("TSeparator",            background=BORDER)
        # Custom button styles
        for name, bg, fg, abg in [
            ("Accent.TButton",  ACCENT,  "#fff", "#3a7aeb"),
            ("Danger.TButton",  DANGER,  "#fff", "#c94444"),
            ("Success.TButton", ACCENT2, "#111", "#28b07d"),
            ("Warn.TButton",    WARN,    "#111", "#d09030"),
            ("Dim.TButton",     SURFACE, FG,    BORDER),
        ]:
            s.configure(name, background=bg, foreground=fg, font=FONT_UI,
                        borderwidth=0, focusthickness=0, padding=[14, 7])
            s.map(name, background=[("active", abg), ("pressed", abg)])

    # ─── Layout ──────────────────────────────────────────────────────────────
    def _build_layout(self):
        # Header bar
        hdr = tk.Frame(self, bg=BG3, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⬡ LocalNet Manager", bg=BG3, fg=ACCENT,
                 font=FONT_BIG).pack(side="left", padx=20, pady=12)
        self.status_dot = tk.Label(hdr, text="●", bg=BG3, fg=FG_DIM, font=("", 14))
        self.status_dot.pack(side="right", padx=6, pady=12)
        self.status_lbl = tk.Label(hdr, text="Checking…", bg=BG3, fg=FG_DIM, font=FONT_UI)
        self.status_lbl.pack(side="right", padx=2, pady=12)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = [
            ("  DNS Setup  ",    self._tab_dns_setup),
            ("  DNS Records  ",  self._tab_dns_records),
            ("  Nginx  ",        self._tab_nginx),
            ("  System Status  ",self._tab_status),
        ]
        for label, builder in tabs:
            frame = ttk.Frame(nb)
            nb.add(frame, text=label)
            builder(frame)

        # Log panel
        log_outer = tk.Frame(self, bg=BG, height=180)
        log_outer.pack(fill="x", side="bottom")
        log_outer.pack_propagate(False)

        log_head = tk.Frame(log_outer, bg=SURFACE, height=26)
        log_head.pack(fill="x")
        log_head.pack_propagate(False)
        tk.Label(log_head, text="OUTPUT LOG", bg=SURFACE, fg=FG_DIM,
                 font=("Courier New", 9, "bold")).pack(side="left", padx=10)
        ttk.Button(log_head, text="Clear", style="Dim.TButton",
                   command=self._clear_log).pack(side="right", padx=6, pady=1)

        self.log_box = scrolledtext.ScrolledText(
            log_outer, bg=LOG_BG, fg=LOG_FG, font=FONT_MONO,
            insertbackground=LOG_FG, relief="flat", borderwidth=0,
            state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_configure("warn",    foreground=WARN)
        self.log_box.tag_configure("error",   foreground=DANGER)
        self.log_box.tag_configure("success", foreground=ACCENT2)
        self.log_box.tag_configure("info",    foreground=ACCENT)
        self.log_box.tag_configure("dim",     foreground=FG_DIM)

    # ─── Tab: DNS Setup ───────────────────────────────────────────────────────
    def _tab_dns_setup(self, parent):
        pad = dict(padx=20, pady=10)
        ip = get_local_ip()

        # Info card
        card = tk.Frame(parent, bg=BG3, bd=0)
        card.pack(fill="x", padx=20, pady=(16, 4))

        tk.Label(card, text="BIND9 Local DNS", bg=BG3, fg=ACCENT, font=FONT_BIG
                 ).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(card, text="Installs and configures a local authoritative DNS server for\n"
                 f"the .{DOMAIN} domain. All LAN devices resolve hostnames automatically.",
                 bg=BG3, fg=FG_DIM, font=FONT_UI, justify="left"
                 ).pack(anchor="w", padx=16, pady=(0, 12))

        # Fields
        fields = ttk.LabelFrame(parent, text="  Configuration", padding=16)
        fields.pack(fill="x", padx=20, pady=8)

        self._field(fields, "Domain", 0, readonly_val=DOMAIN)
        self.dns_ip_var = tk.StringVar(value=ip)
        self._field(fields, "Server IP (auto-detected)", 1, var=self.dns_ip_var, readonly=True)

        # VPN-safe toggle (default ON)
        vpn_row = ttk.Frame(fields)
        vpn_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.vpn_safe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vpn_row, text="VPN-compatible mode  (recommended)",
                        variable=self.vpn_safe_var).pack(side="left")
        tk.Label(vpn_row, text="  → Routes through systemd-resolved so VPNs can still inject their DNS",
                 bg=BG2, fg=FG_DIM, font=("", 9)).pack(side="left")

        # Buttons
        btn_row = tk.Frame(parent, bg=BG2)
        btn_row.pack(fill="x", padx=20, pady=8)
        ttk.Button(btn_row, text="⬡  Install & Configure DNS",
                   style="Accent.TButton",
                   command=self._run_dns_install).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="✕  Remove DNS (BIND9)",
                   style="Danger.TButton",
                   command=self._run_dns_remove).pack(side="left")

        # VPN explanation box
        vpn_card = tk.Frame(parent, bg="#131820", bd=0)
        vpn_card.pack(fill="x", padx=20, pady=(4, 0))
        lines = [
            ("WHY VPN-COMPATIBLE MODE?", ACCENT, FONT_H),
            ("Standard setup: /etc/resolv.conf → 127.0.0.1 (BIND9 directly)", FG_DIM, FONT_MONO),
            ("  VPN tries to push its DNS → system ignores it → VPN DNS broken", DANGER, FONT_MONO),
            ("", FG_DIM, FONT_MONO),
            ("VPN-safe setup:  /etc/resolv.conf → 127.0.0.53 (systemd-resolved)", ACCENT2, FONT_MONO),
            ("  ↳ resolved forwards .localnet → BIND9   (your local names work)", ACCENT2, FONT_MONO),
            ("  ↳ VPN pushes its DNS into resolved normally   (VPN works too  ✔)", ACCENT2, FONT_MONO),
        ]
        for txt, col, fnt in lines:
            tk.Label(vpn_card, text=txt, bg="#131820", fg=col, font=fnt,
                     anchor="w").pack(fill="x", padx=16, pady=1)
        tk.Label(vpn_card, text="", bg="#131820").pack(pady=4)

    # ─── Tab: DNS Records ─────────────────────────────────────────────────────
    def _tab_dns_records(self, parent):
        lp = dict(padx=20, pady=10)

        # ── Add A Record ──────────────────────────────────────────────────────
        af = ttk.LabelFrame(parent, text="  Add A Record  (hostname → IP)", padding=16)
        af.pack(fill="x", padx=20, pady=(16, 8))

        self.a_host = tk.StringVar()
        self.a_ip   = tk.StringVar()
        self._field(af, "Hostname  (e.g. nas)", 0, var=self.a_host, ph="nas")
        self._field(af, "IP Address",           1, var=self.a_ip,   ph="192.168.1.50")
        ttk.Button(af, text="+ Add A Record", style="Accent.TButton",
                   command=self._add_a_record).grid(row=2, column=1, sticky="w", pady=(10, 0))

        # ── Add CNAME ─────────────────────────────────────────────────────────
        cf = ttk.LabelFrame(parent, text="  Add CNAME  (alias → existing host)", padding=16)
        cf.pack(fill="x", padx=20, pady=8)

        self.cn_alias  = tk.StringVar()
        self.cn_target = tk.StringVar()
        self._field(cf, "Alias      (e.g. movies)", 0, var=self.cn_alias,  ph="movies")
        self._field(cf, "Target     (e.g. ns1)",    1, var=self.cn_target, ph="ns1")
        ttk.Button(cf, text="+ Add CNAME", style="Accent.TButton",
                   command=self._add_cname).grid(row=2, column=1, sticky="w", pady=(10, 0))

        # ── Remove Record ─────────────────────────────────────────────────────
        rf = ttk.LabelFrame(parent, text="  Remove Record", padding=16)
        rf.pack(fill="x", padx=20, pady=8)

        self.rm_host = tk.StringVar()
        self._field(rf, "Hostname to remove", 0, var=self.rm_host, ph="nas")
        ttk.Button(rf, text="✕  Remove", style="Danger.TButton",
                   command=self._remove_record).grid(row=1, column=1, sticky="w", pady=(10, 0))

        # ── Quick Test ────────────────────────────────────────────────────────
        tf = ttk.LabelFrame(parent, text="  Quick DNS Test", padding=16)
        tf.pack(fill="x", padx=20, pady=8)

        self.test_host = tk.StringVar(value=f"ns1.{DOMAIN}")
        self._field(tf, "Lookup name", 0, var=self.test_host)
        ttk.Button(tf, text="↗  Test Lookup", style="Warn.TButton",
                   command=self._dns_test).grid(row=1, column=1, sticky="w", pady=(10, 0))

    # ─── Tab: Nginx ───────────────────────────────────────────────────────────
    def _tab_nginx(self, parent):
        # Install card
        ic = tk.Frame(parent, bg=BG3)
        ic.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(ic, text="Nginx Reverse Proxy", bg=BG3, fg=ACCENT2, font=FONT_BIG
                 ).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(ic, text="Lightweight proxy so browser-friendly names like\n"
                 "mediajungle.localnet route to a local port.",
                 bg=BG3, fg=FG_DIM, font=FONT_UI, justify="left"
                 ).pack(anchor="w", padx=16, pady=(0, 12))

        btn_row = tk.Frame(parent, bg=BG2)
        btn_row.pack(fill="x", padx=20, pady=4)
        ttk.Button(btn_row, text="⬡  Install Nginx", style="Success.TButton",
                   command=self._nginx_install).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="✕  Uninstall Nginx", style="Danger.TButton",
                   command=self._nginx_uninstall).pack(side="left")

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=20, pady=12)

        # Add proxy
        pf = ttk.LabelFrame(parent, text="  Add Reverse Proxy", padding=16)
        pf.pack(fill="x", padx=20, pady=8)

        self.ng_domain = tk.StringVar()
        self.ng_port   = tk.StringVar()
        self._field(pf, "Domain name  (e.g. movies.localnet)", 0,
                    var=self.ng_domain, ph="movies.localnet")
        self._field(pf, "Port         (e.g. 8096)",            1,
                    var=self.ng_port,   ph="8096")
        ttk.Button(pf, text="+ Add Proxy", style="Accent.TButton",
                   command=self._nginx_add).grid(row=2, column=1, sticky="w", pady=(10, 0))

        # Remove proxy
        rp = ttk.LabelFrame(parent, text="  Remove Proxy", padding=16)
        rp.pack(fill="x", padx=20, pady=8)

        self.ng_rm = tk.StringVar()
        self._field(rp, "Domain to remove", 0, var=self.ng_rm, ph="movies.localnet")
        ttk.Button(rp, text="✕  Remove", style="Danger.TButton",
                   command=self._nginx_remove).grid(row=1, column=1, sticky="w", pady=(10, 0))

    # ─── Tab: System Status ───────────────────────────────────────────────────
    def _tab_status(self, parent):
        tk.Label(parent, text="Service Health", bg=BG2, fg=ACCENT, font=FONT_BIG
                 ).pack(anchor="w", padx=24, pady=(16, 8))

        grid = tk.Frame(parent, bg=BG2)
        grid.pack(fill="x", padx=20)

        services = [
            ("BIND9 (named)",  "bind9",  "named"),
            ("Nginx",          "nginx",  "nginx"),
            ("systemd-resolved","systemd-resolved","systemd-resolved"),
        ]
        self._svc_labels = {}
        for i, (label, svc, _) in enumerate(services):
            row = tk.Frame(grid, bg=SURFACE, pady=4)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=SURFACE, fg=FG, font=FONT_H, width=22,
                     anchor="w").pack(side="left", padx=14)
            dot = tk.Label(row, text="●", bg=SURFACE, fg=FG_DIM, font=("", 14))
            dot.pack(side="left")
            lbl = tk.Label(row, text="unknown", bg=SURFACE, fg=FG_DIM, font=FONT_UI)
            lbl.pack(side="left", padx=6)
            self._svc_labels[svc] = (dot, lbl)

        btn_row = tk.Frame(parent, bg=BG2)
        btn_row.pack(fill="x", padx=20, pady=12)
        ttk.Button(btn_row, text="↺  Refresh Status", style="Accent.TButton",
                   command=self._refresh_status).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="↺  Reload BIND9", style="Dim.TButton",
                   command=lambda: self._run_cmd(["systemctl", "reload", "bind9"],
                                                  success="BIND9 reloaded.")
                   ).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="↺  Reload Nginx", style="Dim.TButton",
                   command=lambda: self._run_cmd(["systemctl", "reload", "nginx"],
                                                  success="Nginx reloaded.")
                   ).pack(side="left")

        # resolv.conf viewer
        rv = ttk.LabelFrame(parent, text="  /etc/resolv.conf", padding=12)
        rv.pack(fill="x", padx=20, pady=8)
        self.resolv_lbl = tk.Label(rv, text="", bg=BG2, fg=FG, font=FONT_MONO,
                                   justify="left", anchor="w")
        self.resolv_lbl.pack(anchor="w")
        ttk.Button(rv, text="Read", style="Dim.TButton",
                   command=self._show_resolv).pack(anchor="w", pady=(4, 0))

    # ─── Widget Helpers ───────────────────────────────────────────────────────
    def _field(self, parent, label, row, var=None, ph="", readonly=False, readonly_val=""):
        tk.Label(parent, text=label, bg=BG2, fg=FG_DIM, font=FONT_UI
                 ).grid(row=row, column=0, sticky="w", padx=(0, 16), pady=4)
        if readonly or readonly_val:
            v = readonly_val or (var.get() if var else "")
            tk.Label(parent, text=v, bg=SURFACE, fg=FG, font=FONT_MONO,
                     anchor="w", width=36, relief="flat", padx=8, pady=4
                     ).grid(row=row, column=1, sticky="w", pady=4)
        else:
            e = ttk.Entry(parent, textvariable=var, width=38, font=FONT_MONO)
            e.grid(row=row, column=1, sticky="w", pady=4)
            if ph:
                e.insert(0, ph)
                e.config(foreground=FG_DIM)
                def on_focus_in(event, entry=e, placeholder=ph, v=var):
                    if entry.get() == placeholder:
                        entry.delete(0, "end")
                        entry.config(foreground=FG)
                def on_focus_out(event, entry=e, placeholder=ph, v=var):
                    if not entry.get():
                        entry.insert(0, placeholder)
                        entry.config(foreground=FG_DIM)
                        if v: v.set("")
                e.bind("<FocusIn>",  on_focus_in)
                e.bind("<FocusOut>", on_focus_out)

    # ─── Logging ─────────────────────────────────────────────────────────────
    def log(self, text, color=None):
        tag = None
        if color == WARN:    tag = "warn"
        elif color == DANGER: tag = "error"
        elif color == ACCENT2: tag = "success"
        elif color == ACCENT:  tag = "info"
        elif color == FG_DIM:  tag = "dim"

        self.log_box.configure(state="normal")
        prefix = f"[{ts()}] "
        self.log_box.insert("end", prefix, "dim")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ─── Command Runner ───────────────────────────────────────────────────────
    def _run_cmd(self, cmd, input_str=None, success=None, shell=False):
        """Run a command and stream output to the log. Returns (returncode, stdout)."""
        def worker():
            self.log(f"$ {' '.join(cmd) if not shell else cmd}", color=FG_DIM)
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, shell=shell,
                    stdin=subprocess.PIPE if input_str else None
                )
                out, _ = proc.communicate(input=input_str, timeout=120)
                for line in out.splitlines():
                    self.log("  " + line)
                if proc.returncode == 0:
                    if success:
                        self.log(f"✔  {success}", color=ACCENT2)
                    self._refresh_status()
                else:
                    self.log(f"✘  Exit code {proc.returncode}", color=DANGER)
            except Exception as ex:
                self.log(f"ERROR: {ex}", color=DANGER)
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t

    def _run_script(self, script: str, success=None):
        """Write a shell script to /tmp and run it."""
        path = "/tmp/_localnet_op.sh"
        Path(path).write_text(script)
        os.chmod(path, 0o755)
        self._run_cmd(["bash", path], success=success)

    # ─── Status Refresh ───────────────────────────────────────────────────────
    def _refresh_status(self):
        def worker():
            services = ["bind9", "nginx", "systemd-resolved"]
            for svc in services:
                try:
                    r = subprocess.run(["systemctl", "is-active", svc],
                                       capture_output=True, text=True)
                    active = r.stdout.strip() == "active"
                    dot, lbl = self._svc_labels[svc]
                    color = ACCENT2 if active else FG_DIM
                    text  = "running" if active else r.stdout.strip()
                    self.after(0, lambda d=dot, l=lbl, c=color, t=text: (
                        d.config(fg=c), l.config(fg=c, text=t)))
                except Exception:
                    pass

            # Header indicator: check if bind9 up
            try:
                r = subprocess.run(["systemctl", "is-active", "bind9"],
                                   capture_output=True, text=True)
                if r.stdout.strip() == "active":
                    self.after(0, lambda: (
                        self.status_dot.config(fg=ACCENT2),
                        self.status_lbl.config(fg=ACCENT2, text="DNS running")))
                else:
                    self.after(0, lambda: (
                        self.status_dot.config(fg=FG_DIM),
                        self.status_lbl.config(fg=FG_DIM, text="DNS offline")))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _show_resolv(self):
        try:
            text = Path("/etc/resolv.conf").read_text()
            self.resolv_lbl.config(text=text.strip())
        except Exception as e:
            self.resolv_lbl.config(text=str(e))

    # ─── DNS Install ─────────────────────────────────────────────────────────
    def _run_dns_install(self):
        if not is_root():
            messagebox.showerror("Root required", "Run this app with sudo.")
            return
        ip = get_local_ip()
        if not ip:
            messagebox.showerror("No IP", "Could not detect local IP.")
            return

        vpn_safe = self.vpn_safe_var.get()

        # Build subnet info
        parts = ip.split(".")
        octet1, octet2, octet3 = parts[0], parts[1], parts[2]
        subnet = f"{octet1}.{octet2}.{octet3}.0/24"
        rev_zone = f"{octet3}.{octet2}.{octet1}.in-addr.arpa"
        rev_file = f"/etc/bind/db.{octet1}.{octet2}.{octet3}"
        serial = "$(date +%s)"
        server_last = parts[3]
        zone_file = ZONE_FILE

        # Forwarder mode: for VPN-safe we use 'forward first' so local still resolves
        fwd_mode = "first" if vpn_safe else "only"

        script = textwrap.dedent(f"""\
        #!/bin/bash
        set -e
        DOMAIN="{DOMAIN}"
        IP_ADDR="{ip}"
        SUBNET="{subnet}"
        ZONE_FILE="{zone_file}"
        REVERSE_ZONE="{rev_zone}"
        REVERSE_ZONE_FILE="{rev_file}"
        SERIAL=$(date +%s)
        SERVER_LAST_OCTET="{server_last}"

        echo "[1/7] Installing BIND9..."
        apt-get update -qq && apt-get install -y bind9 bind9utils dnsutils

        echo "[2/7] Writing named.conf.options..."
        cat > /etc/bind/named.conf.options <<'OPTS'
        acl "trusted_network" {{
            127.0.0.1;
            {subnet};
        }};

        options {{
            directory "/var/cache/bind";
            allow-query     {{ "trusted_network"; }};
            allow-recursion {{ "trusted_network"; }};
            allow-transfer  {{ none; }};
            recursion yes;
            forwarders {{
                1.0.0.2;
                1.1.1.2;
            }};
            forward {fwd_mode};
            dnssec-validation auto;
            listen-on {{ 127.0.0.1; {ip}; }};
            listen-on-v6 {{ none; }};
        }};
        OPTS

        echo "[3/7] Writing zone declarations..."
        cat > /etc/bind/named.conf.local <<ZONES
        zone "${{DOMAIN}}" {{
            type master;
            file "${{ZONE_FILE}}";
        }};
        zone "${{REVERSE_ZONE}}" {{
            type master;
            file "${{REVERSE_ZONE_FILE}}";
        }};
        ZONES

        echo "[4/7] Writing forward zone..."
        cat > "${{ZONE_FILE}}" <<FZONE
        \$TTL 86400
        @   IN  SOA   ns1.${{DOMAIN}}. admin.${{DOMAIN}}. (
                      ${{SERIAL}} ; Serial
                      3600      ; Refresh
                      900       ; Retry
                      604800    ; Expire
                      86400 )   ; Minimum TTL
        @       IN  NS    ns1.${{DOMAIN}}.
        ns1     IN  A     ${{IP_ADDR}}
        FZONE

        echo "[5/7] Writing reverse zone..."
        cat > "${{REVERSE_ZONE_FILE}}" <<RZONE
        \$TTL 86400
        @   IN  SOA   ns1.${{DOMAIN}}. admin.${{DOMAIN}}. (
                      ${{SERIAL}} ; Serial
                      3600      ; Refresh
                      900       ; Retry
                      604800    ; Expire
                      86400 )   ; Minimum TTL
        @               IN  NS    ns1.${{DOMAIN}}.
        ${{SERVER_LAST_OCTET}}   IN  PTR   ns1.${{DOMAIN}}.
        RZONE

        echo "[6/7] Validating and starting BIND9..."
        named-checkconf
        named-checkzone "${{DOMAIN}}" "${{ZONE_FILE}}"
        named-checkzone "${{REVERSE_ZONE}}" "${{REVERSE_ZONE_FILE}}"
        systemctl restart bind9
        systemctl enable bind9

        echo "[7/7] Configuring resolver..."
        """)

        if vpn_safe:
            script += textwrap.dedent(f"""\
            # VPN-safe: route .localnet through systemd-resolved
            echo "  Creating resolved drop-in directory..."
            mkdir -p /etc/systemd/resolved.conf.d/
            echo "  Writing localnet.conf..."
            cat > /etc/systemd/resolved.conf.d/localnet.conf <<'RCNF'
[Resolve]
DNS=127.0.0.1
Domains=~{DOMAIN}
RCNF
            echo "  Reloading systemd daemon..."
            systemctl daemon-reload
            echo "  Restarting systemd-resolved..."
            systemctl restart systemd-resolved
            echo "  Flushing DNS caches..."
            resolvectl flush-caches
            # Point resolv.conf to resolved stub (VPN-compatible)
            ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
            echo "  resolv.conf → systemd-resolved stub (127.0.0.53)"
            echo "  VPN DNS injection: ENABLED ✔"
            """)
        else:
            script += textwrap.dedent("""\
            # Direct mode: point resolv.conf straight to BIND9
            echo 'nameserver 127.0.0.1' > /etc/resolv.conf
            echo "  resolv.conf → 127.0.0.1 (BIND9 direct)"
            echo "  Note: VPN DNS injection may not work in this mode."
            """)

        script += 'echo ""\necho "✔  DNS setup complete!"\n'

        if messagebox.askyesno("Confirm Install",
                               f"Install BIND9 DNS server on {ip}?\n"
                               f"VPN-compatible mode: {'ON' if vpn_safe else 'OFF'}"):
            self._run_script(script, success="DNS installed successfully!")

    # ─── DNS Remove ───────────────────────────────────────────────────────────
    def _run_dns_remove(self):
        if not is_root():
            messagebox.showerror("Root required", "Run this app with sudo.")
            return
        if not messagebox.askyesno("Confirm Removal",
                                   "Completely remove BIND9 and all DNS configuration?"):
            return

        script = textwrap.dedent("""\
        #!/bin/bash
        echo "[1/5] Stopping BIND9..."
        systemctl stop bind9 2>/dev/null || true
        systemctl disable bind9 2>/dev/null || true

        echo "[2/5] Purging packages..."
        apt-get purge -y bind9 bind9utils bind9-doc dnsutils 2>/dev/null || true
        apt-get autoremove -y 2>/dev/null || true

        echo "[3/5] Removing config directories..."
        rm -rf /etc/bind /var/cache/bind /var/lib/bind

        echo "[4/5] Removing resolved drop-in..."
        rm -f /etc/systemd/resolved.conf.d/localnet.conf
        systemctl restart systemd-resolved 2>/dev/null || true

        echo "[5/5] Restoring resolv.conf to systemd-resolved stub..."
        ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

        echo ""
        echo "✔  BIND9 removed. Internet DNS restored via systemd-resolved."
        """)
        self._run_script(script, success="DNS removed. Internet access restored.")

    # ─── DNS Records ─────────────────────────────────────────────────────────
    def _apply_dns(self):
        rev = find_reverse_file()
        if not rev:
            self.log("Cannot find reverse zone file.", color=DANGER)
            return False
        script = textwrap.dedent(f"""\
        SERIAL=$(date +%s)
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{ZONE_FILE}"
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{rev}"
        named-checkconf && systemctl reload bind9
        echo "Serial updated: $SERIAL"
        """)
        self._run_script(script, success="DNS reloaded.")
        return True

    def _add_a_record(self):
        if not is_root(): return
        host = self.a_host.get().strip()
        ip   = self.a_ip.get().strip()
        if not host or not ip or host == "nas" or ip == "192.168.1.50":
            messagebox.showwarning("Input needed", "Enter a hostname and IP address.")
            return
        last = ip.split(".")[-1]
        rev  = find_reverse_file()
        if not rev:
            self.log("Reverse zone file not found — is DNS installed?", color=DANGER)
            return
        script = textwrap.dedent(f"""\
        echo '{host}    IN  A   {ip}' >> "{ZONE_FILE}"
        echo '{last}    IN  PTR {host}.{DOMAIN}.' >> "{rev}"
        SERIAL=$(date +%s)
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{ZONE_FILE}"
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{rev}"
        named-checkconf && systemctl reload bind9
        echo "Added: {host} → {ip}"
        """)
        if messagebox.askyesno("Confirm", f"Add A record: {host}.{DOMAIN} → {ip}?"):
            self._run_script(script, success=f"A record added: {host} → {ip}")

    def _add_cname(self):
        if not is_root(): return
        alias  = self.cn_alias.get().strip()
        target = self.cn_target.get().strip()
        if not alias or not target or alias == "movies" or target == "ns1":
            messagebox.showwarning("Input needed", "Enter alias and target.")
            return
        script = textwrap.dedent(f"""\
        echo '{alias}    IN  CNAME {target}.{DOMAIN}.' >> "{ZONE_FILE}"
        SERIAL=$(date +%s)
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{ZONE_FILE}"
        named-checkconf && systemctl reload bind9
        echo "Added CNAME: {alias} → {target}.{DOMAIN}"
        """)
        if messagebox.askyesno("Confirm", f"Add CNAME: {alias}.{DOMAIN} → {target}.{DOMAIN}?"):
            self._run_script(script, success=f"CNAME added: {alias} → {target}")

    def _remove_record(self):
        if not is_root(): return
        host = self.rm_host.get().strip()
        if not host or host == "nas":
            messagebox.showwarning("Input needed", "Enter a hostname.")
            return
        rev = find_reverse_file()
        rev_cmd = f'sed -i "/PTR {host}.{DOMAIN}./d" "{rev}"' if rev else "true"
        script = textwrap.dedent(f"""\
        sed -i "/^{host}/d" "{ZONE_FILE}"
        {rev_cmd}
        SERIAL=$(date +%s)
        sed -i "s/[0-9]{{10}} ; Serial/$SERIAL ; Serial/" "{ZONE_FILE}"
        {"sed -i " + '"s/[0-9]{10} ; Serial/$SERIAL ; Serial/" ' + '"' + rev + '"' if rev else "true"}
        named-checkconf && systemctl reload bind9
        echo "Removed records for: {host}"
        """)
        if messagebox.askyesno("Confirm", f"Remove all records for '{host}' from DNS?"):
            self._run_script(script, success=f"Records for '{host}' removed.")

    def _dns_test(self):
        name = self.test_host.get().strip()
        if not name: return
        ip = get_local_ip()
        self._run_cmd(["dig", f"@{ip}", name, "+short"],
                      success=f"Lookup for {name} complete.")

    # ─── Nginx ────────────────────────────────────────────────────────────────
    def _nginx_install(self):
        if not is_root(): return
        if not messagebox.askyesno("Confirm", "Install Nginx and remove default config?"): return
        script = textwrap.dedent("""\
        apt-get update -qq && apt-get install -y nginx
        rm -f /etc/nginx/sites-enabled/default
        chown -R www-data:www-data /var/www/html
        systemctl restart nginx
        systemctl enable nginx
        echo "✔  Nginx installed."
        """)
        self._run_script(script, success="Nginx installed and running.")

    def _nginx_uninstall(self):
        if not is_root(): return
        if not messagebox.askyesno("Confirm", "Completely remove Nginx and all configs?"): return
        script = textwrap.dedent("""\
        systemctl stop nginx || true
        apt-get purge -y nginx nginx-common nginx-full || true
        apt-get autoremove -y || true
        rm -rf /etc/nginx /var/log/nginx
        echo "✔  Nginx removed."
        """)
        self._run_script(script, success="Nginx removed.")

    def _nginx_add(self):
        if not is_root(): return
        domain = self.ng_domain.get().strip()
        port   = self.ng_port.get().strip()
        if not domain or not port or domain == "movies.localnet" or port == "8096":
            messagebox.showwarning("Input needed", "Enter domain and port.")
            return
        script = textwrap.dedent(f"""\
        cat > /etc/nginx/sites-available/{domain} <<'NGCF'
        server {{
            listen 80;
            server_name {domain};
            location / {{
                proxy_pass http://127.0.0.1:{port};
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }}
        }}
        NGCF
        ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/
        nginx -t && systemctl reload nginx
        echo "✔  {domain} → port {port}"
        """)
        if messagebox.askyesno("Confirm", f"Proxy {domain} → 127.0.0.1:{port}?"):
            self._run_script(script, success=f"Proxy added: {domain} → :{port}")

    def _nginx_remove(self):
        if not is_root(): return
        domain = self.ng_rm.get().strip()
        if not domain or domain == "movies.localnet":
            messagebox.showwarning("Input needed", "Enter a domain to remove.")
            return
        script = textwrap.dedent(f"""\
        rm -f /etc/nginx/sites-enabled/{domain}
        rm -f /etc/nginx/sites-available/{domain}
        systemctl reload nginx
        echo "✔  Removed proxy for {domain}"
        """)
        if messagebox.askyesno("Confirm", f"Remove proxy config for {domain}?"):
            self._run_script(script, success=f"Proxy for {domain} removed.")


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
