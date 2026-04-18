<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LocalNet Manager v4 — Documentation</title>
<style>
  /* ── Reset & Base ─────────────────────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg0:    #080b11;
    --bg1:    #0d1018;
    --bg2:    #121620;
    --bg3:    #181d2a;
    --bg4:    #1e2435;
    --border: #232b3e;
    --bord2:  #2d3850;
    --text:   #c2ceea;
    --dim:    #4e5d7a;
    --dim2:   #374158;
    --blue:   #4a9eff;
    --cyan:   #00d4ff;
    --green:  #00e676;
    --amber:  #ffb300;
    --red:    #ff4d6a;
    --purple: #a78bfa;
    --teal:   #34d399;
    --nav-w:  260px;
    --font:   'Segoe UI', system-ui, -apple-system, sans-serif;
    --mono:   'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  }
  html { scroll-behavior: smooth; }
  body {
    background: var(--bg0);
    color: var(--text);
    font-family: var(--font);
    font-size: 14px;
    line-height: 1.7;
    display: flex;
    min-height: 100vh;
  }

  /* ── Sidebar ──────────────────────────────────────────────────────────── */
  nav {
    width: var(--nav-w);
    min-width: var(--nav-w);
    background: var(--bg1);
    border-right: 1px solid var(--border);
    position: fixed;
    top: 0; left: 0; bottom: 0;
    overflow-y: auto;
    padding: 0 0 32px 0;
    z-index: 100;
  }
  .nav-logo {
    padding: 22px 20px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
  }
  .nav-logo-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--cyan);
    letter-spacing: .3px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .nav-logo-hex { font-size: 20px; }
  .nav-logo-sub {
    font-size: 10px;
    color: var(--dim);
    font-family: var(--mono);
    letter-spacing: 2px;
    margin-top: 4px;
  }
  .nav-section {
    font-size: 9px;
    font-weight: 700;
    color: var(--dim2);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 16px 20px 6px;
  }
  nav a {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 20px;
    color: var(--dim);
    text-decoration: none;
    font-size: 13px;
    transition: color .15s, background .15s;
    border-left: 2px solid transparent;
  }
  nav a:hover { color: var(--text); background: var(--bg2); }
  nav a.active { color: var(--cyan); border-left-color: var(--cyan); background: rgba(0,212,255,.06); }
  .nav-icon { width: 16px; text-align: center; opacity: .7; }

  /* ── Main Content ─────────────────────────────────────────────────────── */
  main {
    margin-left: var(--nav-w);
    flex: 1;
    max-width: 960px;
    padding: 40px 48px 80px;
  }

  /* ── Typography ───────────────────────────────────────────────────────── */
  h1 {
    font-size: 30px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 10px;
    line-height: 1.25;
  }
  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--cyan);
    margin: 48px 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin: 28px 0 10px;
  }
  h4 {
    font-size: 13px;
    font-weight: 600;
    color: var(--dim);
    text-transform: uppercase;
    letter-spacing: .8px;
    margin: 20px 0 8px;
  }
  p { margin-bottom: 12px; color: var(--text); }
  a { color: var(--blue); text-decoration: none; }
  a:hover { text-decoration: underline; }
  ul, ol { margin: 0 0 12px 20px; }
  li { margin-bottom: 5px; }
  strong { color: #fff; font-weight: 600; }

  /* ── Section anchors ──────────────────────────────────────────────────── */
  section { padding-top: 8px; }
  .section-anchor { display: block; height: 0; }

  /* ── Hero ─────────────────────────────────────────────────────────────── */
  .hero {
    background: linear-gradient(135deg, rgba(0,212,255,.08), rgba(74,158,255,.05));
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 32px 36px;
    margin-bottom: 36px;
  }
  .hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
  }
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    font-family: var(--mono);
  }
  .badge-cyan  { background: rgba(0,212,255,.15); color: var(--cyan);   border: 1px solid rgba(0,212,255,.3); }
  .badge-blue  { background: rgba(74,158,255,.15); color: var(--blue);  border: 1px solid rgba(74,158,255,.3); }
  .badge-green { background: rgba(0,230,118,.15);  color: var(--green); border: 1px solid rgba(0,230,118,.3); }
  .badge-amber { background: rgba(255,179,0,.15);  color: var(--amber); border: 1px solid rgba(255,179,0,.3); }
  .badge-purple{ background: rgba(167,139,250,.15);color: var(--purple);border: 1px solid rgba(167,139,250,.3); }

  /* ── Callout boxes ────────────────────────────────────────────────────── */
  .callout {
    border-radius: 6px;
    padding: 14px 18px;
    margin: 16px 0;
    font-size: 13px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }
  .callout-icon { font-size: 16px; margin-top: 1px; flex-shrink: 0; }
  .callout.info    { background: rgba(74,158,255,.1);  border-left: 3px solid var(--blue);   color: #8ab8ff; }
  .callout.warn    { background: rgba(255,179,0,.1);   border-left: 3px solid var(--amber);  color: #ffd066; }
  .callout.danger  { background: rgba(255,77,106,.1);  border-left: 3px solid var(--red);    color: #ff8096; }
  .callout.success { background: rgba(0,230,118,.1);   border-left: 3px solid var(--green);  color: #66ffb2; }
  .callout.tip     { background: rgba(167,139,250,.1); border-left: 3px solid var(--purple); color: #c4b5fd; }

  /* ── Code & pre ───────────────────────────────────────────────────────── */
  code {
    font-family: var(--mono);
    font-size: 12px;
    background: var(--bg3);
    border: 1px solid var(--border);
    padding: 1px 6px;
    border-radius: 3px;
    color: var(--cyan);
  }
  pre {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    overflow-x: auto;
    margin: 12px 0 18px;
    position: relative;
  }
  pre code {
    background: none;
    border: none;
    padding: 0;
    color: var(--text);
    font-size: 12.5px;
    line-height: 1.6;
  }
  .pre-label {
    font-size: 10px;
    color: var(--dim);
    font-family: var(--mono);
    letter-spacing: 1px;
    text-transform: uppercase;
    position: absolute;
    top: 8px; right: 14px;
  }
  .kw  { color: var(--purple); }
  .str { color: var(--green); }
  .cm  { color: var(--dim); font-style: italic; }
  .fn  { color: var(--blue); }
  .nm  { color: var(--amber); }

  /* ── Screenshots ──────────────────────────────────────────────────────── */
  .screenshot-wrap {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin: 18px 0;
    box-shadow: 0 8px 32px rgba(0,0,0,.4);
  }
  .screenshot-wrap img {
    width: 100%;
    display: block;
  }
  .screenshot-caption {
    background: var(--bg2);
    border-top: 1px solid var(--border);
    padding: 8px 14px;
    font-size: 11px;
    color: var(--dim);
    font-family: var(--mono);
  }

  /* ── Tables ───────────────────────────────────────────────────────────── */
  .table-wrap { overflow-x: auto; margin: 14px 0 20px; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  thead tr { background: var(--bg3); }
  th {
    text-align: left;
    padding: 10px 14px;
    color: var(--dim);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .8px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,.02); }

  /* ── Method badges ────────────────────────────────────────────────────── */
  .method {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 700;
    font-family: var(--mono);
    vertical-align: middle;
  }
  .get    { background: rgba(0,230,118,.15); color: var(--green); }
  .post   { background: rgba(74,158,255,.15); color: var(--blue); }
  .delete { background: rgba(255,77,106,.15); color: var(--red); }

  /* ── Endpoint blocks ──────────────────────────────────────────────────── */
  .endpoint {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    margin-bottom: 10px;
    overflow: hidden;
  }
  .endpoint-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    cursor: pointer;
    user-select: none;
    transition: background .15s;
  }
  .endpoint-header:hover { background: var(--bg3); }
  .endpoint-path {
    font-family: var(--mono);
    font-size: 12.5px;
    color: var(--text);
    flex: 1;
  }
  .endpoint-desc { font-size: 12px; color: var(--dim); }
  .endpoint-body {
    border-top: 1px solid var(--border);
    padding: 14px 16px;
    background: var(--bg1);
    display: none;
  }
  .endpoint.open .endpoint-body { display: block; }
  .endpoint-toggle { color: var(--dim); font-size: 11px; transition: transform .15s; }
  .endpoint.open .endpoint-toggle { transform: rotate(180deg); }

  /* ── Feature grid ─────────────────────────────────────────────────────── */
  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin: 16px 0;
  }
  .feature-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    transition: border-color .2s;
  }
  .feature-card:hover { border-color: var(--bord2); }
  .feature-icon { font-size: 22px; margin-bottom: 8px; }
  .feature-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
  .feature-desc { font-size: 12px; color: var(--dim); line-height: 1.5; }

  /* ── Steps ────────────────────────────────────────────────────────────── */
  .steps { margin: 14px 0; }
  .step {
    display: flex;
    gap: 14px;
    margin-bottom: 14px;
    align-items: flex-start;
  }
  .step-num {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(0,212,255,.15);
    border: 1px solid rgba(0,212,255,.3);
    color: var(--cyan);
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .step-content { flex: 1; }
  .step-title { font-weight: 600; color: var(--text); margin-bottom: 3px; }
  .step-desc { font-size: 13px; color: var(--dim); }

  /* ── TOC ──────────────────────────────────────────────────────────────── */
  .toc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 14px 0;
  }
  .toc-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 5px;
    color: var(--dim);
    font-size: 13px;
    text-decoration: none;
    transition: color .15s, border-color .15s;
  }
  .toc-item:hover { color: var(--cyan); border-color: var(--bord2); }
  .toc-num { font-family: var(--mono); font-size: 11px; color: var(--dim2); }

  /* ── Responsive ───────────────────────────────────────────────────────── */
  @media (max-width: 900px) {
    nav { display: none; }
    main { margin-left: 0; padding: 24px 20px 60px; }
    .toc-grid { grid-template-columns: 1fr; }
    .feature-grid { grid-template-columns: 1fr 1fr; }
  }

  /* ── Scrollbar ────────────────────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg0); }
  ::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--bord2); }

  /* ── Print ────────────────────────────────────────────────────────────── */
  @media print {
    nav { display: none; }
    main { margin-left: 0; }
    .endpoint-body { display: block !important; }
  }
</style>
</head>
<body>

<!-- ═══════════════ SIDEBAR ═══════════════ -->
<nav id="nav">
  <div class="nav-logo">
    <div class="nav-logo-title"><span class="nav-logo-hex">⬡</span> LocalNet Manager</div>
    <div class="nav-logo-sub">v4 · DOCUMENTATION</div>
  </div>

  <div class="nav-section">Overview</div>
  <a href="#intro"        class="nav-link"><span class="nav-icon">📖</span> Introduction</a>
  <a href="#features"     class="nav-link"><span class="nav-icon">✨</span> Features</a>
  <a href="#architecture" class="nav-link"><span class="nav-icon">🏗</span> Architecture</a>

  <div class="nav-section">Getting Started</div>
  <a href="#requirements" class="nav-link"><span class="nav-icon">📋</span> Requirements</a>
  <a href="#install"      class="nav-link"><span class="nav-icon">⚡</span> Installation</a>
  <a href="#first-login"  class="nav-link"><span class="nav-icon">🔑</span> First Login</a>

  <div class="nav-section">UI Reference</div>
  <a href="#ui-dashboard" class="nav-link"><span class="nav-icon">🖥</span> Dashboard</a>
  <a href="#ui-dns"       class="nav-link"><span class="nav-icon">🌐</span> DNS Server</a>
  <a href="#ui-nginx"     class="nav-link"><span class="nav-icon">↔</span> Nginx Proxy</a>
  <a href="#ui-dhcp"      class="nav-link"><span class="nav-icon">📡</span> DHCP Server</a>
  <a href="#ui-ssl"       class="nav-link"><span class="nav-icon">🔒</span> SSL / TLS</a>
  <a href="#ui-adblock"   class="nav-link"><span class="nav-icon">🚫</span> Ad Blocking</a>
  <a href="#ui-backups"   class="nav-link"><span class="nav-icon">💾</span> Backups</a>
  <a href="#ui-logs"      class="nav-link"><span class="nav-icon">📜</span> System Logs</a>
  <a href="#ui-network"   class="nav-link"><span class="nav-icon">🔌</span> Network</a>
  <a href="#ui-settings"  class="nav-link"><span class="nav-icon">⚙</span> Settings</a>

  <div class="nav-section">API Reference</div>
  <a href="#api-auth"     class="nav-link"><span class="nav-icon">🔐</span> Auth</a>
  <a href="#api-status"   class="nav-link"><span class="nav-icon">📊</span> Status & Config</a>
  <a href="#api-dns"      class="nav-link"><span class="nav-icon">🌐</span> DNS</a>
  <a href="#api-nginx"    class="nav-link"><span class="nav-icon">↔</span> Nginx</a>
  <a href="#api-dhcp"     class="nav-link"><span class="nav-icon">📡</span> DHCP</a>
  <a href="#api-ssl"      class="nav-link"><span class="nav-icon">🔒</span> SSL / TLS</a>
  <a href="#api-adblock"  class="nav-link"><span class="nav-icon">🚫</span> Ad Blocking</a>
  <a href="#api-backups"  class="nav-link"><span class="nav-icon">💾</span> Backups</a>
  <a href="#api-logs"     class="nav-link"><span class="nav-icon">📜</span> Logs</a>

  <div class="nav-section">Internals</div>
  <a href="#config-file"  class="nav-link"><span class="nav-icon">📄</span> Config File</a>
  <a href="#nginx-tmpls"  class="nav-link"><span class="nav-icon">📐</span> Nginx Templates</a>
  <a href="#security"     class="nav-link"><span class="nav-icon">🛡</span> Security</a>
  <a href="#troubleshoot" class="nav-link"><span class="nav-icon">🔧</span> Troubleshooting</a>
</nav>

<!-- ═══════════════ MAIN ═══════════════ -->
<main>

<!-- ─── HERO ─── -->
<div class="hero">
  <h1>⬡ LocalNet Manager v4</h1>
  <p style="color:var(--dim); font-size:15px; margin-bottom:14px;">
    A self-hosted, browser-based control panel for managing a private LAN — DNS, reverse proxy, DHCP, SSL certificates, ad blocking, backups, and live logs — all from a single Python script.
  </p>
  <div class="hero-badges">
    <span class="badge badge-cyan">v4 Alpha</span>
    <span class="badge badge-blue">Python 3 · Flask</span>
    <span class="badge badge-green">BIND9 · Nginx · ISC-DHCP</span>
    <span class="badge badge-amber">Port 8091</span>
    <span class="badge badge-purple">Requires root</span>
  </div>
</div>

<!-- ─── TABLE OF CONTENTS ─── -->
<h2 id="toc">📑 Table of Contents</h2>
<div class="toc-grid">
  <a class="toc-item" href="#intro"><span class="toc-num">01</span> Introduction</a>
  <a class="toc-item" href="#features"><span class="toc-num">02</span> Features</a>
  <a class="toc-item" href="#architecture"><span class="toc-num">03</span> Architecture</a>
  <a class="toc-item" href="#requirements"><span class="toc-num">04</span> Requirements</a>
  <a class="toc-item" href="#install"><span class="toc-num">05</span> Installation</a>
  <a class="toc-item" href="#first-login"><span class="toc-num">06</span> First Login</a>
  <a class="toc-item" href="#ui-dashboard"><span class="toc-num">07</span> UI — Dashboard</a>
  <a class="toc-item" href="#ui-dns"><span class="toc-num">08</span> UI — DNS Server</a>
  <a class="toc-item" href="#ui-nginx"><span class="toc-num">09</span> UI — Nginx Proxy</a>
  <a class="toc-item" href="#ui-dhcp"><span class="toc-num">10</span> UI — DHCP Server</a>
  <a class="toc-item" href="#ui-ssl"><span class="toc-num">11</span> UI — SSL / TLS</a>
  <a class="toc-item" href="#ui-adblock"><span class="toc-num">12</span> UI — Ad Blocking</a>
  <a class="toc-item" href="#ui-backups"><span class="toc-num">13</span> UI — Backups</a>
  <a class="toc-item" href="#api-auth"><span class="toc-num">14</span> API — Auth</a>
  <a class="toc-item" href="#api-dns"><span class="toc-num">15</span> API — DNS</a>
  <a class="toc-item" href="#nginx-tmpls"><span class="toc-num">16</span> Nginx Templates</a>
  <a class="toc-item" href="#security"><span class="toc-num">17</span> Security</a>
  <a class="toc-item" href="#troubleshoot"><span class="toc-num">18</span> Troubleshooting</a>
</div>

<!-- ═══════════════ INTRODUCTION ═══════════════ -->
<section>
<a class="section-anchor" id="intro"></a>
<h2>📖 Introduction</h2>

<p>
  <strong>LocalNet Manager</strong> is a single-file Python web application that turns any Linux machine into a fully managed home or office network infrastructure server. Instead of manually editing <code>/etc/bind/</code> zone files, writing Nginx reverse-proxy configs, or remembering <code>certbot</code> flags, every operation is exposed through a clean browser UI running on port <strong>8091</strong>.
</p>
<p>
  The application is intentionally <strong>dependency-light</strong>: it ships as one <code>.py</code> file, relies only on <strong>Flask</strong> (a Python micro-framework), and drives all real work through shell scripts executed as root via <code>subprocess</code>. Every destructive operation is preceded by an automatic ZIP backup of <code>/etc/bind</code> and <code>/etc/nginx</code> so recovery is always one click away.
</p>

<div class="callout warn">
  <span class="callout-icon">⚠️</span>
  <div><strong>Root required.</strong> Most operations (DNS install, proxy management, DHCP, SSL) require the application to run as <code>root</code>. Launch with <code>sudo python3 localnet_v4_alpha_b.py</code>. The UI will show a warning and disable write operations if run as a non-root user.</div>
</div>

<h3>What problem does it solve?</h3>
<p>
  Self-hosters running services like Home Assistant, Nextcloud, Jellyfin, or Gitea on a local server typically need:
</p>
<ul>
  <li>Custom DNS names like <code>nas.localnet</code> or <code>dash.localnet</code> instead of bare IP addresses</li>
  <li>Nginx reverse proxy so multiple services share port 80/443</li>
  <li>Local HTTPS without browser warnings — via <code>mkcert</code> or Let's Encrypt</li>
  <li>Network-wide ad blocking without a separate Pi-hole</li>
  <li>DHCP so devices get addresses automatically and the DNS server is injected</li>
</ul>
<p>LocalNet Manager automates all of this from a single web interface.</p>
</section>

<!-- ═══════════════ FEATURES ═══════════════ -->
<section>
<a class="section-anchor" id="features"></a>
<h2>✨ Features</h2>

<div class="feature-grid">
  <div class="feature-card">
    <div class="feature-icon">🌐</div>
    <div class="feature-title">BIND9 DNS Server</div>
    <div class="feature-desc">Install, configure, and manage an authoritative private TLD. A/CNAME/TXT/SRV/wildcard records with one-click add/delete.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">↔️</div>
    <div class="feature-title">Nginx Reverse Proxy</div>
    <div class="feature-desc">Five built-in templates: Basic, WebSocket, Home Assistant, Nextcloud, and Load Balancer. Full upstream IP + port control.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">📡</div>
    <div class="feature-title">DHCP Server</div>
    <div class="feature-desc">ISC-DHCP-Server install and configure with range, gateway, lease time, and DNS injection. Live lease viewer.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🔒</div>
    <div class="feature-title">SSL / TLS</div>
    <div class="feature-desc">Local CA via mkcert for *.localnet certs, plus Certbot DNS-01 for globally trusted Let's Encrypt certs — no port 80 required.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🚫</div>
    <div class="feature-title">Ad Blocking</div>
    <div class="feature-desc">DNS-layer ad blocking via BIND9 RPZ using the StevenBlack unified hosts list. Blocks 100k–200k ad/tracker domains network-wide.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">💾</div>
    <div class="feature-title">Automatic Backups</div>
    <div class="feature-desc">ZIP snapshots of /etc/bind and /etc/nginx before every install, remove, or modify operation. One-click restore.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">📜</div>
    <div class="feature-title">Live System Logs</div>
    <div class="feature-desc">Server-Sent Events (SSE) stream of journalctl output for BIND9, Nginx, DHCP, and systemd-resolved in real time.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🛡️</div>
    <div class="feature-title">Authentication</div>
    <div class="feature-desc">Session-based login with SHA-256 hashed passwords stored in JSON config. Default password is <code>localnet</code>.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🔌</div>
    <div class="feature-title">VPN Compatible</div>
    <div class="feature-desc">Routes through systemd-resolved stub so VPN clients can still inject their own DNS while local names continue to resolve.</div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🗄️</div>
    <div class="feature-title">SQLite Metadata</div>
    <div class="feature-desc">Optional notes on DNS records and proxies, plus a backup history log, all stored in a local SQLite database.</div>
  </div>
</div>
</section>

<!-- ═══════════════ ARCHITECTURE ═══════════════ -->
<section>
<a class="section-anchor" id="architecture"></a>
<h2>🏗 Architecture</h2>

<p>LocalNet Manager is deliberately <strong>stateless at the application layer</strong>. All real configuration lives in system files (<code>/etc/bind/</code>, <code>/etc/nginx/</code>, etc.). The app reads those files on every request and writes them via Bash scripts executed by <code>subprocess</code> as root.</p>

<pre><code><span class="cm">┌──────────────────── Browser ────────────────────────┐</span>
<span class="cm">│                 http://&lt;server&gt;:8091                │</span>
<span class="cm">│   Vanilla JS SPA  ←──SSE log stream──→  Flask App   │</span>
<span class="cm">└────────────────────────┬────────────────────────────┘</span>
                         │ REST API (JSON)
                         ▼
<span class="cm">┌───────────────── Flask (Python 3) ──────────────────┐</span>
<span class="cm">│  Auth  │  Config  │  Script Runner  │  SSE Queue    │</span>
<span class="cm">│  ├─ session-based  login            │               │</span>
<span class="cm">│  ├─ /etc/localnet/config.json       │               │</span>
<span class="cm">│  ├─ /etc/localnet/localnet.db       │               │</span>
<span class="cm">│  └─ threading.Thread (bash scripts) │               │</span>
<span class="cm">└──────────┬──────────────────────────┘               </span>
           │ subprocess.Popen
           ▼
<span class="cm">┌──────────────── System Services ────────────────────┐</span>
<span class="cm">│  BIND9 (named)     /etc/bind/                       │</span>
<span class="cm">│  Nginx             /etc/nginx/sites-{available,enabled}</span>
<span class="cm">│  ISC-DHCP-Server   /etc/dhcp/dhcpd.conf             │</span>
<span class="cm">│  mkcert / certbot  /etc/localnet/certs/             │</span>
<span class="cm">│  systemd-resolved  /etc/systemd/resolved.conf.d/    │</span>
<span class="cm">└─────────────────────────────────────────────────────┘</span></code></pre>

<h3>Key source modules (within single file)</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Section</th><th>Lines</th><th>Responsibility</th></tr></thead>
  <tbody>
    <tr><td><code>Config</code></td><td>52–69</td><td>Load/save <code>/etc/localnet/config.json</code> with fallback to <code>/tmp</code></td></tr>
    <tr><td><code>Auth Helpers</code></td><td>79–106</td><td>SHA-256 password hashing, HMAC compare, Flask session guard decorator</td></tr>
    <tr><td><code>SQLite DB</code></td><td>108–182</td><td>Record notes, proxy notes, backup history (3 tables)</td></tr>
    <tr><td><code>Logging</code></td><td>184–194</td><td>In-memory ring buffer (1000 entries) + fan-out to SSE subscriber queues</td></tr>
    <tr><td><code>Helpers</code></td><td>196–296</td><td>IP detection, interface enumeration, zone file parser, proxy lister</td></tr>
    <tr><td><code>Backup System</code></td><td>298–336</td><td>ZIP /etc/bind + /etc/nginx; restore by extracting to <code>/</code></td></tr>
    <tr><td><code>Script Runner</code></td><td>338–369</td><td>Writes Bash to <code>/tmp/_localnet_v4.sh</code>, runs in daemon thread, pipes output to log</td></tr>
    <tr><td><code>Nginx Templates</code></td><td>371–506</td><td>5 config templates rendered with plain <code>.replace()</code></td></tr>
    <tr><td><code>API Routes</code></td><td>508–1522</td><td>All REST endpoints (see API Reference)</td></tr>
    <tr><td><code>HTML_PAGE</code></td><td>1524–3197</td><td>Entire frontend as an embedded Python string (SPA)</td></tr>
    <tr><td><code>LOGIN_PAGE</code></td><td>3199–3245</td><td>Standalone login HTML</td></tr>
  </tbody>
</table>
</div>

<h3>Concurrency model</h3>
<p>
  Flask runs with <code>threaded=True</code>. Every shell script runs in a <strong>daemon thread</strong> so HTTP requests return immediately with <code>{"ok": true}</code> while the script executes in the background. Progress is streamed back to the browser via the <strong>SSE log endpoint</strong> (<code>/api/logs/stream</code>) using a per-client <code>queue.Queue</code>.
</p>

<h3>DNS resolution chain (VPN-compatible mode)</h3>
<pre><code>resolv.conf → 127.0.0.53 (systemd-resolved stub)
   ├── *.localnet  → 127.0.0.1 (BIND9)  ✔ local names
   └── everything else → upstream / VPN DNS  ✔ VPN works</code></pre>

<p>In non-VPN mode, <code>resolv.conf</code> points directly to BIND9 at the server LAN IP with <code>forward only</code>, which is simpler but breaks VPN DNS injection.</p>
</section>

<!-- ═══════════════ REQUIREMENTS ═══════════════ -->
<section>
<a class="section-anchor" id="requirements"></a>
<h2>📋 Requirements</h2>

<h3>Host system</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Requirement</th><th>Details</th></tr></thead>
  <tbody>
    <tr><td><strong>OS</strong></td><td>Ubuntu 22.04+ or Debian 12+ (uses <code>apt-get</code>, <code>systemctl</code>, <code>journalctl</code>)</td></tr>
    <tr><td><strong>Python</strong></td><td>3.10+ (uses <code>str | None</code> union type hints in internal helpers)</td></tr>
    <tr><td><strong>Privilege</strong></td><td>Must run as <code>root</code> (<code>sudo</code>) for all write operations</td></tr>
    <tr><td><strong>Network</strong></td><td>Static LAN IP strongly recommended; the detected IP is baked into BIND9 config</td></tr>
    <tr><td><strong>Internet</strong></td><td>Required during service installation (apt-get, mkcert download, StevenBlack list)</td></tr>
  </tbody>
</table>
</div>

<h3>Python dependencies</h3>
<pre><code><span class="cm"># Runtime (auto-installed by pip)</span>
flask          <span class="cm"># Web framework — only external dependency</span>

<span class="cm"># Standard library (no install needed)</span>
os, sys, json, glob, socket, subprocess, threading, re, time, base64
hashlib, secrets, sqlite3, zipfile, functools, hmac
queue.Queue, pathlib.Path, datetime</code></pre>

<h3>System packages installed on demand</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Package</th><th>Installed when</th></tr></thead>
  <tbody>
    <tr><td><code>bind9 bind9utils dnsutils</code></td><td>DNS → Install DNS Server</td></tr>
    <tr><td><code>nginx</code></td><td>Nginx Proxy → Install / Remove → Install Nginx</td></tr>
    <tr><td><code>isc-dhcp-server</code></td><td>DHCP → Install &amp; Configure DHCP</td></tr>
    <tr><td><code>libnss3-tools wget</code> + mkcert binary</td><td>SSL / TLS → Install mkcert</td></tr>
    <tr><td><code>certbot python3-certbot-dns-rfc2136</code></td><td>SSL / TLS → Let's Encrypt → Install Certbot</td></tr>
  </tbody>
</table>
</div>
</section>

<!-- ═══════════════ INSTALLATION ═══════════════ -->
<section>
<a class="section-anchor" id="install"></a>
<h2>⚡ Installation</h2>

<div class="steps">
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-content">
      <div class="step-title">Install Python &amp; Flask</div>
      <pre><code>sudo apt-get update
sudo apt-get install -y python3 python3-pip
pip3 install flask</code></pre>
    </div>
  </div>
  <div class="step">
    <div class="step-num">2</div>
    <div class="step-content">
      <div class="step-title">Copy the script to your server</div>
      <pre><code>sudo cp localnet_v4_alpha_b.py /usr/local/bin/localnet
sudo chmod +x /usr/local/bin/localnet</code></pre>
    </div>
  </div>
  <div class="step">
    <div class="step-num">3</div>
    <div class="step-content">
      <div class="step-title">Run as root</div>
      <pre><code>sudo python3 /usr/local/bin/localnet</code></pre>
      <p style="font-size:13px; color:var(--dim); margin-top:6px;">You will see startup output including the web UI URL and detected server IP.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num">4</div>
    <div class="step-content">
      <div class="step-title">Open the web UI</div>
      <pre><code>http://&lt;your-server-ip&gt;:8091</code></pre>
      <p style="font-size:13px; color:var(--dim); margin-top:6px;">Or <code>http://localhost:8091</code> if on the same machine.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num">5</div>
    <div class="step-content">
      <div class="step-title">(Optional) Run as a systemd service</div>
      <pre><code><span class="cm"># /etc/systemd/system/localnet.service</span>
[Unit]
Description=LocalNet Manager v4
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/localnet
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target</code></pre>
      <pre><code>sudo systemctl daemon-reload
sudo systemctl enable --now localnet</code></pre>
    </div>
  </div>
</div>

<div class="callout info">
  <span class="callout-icon">ℹ️</span>
  <div>When run as a non-root user, the application falls back to storing config in <code>/tmp/localnet_v4/</code> and the SQLite database in the same location. All write operations that require root will return HTTP 403.</div>
</div>
</section>

<!-- ═══════════════ FIRST LOGIN ═══════════════ -->
<section>
<a class="section-anchor" id="first-login"></a>
<h2>🔑 First Login</h2>

<p>On first run, navigate to <code>http://&lt;server&gt;:8091</code>. You will be redirected to the login page.</p>

<div class="callout warn">
  <span class="callout-icon">⚠️</span>
  <div><strong>Default password is <code>localnet</code>.</strong> Change it immediately via Settings → Change Password. The password is stored as a SHA-256 hash in <code>/etc/localnet/config.json</code>.</div>
</div>

<p>After logging in:</p>
<ol>
  <li>Navigate to <strong>Settings</strong> and change the password.</li>
  <li>Verify your server IP is detected correctly in the <strong>Network</strong> page.</li>
  <li>Go to <strong>DNS → Setup</strong> and install BIND9 with your chosen TLD (default: <code>localnet</code>).</li>
  <li>Add an A record for your server in <strong>DNS → Records</strong>.</li>
  <li>Install Nginx via <strong>Nginx Proxy → Install / Remove</strong>, then add your first proxy.</li>
</ol>
</section>

<!-- ═══════════════ UI: DASHBOARD ═══════════════ -->
<section>
<a class="section-anchor" id="ui-dashboard"></a>
<h2>🖥 Dashboard</h2>

<div class="screenshot-wrap">
  <img src="./images/1.png" alt="LocalNet Manager Dashboard">
  <div class="screenshot-caption">fig 1 — Dashboard showing service status, record counts, active domain, and /etc/resolv.conf</div>
</div>

<p>The dashboard provides a live overview of the entire stack. It polls <code>GET /api/status</code> every 8 seconds and the service status indicators in the top-right corner (<strong>BIND9</strong> / <strong>NGINX</strong>) update in real time.</p>

<h3>Dashboard widgets</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Widget</th><th>Data source</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><strong>BIND9 DNS</strong></td><td><code>systemctl is-active bind9</code></td><td>Green dot = active. "reload" button calls <code>POST /api/service/reload</code></td></tr>
    <tr><td><strong>Nginx</strong></td><td><code>systemctl is-active nginx</code></td><td>Same as above for Nginx</td></tr>
    <tr><td><strong>systemd-resolved</strong></td><td><code>systemctl is-active systemd-resolved</code></td><td>Status + reload button</td></tr>
    <tr><td><strong>DNS Records</strong></td><td>Count of <code>A/CNAME/TXT</code> entries in zone file</td><td>Links to DNS → Records</td></tr>
    <tr><td><strong>Nginx Proxies</strong></td><td>Count of sites in <code>/etc/nginx/sites-enabled/</code></td><td>Links to Nginx Proxy</td></tr>
    <tr><td><strong>SSL Certs</strong></td><td>Count of <code>*.pem</code> files in <code>/etc/localnet/certs/</code></td><td>Links to SSL / TLS</td></tr>
    <tr><td><strong>Active Domain</strong></td><td><code>cfg.domain</code> from config.json</td><td>Shows TLD + server IP</td></tr>
    <tr><td><strong>/etc/resolv.conf</strong></td><td>First 300 chars of the file</td><td>Read-only preview</td></tr>
  </tbody>
</table>
</div>

<h3>Output log panel</h3>
<p>The collapsible log panel at the bottom of every page shows real-time output from the SSE stream (<code>GET /api/logs/stream</code>). It displays the last 80 historical entries on connect, then streams new entries as scripts execute. Log entries are color-coded: <span style="color:var(--green)">success</span>, <span style="color:var(--red)">error</span>, and plain info.</p>
</section>

<!-- ═══════════════ UI: DNS ═══════════════ -->
<section>
<a class="section-anchor" id="ui-dns"></a>
<h2>🌐 DNS Server</h2>

<p>The DNS section has three tabs: <strong>Setup</strong>, <strong>Records</strong>, and <strong>Test</strong>.</p>

<h3>Setup tab</h3>
<div class="screenshot-wrap">
  <img src="./images/2.png" alt="DNS Server Setup tab">
  <div class="screenshot-caption">fig 2 — DNS Setup: domain TLD, server IP, forwarders, VPN-compatible mode toggle</div>
</div>

<p>Configures and installs BIND9. The install script performs <strong>8 steps</strong>:</p>
<ol>
  <li>Installs <code>bind9 bind9utils dnsutils</code> via apt-get</li>
  <li>Writes <code>/etc/bind/named.conf.options</code> (ACL, recursion, forwarders, DNSSEC)</li>
  <li>Writes <code>/etc/bind/named.conf.local</code> (forward and reverse zone declarations)</li>
  <li>Writes the forward zone file (<code>/etc/bind/db.{domain}</code>) with SOA, NS, and ns1 A record</li>
  <li>Writes the reverse zone file (<code>/etc/bind/db.{octet1}.{octet2}.{octet3}</code>)</li>
  <li>Validates with <code>named-checkconf</code> + <code>named-checkzone</code> and starts/enables <code>named</code></li>
  <li>Writes <code>/etc/systemd/resolved.conf.d/localnet.conf</code> to route <code>~domain</code> through BIND9</li>
  <li>Symlinks <code>/etc/resolv.conf</code> → systemd-resolved stub and flushes caches</li>
</ol>

<div class="table-wrap">
<table>
  <thead><tr><th>Field</th><th>Default</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td>Domain (TLD)</td><td><code>localnet</code></td><td>Your private top-level domain. All records live under <code>.localnet</code></td></tr>
    <tr><td>Server IP</td><td>Auto-detected</td><td>Dropdown of non-loopback IPv4 interfaces. Used as BIND9's listen-on address</td></tr>
    <tr><td>Forwarders</td><td><code>1.1.1.2, 1.0.0.2</code></td><td>Comma-separated upstream resolvers for non-local queries</td></tr>
    <tr><td>VPN-compatible mode</td><td>ON</td><td>Routes through systemd-resolved stub; allows VPN to inject its own DNS</td></tr>
  </tbody>
</table>
</div>

<h3>Records tab</h3>
<div class="screenshot-wrap">
  <img src="./images/3.png" alt="DNS Records tab">
  <div class="screenshot-caption">fig 3 — DNS Records: A/CNAME sub-tabs, zone record table with delete buttons</div>
</div>

<p>Four record sub-tabs are available:</p>

<div class="table-wrap">
<table>
  <thead><tr><th>Sub-tab</th><th>Record type</th><th>Fields</th></tr></thead>
  <tbody>
    <tr><td><strong>A / CNAME</strong></td><td><code>A</code> and <code>CNAME</code></td><td>Hostname + IP (A) or Alias + Target (CNAME)</td></tr>
    <tr><td><strong>TXT</strong></td><td><code>TXT</code></td><td>Hostname + value (auto-quoted). Used for SPF, DKIM, verification strings</td></tr>
    <tr><td><strong>SRV</strong></td><td><code>SRV</code></td><td>Service, Proto, Priority, Weight, Port, Target — e.g. <code>_http._tcp</code></td></tr>
    <tr><td><strong>Wildcard</strong></td><td><code>A</code> with <code>*</code> host</td><td>IP only. Routes all unmatched subdomains to the given IP</td></tr>
  </tbody>
</table>
</div>

<p>Every add/delete operation appends or removes lines from the zone file, bumps the serial to <code>$(date +%s)</code>, runs <code>named-checkconf</code>, and calls <code>systemctl reload named</code>. Reverse-zone PTR records are also updated automatically when adding/removing A records.</p>

<h3>Test tab</h3>
<div class="screenshot-wrap">
  <img src="./images/4.png" alt="DNS Test tab">
  <div class="screenshot-caption">fig 4 — DNS Lookup Test: runs a dig query against the BIND9 server</div>
</div>

<p>Runs <code>dig @{server} {name} +short +time=2</code> and returns the result. Enter a hostname like <code>nas.localnet</code> to verify it resolves correctly. The DNS server IP field defaults to the detected server IP.</p>
</section>

<!-- ═══════════════ UI: NGINX ═══════════════ -->
<section>
<a class="section-anchor" id="ui-nginx"></a>
<h2>↔ Nginx Reverse Proxy</h2>

<h3>Proxies tab</h3>
<div class="screenshot-wrap">
  <img src="./images/5.png" alt="Nginx Proxies tab">
  <div class="screenshot-caption">fig 5 — Nginx Proxies: active proxy list with domain, port, template, and delete button</div>
</div>

<p>Lists all active proxies by reading symlinks in <code>/etc/nginx/sites-enabled/</code> (excluding <code>default</code>) and parsing the config for <code>proxy_pass</code> port and the <code># template:</code> comment. Each proxy row shows domain, upstream port, and template badge, with a delete button that removes both the <code>sites-available</code> file and its symlink.</p>

<h3>Add Proxy tab</h3>
<div class="screenshot-wrap">
  <img src="./images/6.png" alt="Nginx Add Proxy tab">
  <div class="screenshot-caption">fig 6 — Add Proxy: template selection cards and configure form</div>
</div>

<p>Select a template card, then fill in <strong>Domain Name</strong> (e.g. <code>movies.localnet</code>), <strong>Upstream IP</strong> (usually <code>127.0.0.1</code>), and <strong>Port</strong>. The generated config is written to <code>/etc/nginx/sites-available/{domain}</code>, symlinked to <code>sites-enabled/</code>, validated with <code>nginx -t</code>, and reloaded.</p>

<div class="callout tip">
  <span class="callout-icon">💡</span>
  <div>Create the DNS record (<strong>CNAME</strong> or <strong>A</strong>) for the domain in the DNS section <em>before</em> or <em>after</em> adding the proxy — both work. The proxy only needs DNS to be resolvable from client devices.</div>
</div>
</section>

<!-- ═══════════════ UI: DHCP ═══════════════ -->
<section>
<a class="section-anchor" id="ui-dhcp"></a>
<h2>📡 DHCP Server</h2>

<div class="screenshot-wrap">
  <img src="./images/7.png" alt="DHCP Server page">
  <div class="screenshot-caption">fig 7 — DHCP Server: configure range, gateway, lease time, and DNS server IP</div>
</div>

<p>Installs and configures <strong>ISC-DHCP-Server</strong> (<code>isc-dhcp-server</code>). When enabled, network devices will receive their IP address from this server along with the LocalNet DNS server IP, making all <code>.localnet</code> hostnames resolve automatically on every device without manual configuration.</p>

<div class="table-wrap">
<table>
  <thead><tr><th>Field</th><th>Default</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td>Range Start</td><td><code>192.168.1.100</code></td><td>First IP in the DHCP pool. Derived from server IP subnet</td></tr>
    <tr><td>Range End</td><td><code>192.168.1.200</code></td><td>Last IP in the DHCP pool</td></tr>
    <tr><td>Router / Gateway</td><td><code>192.168.1.1</code></td><td>Injected as <code>option routers</code>. Should be your router's IP</td></tr>
    <tr><td>Lease Time (seconds)</td><td><code>3600</code></td><td>Default lease; max lease is automatically set to <code>2×</code> this value</td></tr>
    <tr><td>Server IP (DNS)</td><td>Auto-detected</td><td>The LocalNet server's IP — pushed to all DHCP clients as their DNS resolver</td></tr>
  </tbody>
</table>
</div>

<div class="callout warn">
  <span class="callout-icon">⚠️</span>
  <div>Only <strong>one DHCP server</strong> should run on a subnet. Disable DHCP on your router before enabling it here, or use non-overlapping ranges. Running two DHCP servers causes address conflicts.</div>
</div>

<p>The <strong>Active Leases</strong> tab reads <code>/var/lib/dhcp/dhcpd.leases</code>, parses all blocks with <code>binding state active</code>, and displays IP address, MAC, hostname, and expiry time for each current lease.</p>
</section>

<!-- ═══════════════ UI: SSL ═══════════════ -->
<section>
<a class="section-anchor" id="ui-ssl"></a>
<h2>🔒 SSL / TLS</h2>

<p>Two approaches to HTTPS certificates are provided, each on its own sub-tab.</p>

<h3>mkcert (Local CA) tab</h3>
<div class="screenshot-wrap">
  <img src="./images/8.png" alt="SSL TLS mkcert tab">
  <div class="screenshot-caption">fig 8 — mkcert: local CA install, certificate generation, issued certs panel, browser trust guide</div>
</div>

<p><strong>mkcert</strong> creates a local Certificate Authority that is trusted by the machine that installs it. Any cert it signs is trusted automatically — <strong>no port 80 needed, works entirely offline</strong>.</p>

<div class="steps">
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-content">
      <div class="step-title">Install mkcert</div>
      <div class="step-desc">Downloads the latest mkcert binary for your architecture (amd64/arm64/armhf), installs the local CA into OS and browser trust stores via <code>mkcert -install</code>. CA files are stored in <code>/etc/localnet/ca/</code>.</div>
    </div>
  </div>
  <div class="step">
    <div class="step-num">2</div>
    <div class="step-content">
      <div class="step-title">Generate a certificate</div>
      <div class="step-desc">Enter a domain (e.g. <code>mypc.localnet</code>) or leave blank for a wildcard (<code>*.localnet</code>). The cert is generated with three SANs: the entered domain, <code>*.{tld}</code>, and <code>{tld}</code> — stored in <code>/etc/localnet/certs/</code>.</div>
    </div>
  </div>
  <div class="step">
    <div class="step-num">3</div>
    <div class="step-content">
      <div class="step-title">Auto-configure Nginx</div>
      <div class="step-desc">After cert generation, the script checks if a matching Nginx site config exists. If found and not already SSL-enabled, it injects <code>listen 443 ssl;</code> and the cert/key paths, then reloads Nginx.</div>
    </div>
  </div>
  <div class="step">
    <div class="step-num">4</div>
    <div class="step-content">
      <div class="step-title">Trust on other devices</div>
      <div class="step-desc">Download the Root CA from the "Click here to download 'Root CA'" link and import <code>/etc/localnet/ca/rootCA.pem</code> into each device's browser/OS certificate store.</div>
    </div>
  </div>
</div>

<h3>Let's Encrypt tab</h3>
<div class="screenshot-wrap">
  <img src="./images/9.png" alt="SSL TLS Let's Encrypt tab">
  <div class="screenshot-caption">fig 9 — Let's Encrypt: Certbot DNS-01 challenge via BIND9 TSIG key</div>
</div>

<p>Issues <strong>globally browser-trusted</strong> Let's Encrypt certificates using the <strong>DNS-01 ACME challenge</strong> via your local BIND9 server. This means <strong>no port 80 or public IP is required</strong> — Certbot writes a temporary TXT record into your BIND9 zone, proves domain ownership, then removes it.</p>

<div class="callout danger">
  <span class="callout-icon">❗</span>
  <div><strong>Domain must be publicly resolvable.</strong> Let's Encrypt's validation servers must be able to look up a TXT record on your domain. This means you must own a real, registered domain (e.g. <code>*.yourdomain.com</code>) and have its NS records pointing somewhere public. This tab does <em>not</em> work with private <code>.localnet</code> TLDs.</div>
</div>

<p>The implementation generates a TSIG key (<code>tsig-keygen</code>), writes an <code>rfc2136.ini</code> credentials file, and runs <code>certbot certonly --dns-rfc2136</code>. The resulting cert appears in <code>/etc/letsencrypt/live/{domain}/</code>.</p>
</section>

<!-- ═══════════════ UI: AD BLOCKING ═══════════════ -->
<section>
<a class="section-anchor" id="ui-adblock"></a>
<h2>🚫 Ad Blocking</h2>

<div class="screenshot-wrap">
  <img src="./images/10.png" alt="Ad Blocking page">
  <div class="screenshot-caption">fig 10 — Ad Blocking: 175,540 blocked domains via BIND9 RPZ, enable/disable/update controls</div>
</div>

<p>Network-wide ad blocking implemented entirely at the <strong>DNS layer</strong> using BIND9's <strong>Response Policy Zone (RPZ)</strong> feature. No separate proxy or additional software is needed.</p>

<h3>How it works</h3>
<ol>
  <li>Downloads the <a href="https://github.com/StevenBlack/hosts" target="_blank">StevenBlack unified hosts list</a> (100,000–200,000 ad/tracker/malware domains)</li>
  <li>Builds a BIND9 RPZ zone file at <code>/etc/bind/adblock/db.rpz.adblock</code> with <code>CNAME .</code> entries for every domain (and its wildcard)</li>
  <li>Declares the zone in <code>named.conf.local</code> and adds a <code>response-policy</code> directive to <code>named.conf.options</code></li>
  <li>Reloads BIND9 — blocked domains return <strong>NXDOMAIN</strong> to all clients on the network instantly</li>
</ol>

<p>The current entry count is read live from the zone file by counting <code>CNAME</code> occurrences. Click <strong>Update List</strong> to re-download and regenerate the zone with the latest blocklist.</p>

<div class="callout info">
  <span class="callout-icon">ℹ️</span>
  <div>Ad blocking requires BIND9 to be installed and running. It integrates directly with your existing DNS setup — no additional ports or services.</div>
</div>
</section>

<!-- ═══════════════ UI: BACKUPS ═══════════════ -->
<section>
<a class="section-anchor" id="ui-backups"></a>
<h2>💾 Backups &amp; Restore</h2>

<div class="screenshot-wrap">
  <img src="./images/11.png" alt="Backups and Restore page">
  <div class="screenshot-caption">fig 11 — Backups: automatic snapshot history with restore and delete per entry</div>
</div>

<p>Before every install, remove, or modify operation, LocalNet Manager automatically creates a ZIP snapshot of <code>/etc/bind</code> and <code>/etc/nginx</code>. Backups are stored in <code>/etc/localnet/backups/</code> and logged to the SQLite database.</p>

<h3>Backup file naming</h3>
<pre><code>backup_{YYYYMMDD}_{HHMMSS}_{sanitized_label}.zip

<span class="cm">Example:</span>
backup_20280417_170918_generate_cert___auto_configure__mypc_loc.zip</code></pre>

<h3>Operations</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Action</th><th>Behavior</th></tr></thead>
  <tbody>
    <tr><td><strong>Create Snapshot Now</strong></td><td>Manually trigger a backup with label "manual"</td></tr>
    <tr><td><strong>Restore</strong></td><td>Extracts the ZIP to <code>/</code>, then restarts BIND9 and Nginx automatically</td></tr>
    <tr><td><strong>Delete</strong></td><td>Removes the ZIP file and its database record</td></tr>
    <tr><td><strong>Refresh</strong></td><td>Rescans the backup directory for any ZIPs not in the database</td></tr>
  </tbody>
</table>
</div>

<div class="callout success">
  <span class="callout-icon">✅</span>
  <div>Up to 20 most recent backups are shown. The backup directory is also scanned on each load in case backups exist that aren't tracked in the database (e.g. manually copied files).</div>
</div>
</section>

<!-- ═══════════════ UI: SYSTEM LOGS ═══════════════ -->
<section>
<a class="section-anchor" id="ui-logs"></a>
<h2>📜 System Logs</h2>

<div class="screenshot-wrap">
  <img src="./images/12.png" alt="System Logs page">
  <div class="screenshot-caption">fig 12 — System Logs: live journalctl stream for DHCP service</div>
</div>

<p>Streams <code>journalctl -fu {service}</code> output live via Server-Sent Events. Available log tabs:</p>

<div class="table-wrap">
<table>
  <thead><tr><th>Tab</th><th>journalctl unit</th></tr></thead>
  <tbody>
    <tr><td>BIND9</td><td><code>named</code></td></tr>
    <tr><td>Nginx</td><td><code>nginx</code></td></tr>
    <tr><td>DHCP</td><td><code>isc-dhcp-server</code></td></tr>
    <tr><td>Resolved</td><td><code>systemd-resolved</code></td></tr>
  </tbody>
</table>
</div>

<p>The stream starts with the last 100 journal lines, then follows new entries in real time. Navigation away from the Logs page automatically kills the SSE connection via the overridden <code>navigate()</code> function.</p>
</section>

<!-- ═══════════════ UI: NETWORK ═══════════════ -->
<section>
<a class="section-anchor" id="ui-network"></a>
<h2>🔌 Network Interfaces</h2>

<div class="screenshot-wrap">
  <img src="./images/13.png" alt="Network Interfaces page">
  <div class="screenshot-caption">fig 13 — Network Interfaces: detected non-loopback IPv4 interfaces with state and subnet</div>
</div>

<p>Displays all non-loopback, non-Docker, non-bridge IPv4 network interfaces detected via <code>ip -j addr</code>. Shows interface name, IP address, prefix length, state (UP/DOWN), and computed subnet.</p>

<p>The multi-subnet tip at the bottom explains how to add additional subnets to the BIND9 <code>trusted_network</code> ACL for multi-VLAN environments.</p>
</section>

<!-- ═══════════════ UI: SETTINGS ═══════════════ -->
<section>
<a class="section-anchor" id="ui-settings"></a>
<h2>⚙ Settings</h2>

<div class="screenshot-wrap">
  <img src="./images/14.png" alt="Settings page">
  <div class="screenshot-caption">fig 14 — Settings: general config, change password, quick service controls</div>
</div>

<h3>General Settings</h3>
<p>Saved to <code>/etc/localnet/config.json</code> but <strong>do not apply to a running DNS install</strong> — re-run Install DNS Server to apply domain or forwarder changes.</p>

<div class="table-wrap">
<table>
  <thead><tr><th>Setting</th><th>Key</th><th>Default</th></tr></thead>
  <tbody>
    <tr><td>Default Domain (TLD)</td><td><code>domain</code></td><td><code>localnet</code></td></tr>
    <tr><td>DNS Forwarders</td><td><code>forwarders</code></td><td><code>["1.1.1.2","1.0.0.2"]</code></td></tr>
    <tr><td>VPN-Compatible Mode</td><td><code>vpn_safe</code></td><td><code>true</code></td></tr>
  </tbody>
</table>
</div>

<h3>Change Password</h3>
<p>Requires the current password. New password must be at least 6 characters. Stored as <code>hashlib.sha256(pw.encode()).hexdigest()</code> in config.json under the key <code>password_hash</code>.</p>

<h3>Quick Service Controls</h3>
<p>Reload BIND9, Reload Nginx, or Restart systemd-resolved without leaving the page. These call <code>POST /api/service/reload</code> with the service name.</p>
</section>

<!-- ═══════════════ API REFERENCE ═══════════════ -->
<section>
<a class="section-anchor" id="api-auth"></a>
<h2>🔐 API — Auth</h2>

<p>All API endpoints (except <code>GET /login</code> and <code>POST /login</code>) require an active session cookie. Unauthenticated requests to <code>/api/*</code> return HTTP 401 <code>{"error":"Unauthorized"}</code>. Non-API routes redirect to <code>/login</code>.</p>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/login</span>
    <span class="endpoint-desc">Authenticate and create session</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Form data:</strong> <code>password</code> (string)</p>
    <p>Validates against stored SHA-256 hash (or default <code>localnet</code> on first run). On success, sets <code>session["authed"] = True</code> and redirects to <code>/</code>. On failure, re-renders login page with error.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/logout</span>
    <span class="endpoint-desc">Clear session and redirect to login</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Calls <code>session.clear()</code> and redirects to <code>/login</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/auth/change-password</span>
    <span class="endpoint-desc">Change the web UI password</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Body:</strong></p>
    <pre><code>{ "current": "oldpassword", "new": "newpassword" }</code></pre>
    <p><strong>Returns 403</strong> if current password is wrong. <strong>Returns 400</strong> if new password is shorter than 6 characters. On success, updates <code>password_hash</code> in config.json.</p>
    <pre><code>{ "ok": true }</code></pre>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-status"></a>
<h2>📊 API — Status &amp; Config</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/status</span>
    <span class="endpoint-desc">Overall system status snapshot</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Returns service states (via <code>systemctl is-active</code>), record/proxy/cert counts, server IP, domain, and the first 300 chars of <code>/etc/resolv.conf</code>.</p>
    <pre><code>{
  "services":     { "bind9": "active", "nginx": "active", "systemd-resolved": "active" },
  "record_count": 3,
  "proxy_count":  2,
  "cert_count":   1,
  "resolv":       "# This is /run/systemd/resolve/stub-resolv.conf...",
  "is_root":      true,
  "server_ip":    "192.168.1.112",
  "domain":       "localnet"
}</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/config</span>
    <span class="endpoint-desc">Read current configuration + detected interfaces</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{
  "domain":        "localnet",
  "vpn_safe":      true,
  "server_ip":     "192.168.1.112",
  "forwarders":    ["1.1.1.2", "1.0.0.2"],
  "adblock_enabled": false,
  "interfaces":    [{ "name": "wlp3s0", "ip": "192.168.1.112", "prefix": 24, "state": "UP" }]
}</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/config</span>
    <span class="endpoint-desc">Save configuration (non-destructive)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Body:</strong> Any subset of config keys (<code>domain</code>, <code>forwarders</code>, <code>vpn_safe</code>). Only keys present in <code>DEFAULT_CONFIG</code> are merged.</p>
    <pre><code>{ "ok": true }</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/network/interfaces</span>
    <span class="endpoint-desc">List detected network interfaces</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Returns all non-loopback, non-Docker IPv4 interfaces as parsed by <code>ip -j addr</code>.</p>
    <pre><code>[{ "name": "wlp3s0", "ip": "192.168.1.112", "prefix": 24, "state": "UP" }]</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/service/reload</span>
    <span class="endpoint-desc">Reload or restart a system service</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Body:</strong></p>
    <pre><code>{ "service": "bind9" }</code></pre>
    <p>Allowed values: <code>bind9</code> (reload), <code>nginx</code> (reload), <code>systemd-resolved</code> (restart). Returns 400 for any other value.</p>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-dns"></a>
<h2>🌐 API — DNS</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/install</span>
    <span class="endpoint-desc">Install and configure BIND9 (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Body:</strong></p>
    <pre><code>{
  "domain":   "localnet",
  "server_ip": "192.168.1.112",
  "vpn_safe":  true,
  "forwarders": ["1.1.1.2", "1.0.0.2"]
}</code></pre>
    <p>Runs an 8-step bash install script asynchronously. Progress streams through <code>/api/logs/stream</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/remove</span>
    <span class="endpoint-desc">Purge BIND9 and restore system DNS (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Stops and purges <code>bind9 bind9utils bind9-doc dnsutils</code>, removes <code>/etc/bind</code> and the resolved drop-in config, restarts systemd-resolved.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/dns/records</span>
    <span class="endpoint-desc">List all zone records</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Parses <code>/etc/bind/db.{domain}</code> and returns A, CNAME, MX, TXT, AAAA records (excludes SOA/NS/@).</p>
    <pre><code>[
  { "host": "ns1",  "type": "A",     "value": "192.168.1.112" },
  { "host": "mypc", "type": "A",     "value": "192.168.1.112" },
  { "host": "dash", "type": "CNAME", "value": "mypc.localnet." }
]</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/records/a</span>
    <span class="endpoint-desc">Add an A record (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "host": "nas", "ip": "192.168.1.20" }</code></pre>
    <p>Appends <code>nas  IN  A  192.168.1.20</code> to the zone file, appends a PTR record to the reverse zone, bumps serial, and reloads BIND9.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/records/cname</span>
    <span class="endpoint-desc">Add a CNAME record (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "alias": "movies", "target": "nas" }</code></pre>
    <p>Creates <code>movies.localnet → nas.localnet.</code></p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/records/txt</span>
    <span class="endpoint-desc">Add a TXT record (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "host": "_dmarc", "value": "v=DMARC1; p=none" }</code></pre>
    <p>Value is automatically wrapped in double quotes if not already present.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/records/srv</span>
    <span class="endpoint-desc">Add an SRV record (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{
  "service":  "_http",
  "proto":    "_tcp",
  "priority": 10,
  "weight":   5,
  "port":     8080,
  "target":   "mypc"
}</code></pre>
    <p>Writes: <code>_http._tcp  IN  SRV  10 5 8080 mypc.localnet.</code></p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/records/wildcard</span>
    <span class="endpoint-desc">Add a wildcard A record (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "ip": "192.168.1.112" }</code></pre>
    <p>Writes: <code>*  IN  A  192.168.1.112</code> — all unmatched subdomains resolve to this IP.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method delete">DELETE</span>
    <span class="endpoint-path">/api/dns/records/&lt;host&gt;</span>
    <span class="endpoint-desc">Remove all records for a hostname (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Runs <code>sed -i '/^{host}/d'</code> on the forward zone and removes the matching PTR entry from the reverse zone. Bumps serial and reloads.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/test</span>
    <span class="endpoint-desc">Run a DNS lookup test via dig</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "name": "nas.localnet", "server": "192.168.1.112" }</code></pre>
    <p>Runs <code>dig @{server} {name} +short +time=2</code>. Returns:</p>
    <pre><code>{ "result": "192.168.1.20", "ok": true }</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dns/notes</span>
    <span class="endpoint-desc">Set a note on a DNS record</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "host": "nas", "note": "My NAS server" }</code></pre>
    <p>Stored in SQLite <code>record_notes</code> table keyed by (host, domain).</p>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-nginx"></a>
<h2>↔ API — Nginx</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/nginx/install</span>
    <span class="endpoint-desc">Install Nginx (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Runs <code>apt-get install -y nginx</code>, removes the default site, and enables the service.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/nginx/uninstall</span>
    <span class="endpoint-desc">Purge Nginx (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Stops, purges <code>nginx nginx-common nginx-full</code>, and removes <code>/etc/nginx</code> and <code>/var/log/nginx</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/nginx/proxies</span>
    <span class="endpoint-desc">List active proxies</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>[
  { "domain": "dash.localnet", "port": "8091", "template": "basic" },
  { "domain": "mypc.localnet", "port": "8091", "template": "basic" }
]</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/nginx/proxies</span>
    <span class="endpoint-desc">Add a new proxy (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{
  "domain":      "movies.localnet",
  "template":    "basic",
  "upstream_ip": "127.0.0.1",
  "port":        "8096",
  "extras":      {}
}</code></pre>
    <p>For the <code>loadbalancer</code> template, pass <code>"extras": { "upstreams": "192.168.1.10:8080\n192.168.1.11:8080" }</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method delete">DELETE</span>
    <span class="endpoint-path">/api/nginx/proxies/&lt;domain&gt;</span>
    <span class="endpoint-desc">Remove a proxy (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Deletes <code>/etc/nginx/sites-available/{domain}</code> and its symlink in <code>sites-enabled/</code>, then reloads Nginx.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/nginx/templates</span>
    <span class="endpoint-desc">List available proxy templates</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{
  "basic":         { "label": "Basic Proxy",      "desc": "Simple HTTP reverse proxy", "icon": "⇌", "color": "#4a9eff" },
  "websocket":     { "label": "WebSocket",         "desc": "WebSocket-capable (Grafana, Jupyter, etc.)", ... },
  "homeassistant": { "label": "Home Assistant",    "desc": "Long-poll + WebSocket for HA", ... },
  "nextcloud":     { "label": "Nextcloud",         "desc": "Large uploads, CalDAV/CardDAV", ... },
  "loadbalancer":  { "label": "Load Balancer",     "desc": "Round-robin multiple upstreams", ... }
}</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/nginx/notes</span>
    <span class="endpoint-desc">Set a note on a proxy</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "domain": "movies.localnet", "note": "Jellyfin media server" }</code></pre>
    <p>Stored in SQLite <code>proxy_notes</code> table keyed by domain.</p>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-dhcp"></a>
<h2>📡 API — DHCP</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dhcp/install</span>
    <span class="endpoint-desc">Install and configure ISC-DHCP-Server (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{
  "server_ip":   "192.168.1.112",
  "router":      "192.168.1.1",
  "range_start": "192.168.1.100",
  "range_end":   "192.168.1.200",
  "lease_time":  3600
}</code></pre>
    <p>All fields are optional with sensible defaults derived from the detected server IP.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/dhcp/remove</span>
    <span class="endpoint-desc">Purge ISC-DHCP-Server (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Stops, disables, and purges <code>isc-dhcp-server</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/dhcp/leases</span>
    <span class="endpoint-desc">List active DHCP leases</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Parses <code>/var/lib/dhcp/dhcpd.leases</code>. Returns only leases with <code>binding state active</code>.</p>
    <pre><code>[{ "ip": "192.168.1.105", "mac": "aa:bb:cc:dd:ee:ff", "hostname": "laptop", "starts": "2028/04/17 17:00:00", "ends": "2028/04/17 18:00:00", "state": "active" }]</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/dhcp/status</span>
    <span class="endpoint-desc">Check if DHCP server is running</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "active": true }</code></pre>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-ssl"></a>
<h2>🔒 API — SSL / TLS</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/ssl/mkcert/install</span>
    <span class="endpoint-desc">Install mkcert and create local CA (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Downloads the latest mkcert binary for the system architecture, places it at <code>/usr/local/bin/mkcert</code>, and runs <code>CAROOT=/etc/localnet/ca mkcert -install</code> to create and trust the local CA.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/ssl/mkcert/cert</span>
    <span class="endpoint-desc">Generate a mkcert certificate (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "domain": "mypc.localnet" }</code></pre>
    <p>If domain is blank or omitted, defaults to the configured TLD (effectively a wildcard). The cert is signed with three SANs: <code>{domain}</code>, <code>*.{tld}</code>, <code>{tld}</code>. Files are saved to <code>/etc/localnet/certs/{domain}.pem</code> and <code>{domain}-key.pem</code>. Automatically injects SSL config into a matching Nginx site if found.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/ssl/certs</span>
    <span class="endpoint-desc">List issued mkcert certificates</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>[{ "name": "mypc.localnet", "path": "/etc/localnet/certs/mypc.localnet.pem" }]</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method delete">DELETE</span>
    <span class="endpoint-path">/api/ssl/certs/&lt;domain&gt;</span>
    <span class="endpoint-desc">Delete a cert and clean Nginx config (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Removes the <code>.pem</code> and <code>-key.pem</code> files, then strips <code>listen 443 ssl;</code> and all <code>ssl_*</code> directives from the matching Nginx site config and reloads.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/ssl/rootca</span>
    <span class="endpoint-desc">Download the local Root CA certificate</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Serves <code>/etc/localnet/ca/rootCA.pem</code> as a download named <code>LocalNet-Root-CA.pem</code>. Returns 404 if mkcert hasn't been installed yet.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/ssl/certbot/install</span>
    <span class="endpoint-desc">Install Certbot with DNS-RFC2136 plugin (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Installs <code>certbot</code> and <code>python3-certbot-dns-rfc2136</code> via apt-get.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/ssl/certbot/cert</span>
    <span class="endpoint-desc">Request a Let's Encrypt cert via DNS-01 (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "email": "you@example.com", "domain": "*.yourdomain.com" }</code></pre>
    <p>Generates a TSIG key, writes <code>/etc/localnet/certbot/rfc2136.ini</code>, and runs <code>certbot certonly --dns-rfc2136</code>. The certificate is placed in <code>/etc/letsencrypt/live/{domain}/</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/ssl/letsencrypt/certs</span>
    <span class="endpoint-desc">List issued Let's Encrypt certificates</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>[{ "name": "yourdomain.com", "cert": "/etc/letsencrypt/live/yourdomain.com/fullchain.pem", "key": "/etc/letsencrypt/live/yourdomain.com/privkey.pem", "exists": true }]</code></pre>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-adblock"></a>
<h2>🚫 API — Ad Blocking</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/adblock/enable</span>
    <span class="endpoint-desc">Download blocklist and enable RPZ ad blocking (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Downloads <code>https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts</code>, builds a BIND9 RPZ zone file, configures BIND9, and reloads. Sets <code>adblock_enabled: true</code> in config.json.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/adblock/disable</span>
    <span class="endpoint-desc">Remove RPZ zone and disable ad blocking (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p>Removes the zone declaration from <code>named.conf.local</code>, removes the <code>response-policy</code> line from <code>named.conf.options</code>, deletes <code>/etc/bind/adblock/</code>, and reloads BIND9.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/adblock/status</span>
    <span class="endpoint-desc">Get ad blocking status and blocked domain count</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "enabled": true, "entry_count": 350880 }</code></pre>
    <p><code>entry_count</code> is read live from the RPZ zone file by counting <code>CNAME</code> occurrences (each blocked domain has two entries: itself and its wildcard).</p>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-backups"></a>
<h2>💾 API — Backups</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/backups</span>
    <span class="endpoint-desc">List all backups</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>[{ "id": 1, "path": "/etc/localnet/backups/backup_20280417_170918_generate_cert.zip", "label": "Generate cert &amp; auto-configure: mypc.localnet", "created_at": "2028-04-17T17:09:18" }]</code></pre>
    <p>Merges SQLite records with a filesystem scan — ZIPs present on disk but missing from the DB are included.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/backups/create</span>
    <span class="endpoint-desc">Create a manual backup (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "label": "pre-migration" }</code></pre>
    <pre><code>{ "ok": true, "path": "/etc/localnet/backups/backup_20280417_171000_pre_migration.zip" }</code></pre>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/backups/restore</span>
    <span class="endpoint-desc">Restore a backup (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "path": "/etc/localnet/backups/backup_20280417_171000_pre_migration.zip" }</code></pre>
    <p>Extracts the ZIP to <code>/</code> (restoring both <code>/etc/bind</code> and <code>/etc/nginx</code>), then restarts BIND9 and Nginx asynchronously.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method post">POST</span>
    <span class="endpoint-path">/api/backups/delete</span>
    <span class="endpoint-desc">Delete a backup (root required)</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <pre><code>{ "path": "/etc/localnet/backups/backup_20280417_171000_pre_migration.zip" }</code></pre>
    <p>Deletes the ZIP file and removes the database record.</p>
  </div>
</div>
</section>

<section>
<a class="section-anchor" id="api-logs"></a>
<h2>📜 API — Logs</h2>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/logs/stream</span>
    <span class="endpoint-desc">SSE stream of LocalNet application log</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Content-Type:</strong> <code>text/event-stream</code></p>
    <p>Replays the last 80 log entries from the in-memory ring buffer (max 1000 entries), then streams new entries as they are produced. Sends a <code>ping</code> event every 20 seconds to keep the connection alive. Each event is a JSON object:</p>
    <pre><code>data: {"t": "18:51:52", "msg": "LocalNet Manager v4 started", "level": "success"}

data: {"type": "ping"}</code></pre>
    <p><code>level</code> values: <code>info</code>, <code>success</code>, <code>error</code>.</p>
  </div>
</div>

<div class="endpoint">
  <div class="endpoint-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="method get">GET</span>
    <span class="endpoint-path">/api/logs/journal?service=bind9&amp;tail=100</span>
    <span class="endpoint-desc">SSE stream of journalctl for a system service</span>
    <span class="endpoint-toggle">▼</span>
  </div>
  <div class="endpoint-body">
    <p><strong>Query params:</strong></p>
    <ul>
      <li><code>service</code>: one of <code>bind9</code>, <code>nginx</code>, <code>dhcp</code>, <code>resolved</code> (default: <code>bind9</code>)</li>
      <li><code>tail</code>: number of historical lines to show (default: <code>100</code>)</li>
    </ul>
    <p>Runs <code>journalctl -fu {unit} --no-pager -n {tail} --output=short</code> as a subprocess and streams each line as:</p>
    <pre><code>data: {"msg": "Apr 17 18:51:52 named[1234]: zone localnet/IN: loaded serial 1713376312"}</code></pre>
    <p>The subprocess is killed when the SSE connection closes.</p>
  </div>
</div>
</section>

<!-- ═══════════════ CONFIG FILE ═══════════════ -->
<section>
<a class="section-anchor" id="config-file"></a>
<h2>📄 Configuration File</h2>

<p>Stored at <code>/etc/localnet/config.json</code> (falls back to <code>/tmp/localnet_v4/</code> when not root).</p>

<pre><code>{
  <span class="str">"domain"</span>:         <span class="str">"localnet"</span>,       <span class="cm">// Private TLD for all DNS records</span>
  <span class="str">"vpn_safe"</span>:       <span class="kw">true</span>,             <span class="cm">// Route through systemd-resolved stub</span>
  <span class="str">"server_ip"</span>:      <span class="str">"192.168.1.112"</span>,  <span class="cm">// Auto-detected; baked into BIND9 config</span>
  <span class="str">"forwarders"</span>:     [<span class="str">"1.1.1.2"</span>, <span class="str">"1.0.0.2"</span>], <span class="cm">// Cloudflare for Families (default)</span>
  <span class="str">"password_hash"</span>:  <span class="str">"sha256hex..."</span>,   <span class="cm">// SHA-256 of web UI password</span>
  <span class="str">"secret_key"</span>:     <span class="str">"hex64..."</span>,       <span class="cm">// Flask session secret (auto-generated)</span>
  <span class="str">"adblock_enabled"</span>:<span class="kw">false</span>             <span class="cm">// Persisted adblock toggle state</span>
}</code></pre>

<h3>Important paths</h3>
<div class="table-wrap">
<table>
  <thead><tr><th>Path</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>/etc/localnet/config.json</code></td><td>Application configuration</td></tr>
    <tr><td><code>/etc/localnet/localnet.db</code></td><td>SQLite: notes, backup history</td></tr>
    <tr><td><code>/etc/localnet/certs/</code></td><td>mkcert-issued certificates</td></tr>
    <tr><td><code>/etc/localnet/ca/</code></td><td>mkcert local CA root</td></tr>
    <tr><td><code>/etc/localnet/backups/</code></td><td>ZIP backup snapshots</td></tr>
    <tr><td><code>/etc/localnet/certbot/</code></td><td>Certbot TSIG key and rfc2136.ini</td></tr>
    <tr><td><code>/etc/bind/db.{domain}</code></td><td>BIND9 forward zone file</td></tr>
    <tr><td><code>/etc/bind/named.conf.options</code></td><td>BIND9 global options (ACL, forwarders)</td></tr>
    <tr><td><code>/etc/bind/named.conf.local</code></td><td>BIND9 zone declarations</td></tr>
    <tr><td><code>/etc/bind/adblock/db.rpz.adblock</code></td><td>Ad blocking RPZ zone</td></tr>
    <tr><td><code>/etc/nginx/sites-available/</code></td><td>Nginx proxy config files</td></tr>
    <tr><td><code>/etc/nginx/sites-enabled/</code></td><td>Nginx active proxy symlinks</td></tr>
    <tr><td><code>/etc/dhcp/dhcpd.conf</code></td><td>ISC-DHCP-Server configuration</td></tr>
    <tr><td><code>/etc/systemd/resolved.conf.d/localnet.conf</code></td><td>systemd-resolved DNS routing</td></tr>
    <tr><td><code>/tmp/_localnet_v4.sh</code></td><td>Temporary script file for each operation</td></tr>
  </tbody>
</table>
</div>
</section>

<!-- ═══════════════ NGINX TEMPLATES ═══════════════ -->
<section>
<a class="section-anchor" id="nginx-tmpls"></a>
<h2>📐 Nginx Proxy Templates</h2>

<p>Templates are rendered with simple <code>.replace()</code> substitution (not f-strings) so Nginx variables like <code>$host</code> and <code>$remote_addr</code> are preserved literally.</p>

<h3>basic</h3>
<pre><code><span class="cm"># template: basic</span>
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
}</code></pre>

<h3>websocket</h3>
<pre><code><span class="cm"># template: websocket — adds Upgrade headers and 24h timeouts</span>
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_read_timeout 86400;
proxy_send_timeout 86400;</code></pre>

<h3>homeassistant</h3>
<pre><code><span class="cm"># template: homeassistant — WebSocket + dedicated /api/websocket location, 1h timeouts</span></code></pre>

<h3>nextcloud</h3>
<pre><code><span class="cm"># template: nextcloud — 10GB body size, CalDAV/CardDAV redirects, 5min timeouts, no buffering</span>
client_max_body_size 10G;
proxy_request_buffering off;
location /.well-known/carddav { return 301 $scheme://$host/remote.php/dav; }
location /.well-known/caldav  { return 301 $scheme://$host/remote.php/dav; }</code></pre>

<h3>loadbalancer</h3>
<pre><code><span class="cm"># template: loadbalancer — upstream block with keepalive, round-robin by default</span>
upstream {DOMAIN}_backend {
    server 192.168.1.10:8080;
    server 192.168.1.11:8080;
    keepalive 32;
}
server { proxy_pass http://{DOMAIN}_backend; }</code></pre>
<p>The upstream name is derived from the domain with non-alphanumeric characters replaced by underscores.</p>
</section>

<!-- ═══════════════ SECURITY ═══════════════ -->
<section>
<a class="section-anchor" id="security"></a>
<h2>🛡 Security Notes</h2>

<div class="callout danger">
  <span class="callout-icon">❗</span>
  <div><strong>This application is designed for trusted LAN use only.</strong> It runs on port 8091 with no TLS by default. Do not expose port 8091 to the internet.</div>
</div>

<h3>Authentication implementation</h3>
<ul>
  <li>Password stored as <code>hashlib.sha256(pw.encode()).hexdigest()</code> — not salted. Adequate for a single-user LAN tool, but not production-grade.</li>
  <li>Comparison uses <code>hmac.compare_digest()</code> to prevent timing attacks.</li>
  <li>Flask secret key is a 64-character hex string generated with <code>secrets.token_hex(32)</code> and persisted in config.json so sessions survive restarts.</li>
  <li>All API endpoints except <code>/login</code> are guarded by <code>@app.before_request → require_auth</code>.</li>
</ul>

<h3>Shell injection considerations</h3>
<p>All DNS hostnames, IPs, and domain values passed to shell scripts are inserted using Python f-strings. Values from user input are used directly in <code>sed</code> and <code>echo</code> commands. For extra safety, consider sanitizing inputs before submission — the UI performs basic client-side validation but the backend trusts the values it receives.</p>

<h3>Backup security</h3>
<p>Backups contain your full BIND9 and Nginx configuration. Store the <code>/etc/localnet/backups/</code> directory securely or restrict access.</p>

<h3>Self-hosting the UI over HTTPS</h3>
<p>To serve the LocalNet Manager itself over HTTPS, generate a mkcert cert for <code>dash.localnet</code> (or your chosen name), then add an Nginx proxy pointing to <code>localhost:8091</code> using the mkcert cert for TLS termination.</p>
</section>

<!-- ═══════════════ TROUBLESHOOTING ═══════════════ -->
<section>
<a class="section-anchor" id="troubleshoot"></a>
<h2>🔧 Troubleshooting</h2>

<h3>DNS names don't resolve from other devices</h3>
<ol>
  <li>Make sure DHCP is installed and configured with your LocalNet server's IP as the DNS server.</li>
  <li>Or manually set each device's DNS server to the LocalNet server IP.</li>
  <li>Verify with: <code>dig @192.168.1.112 nas.localnet +short</code></li>
</ol>

<h3>BIND9 fails to start after editing records</h3>
<pre><code>sudo named-checkconf
sudo named-checkzone localnet /etc/bind/db.localnet</code></pre>
<p>Use the Backups page to restore the last known-good configuration.</p>

<h3>Nginx returns "502 Bad Gateway"</h3>
<p>The upstream service is not running or the port is wrong. Verify the upstream: <code>curl http://127.0.0.1:&lt;port&gt;</code>.</p>

<h3>mkcert cert not trusted in browser</h3>
<p>You must import the Root CA (<code>/etc/localnet/ca/rootCA.pem</code>) into the browser's or OS's certificate store on <em>each device</em> that needs to trust the certs. The "Click here to download 'Root CA'" link on the SSL page serves this file directly.</p>

<h3>Application shows "(Root: NO)" warning</h3>
<p>The app was not started with <code>sudo</code>. Most write operations will return HTTP 403. Restart with: <code>sudo python3 localnet_v4_alpha_b.py</code></p>

<h3>Log stream disconnects frequently</h3>
<p>The SSE stream sends a ping every 20 seconds. Reverse proxies with short read timeouts (e.g. Nginx default 60s) may close the connection. If running LocalNet Manager behind Nginx, add <code>proxy_read_timeout 3600;</code> to the proxy config.</p>

<h3>Config saved in /tmp instead of /etc/localnet</h3>
<p>Running without root. Configuration and database are stored in <code>/tmp/localnet_v4/</code> and will be lost on reboot. Always run as root for persistent storage.</p>
</section>

<!-- ─── Footer ─── -->
<div style="margin-top:60px; padding-top:24px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; color:var(--dim2); font-size:12px;">
  <span>⬡ LocalNet Manager v4 — Alpha Documentation</span>
  <span style="font-family:var(--mono);">localnet_v4_alpha_b.py</span>
</div>

</main>

<script>
  // ── Active nav link tracking ─────────────────────────
  const sections = document.querySelectorAll('a.section-anchor');
  const navLinks  = document.querySelectorAll('a.nav-link');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const id = e.target.id;
        navLinks.forEach(l => {
          l.classList.toggle('active', l.getAttribute('href') === '#' + id);
        });
      }
    });
  }, { rootMargin: '-20% 0px -75% 0px' });

  sections.forEach(s => observer.observe(s));

  // ── Endpoint toggle ───────────────────────────────────
  document.querySelectorAll('.endpoint-header').forEach(h => {
    h.addEventListener('click', () => {
      h.parentElement.classList.toggle('open');
    });
  });
</script>
</body>
</html>
