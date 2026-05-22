# Setup

How this app and its surrounding bench were brought up on a fresh Ubuntu 24.04 machine.

## Stack

| Component | Version |
|---|---|
| OS | Ubuntu 24.04.4 LTS (noble) |
| Python | 3.14.5 (via deadsnakes PPA — Frappe v16 pins `>=3.14,<3.15`) |
| Node | 24.16.0 (Krypton LTS — Frappe v16 needs `>=24`) |
| yarn | 1.22.22 |
| MariaDB | 10.11.x (Ubuntu default, configured for utf8mb4) |
| Redis | 7.0.x |
| wkhtmltopdf | 0.12.6.1 with patched Qt (the apt version is unpatched — do not use) |
| Frappe | v16.18.3 (branch `version-16`) |
| ERPNext | v16.19.1 (branch `version-16`) |
| bench | 5.29.1 (installed via pipx with Python 3.14) |
| uv | 0.11.16 (required by bench 5.29+ for venv/pip operations) |

## Directory layout

```
~/work/now/tdn-print-manager/                     workspace (not a git repo)
├── tdn_print_manager_findings.md                 customization audit of the source ERPNext tenant
├── 99-frappe.cnf                                 MariaDB drop-in config (utf8mb4)
└── frappe-bench/                                 bench infrastructure (not committed)
    ├── apps/
    │   ├── frappe/                               upstream
    │   ├── erpnext/                              upstream
    │   └── tdn_print_manager/                    this repo
    ├── sites/tdn.localhost/                      site data + DB creds
    └── env/                                      Python 3.14 venv
```

Only `apps/tdn_print_manager/` is committed to git. The bench, the site data, and the venv are local infrastructure each developer recreates with `bench init`.

## System prerequisites (one-time)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y \
    python3.14 python3.14-dev python3.14-venv \
    libmariadb-dev libxml2-dev libxslt1-dev libffi-dev libjpeg-dev zlib1g-dev \
    pipx redis-server mariadb-server mariadb-client

# Node 24 via nvm
nvm install 24
nvm alias default 24
npm i -g yarn

# wkhtmltopdf with patched Qt — apt's version is unpatched, do not use
wget -P /tmp https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb
sudo apt install -y /tmp/wkhtmltox_0.12.6.1-3.jammy_amd64.deb

# bench + uv
pipx install --python python3.14 frappe-bench
pipx install uv
pipx ensurepath
```

## MariaDB configuration

```bash
# Set a root password (Frappe needs password auth, not socket auth)
sudo mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'frappe-dev-root'; FLUSH PRIVILEGES;"

# Drop in utf8mb4 charset config
sudo cp 99-frappe.cnf /etc/mysql/mariadb.conf.d/
sudo systemctl restart mariadb
```

Contents of `99-frappe.cnf`:

```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
```

## Bench + ERPNext + site

```bash
cd ~/work/now/tdn-print-manager

bench init --frappe-branch version-16 --python /usr/bin/python3.14 frappe-bench
cd frappe-bench

bench get-app erpnext --branch version-16
bench new-site tdn.localhost --db-root-password frappe-dev-root --admin-password admin
bench --site tdn.localhost install-app erpnext
```

## This app

```bash
cd ~/work/now/tdn-print-manager/frappe-bench
bench new-app tdn_print_manager
bench --site tdn.localhost install-app tdn_print_manager
```

Created with:
- App title: TDN Print Manager
- Publisher: Blurd Technologies Private Limited
- Email: contact@3dn.app
- License: MIT
- Default branch: main

## Running

```bash
cd ~/work/now/tdn-print-manager/frappe-bench
nvm use 24
bench start
```

Site at <http://tdn.localhost:8000>. Login `Administrator` / `admin`.

## Local credentials (dev only)

- MariaDB root: `frappe-dev-root`
- Frappe Administrator: `admin`

Both are local-dev placeholders. Change for any non-dev environment.
