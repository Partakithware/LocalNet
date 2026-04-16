>![IMPORTANT]
>The .py is another test version all in one manager.....and is flawed below is a command that should fix it (run after install).

```
sudo mkdir -p /etc/systemd/resolved.conf.d/
sudo nano /etc/systemd/resolved.conf.d/localnet.conf
```
fill localnet.conf with 
``` 
[Resolve]
DNS=127.0.0.1
Domains=~localnet
```


LocalNet Manager: DNS & Reverse Proxy Toolkit

A collection of Bash scripts for deploying and managing a local DNS server (BIND9) and an Nginx reverse proxy on Debian-based systems.
System Requirements

    OS: Ubuntu, Debian, or derivatives.

    Privileges: Root/Sudo (enforced by script checks).

    Dependencies: bind9, nginx, systemd, and standard GNU utilities (sed, awk, grep).

Script Overview
DNS Management (BIND9)

    setup_dns.sh: Installs BIND9 and configures the localnet domain. It automatically detects the host IP/subnet to set up ACLs and forward/reverse zones.

    manage_dns.sh: Interactive CLI to add/remove A records and CNAMEs. It handles serial increments using Unix timestamps and reloads the service.

    remove_dns.sh: Purges BIND9 packages and deletes all configuration files/zones in /etc/bind.

Proxy Management (Nginx)

    nginx_install.sh: Installs Nginx and removes the default "Welcome" site to clear port 80 for custom routing.

    nginx_manage.sh: Interactive CLI to create or remove Nginx server blocks. Maps local domains to specific internal ports.

    nginx_uninstall.sh: Purges Nginx and deletes all site configurations and logs.

Setup & Implementation
1. Initialize Services

Grant execution permissions and run the installers.
Bash

chmod +x *.sh
sudo ./setup_dns.sh
sudo ./nginx_install.sh

2. Configure DNS Records

Use manage_dns.sh to map hostnames to IP addresses.

    A Records: Maps a name (e.g., nas) to an IP. Also creates the corresponding PTR record.

    CNAMEs: Maps an alias (e.g., vault) to an existing A record.

3. Configure Proxy Routing

Use nginx_manage.sh to route traffic from a domain name to a service port.

    Example: Routing media.localnet to port 8080.

    Result: Nginx creates a config file in /etc/nginx/sites-available/ and links it to sites-enabled/.

Technical Reference
File Locations
Component	Path
DNS Zone Files	/etc/bind/db.localnet (Forward), /etc/bind/db.[Subnet] (Reverse)
DNS Options	/etc/bind/named.conf.options
Nginx Configs	/etc/nginx/sites-available/
Validation Commands

    DNS Status: named-checkconf and systemctl status bind9

    Resolution Test: dig @localhost [hostname].localnet

    Proxy Status: nginx -t and systemctl status nginx

Uninstallation

To revert all changes and remove installed packages:
Bash

sudo ./remove_dns.sh
sudo ./nginx_uninstall.sh

    Note: If remove_dns.sh is used, ensure /etc/resolv.conf is updated to a valid external nameserver (e.g., 1.1.1.1) to maintain internet connectivity.
