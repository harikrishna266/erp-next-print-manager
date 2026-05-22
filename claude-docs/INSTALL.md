# Install

How to get this app running on a fresh Ubuntu 24.04 (or similar Debian-based)
machine. See [SETUP.md](SETUP.md) for the stack versions this targets.

## 1. System packages

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y \
    python3.14 python3.14-dev python3.14-venv \
    libmariadb-dev libxml2-dev libxslt1-dev libffi-dev libjpeg-dev zlib1g-dev \
    pipx redis-server mariadb-server mariadb-client
```

## 2. Node 24 + yarn

Install nvm from <https://github.com/nvm-sh/nvm> if you don't have it, then:

```bash
nvm install 24
nvm alias default 24
npm i -g yarn
```

## 3. wkhtmltopdf (patched-Qt build)

The apt version is **not** patched-Qt and will produce broken PDFs. Install
the upstream `.deb`:

```bash
wget -P /tmp https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb
sudo apt install -y /tmp/wkhtmltox_0.12.6.1-3.jammy_amd64.deb
wkhtmltopdf --version    # must print "(with patched qt)"
```

The `jammy` (22.04) build is the latest upstream release and works on noble.

## 4. bench CLI + uv

```bash
pipx install --python python3.14 frappe-bench
pipx install uv
pipx ensurepath
```

Open a new terminal so PATH updates take effect:

```bash
bench --version    # 5.29+
uv --version       # 0.11+
```

## 5. MariaDB

Set a root password (Frappe needs password auth, not the default socket auth)
and configure utf8mb4:

```bash
sudo mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'frappe-dev-root'; FLUSH PRIVILEGES;"

sudo tee /etc/mysql/mariadb.conf.d/99-frappe.cnf > /dev/null <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF

sudo systemctl restart mariadb
```

Change `frappe-dev-root` to anything you like — just remember it for step 8.

## 6. Initialize the bench

```bash
mkdir -p ~/work/tdn-print-manager
cd ~/work/tdn-print-manager

bench init --frappe-branch version-16 --python /usr/bin/python3.14 frappe-bench
cd frappe-bench
```

This takes 5–10 min — it clones Frappe, builds a Python 3.14 venv, installs
all deps, and builds the JS bundles.

## 7. Get ERPNext and this app

```bash
bench get-app erpnext --branch version-16
bench get-app https://github.com/<your-fork>/tdn_print_manager.git
```

Replace the URL with wherever this repo lives. If you only have a local copy
of the app, drop it at `frappe-bench/apps/tdn_print_manager/` manually and
run `bench setup requirements` to install its Python deps.

## 8. Create a site and install both apps on it

```bash
bench new-site tdn.localhost \
    --db-root-password frappe-dev-root \
    --admin-password admin

bench --site tdn.localhost install-app erpnext
bench --site tdn.localhost install-app tdn_print_manager
```

`bench new-site` creates a MariaDB database, runs initial migrations, and
sets up the `Administrator` user.

## 9. Run

```bash
nvm use 24    # if a fresh shell doesn't default to it
bench start
```

Visit <http://tdn.localhost:8000>. Ubuntu's systemd-resolved auto-resolves
`*.localhost` to 127.0.0.1, so no `/etc/hosts` edit is needed.

Login:
- Username: `Administrator`
- Password: `admin` (or whatever you passed to `--admin-password`)

`bench start` runs in the foreground and tails live logs for every process
(web, redis, scheduler, worker, esbuild watch). Stop with Ctrl-C.

---

## Troubleshooting

**`yarn install` fails with `engine "node" is incompatible`** — your shell
has Node 22 active. Run `nvm use 24` and retry. To make it stick, run
`nvm alias default 24`.

**`bench init` fails with `No such file or directory: 'uv'`** — bench 5.29+
requires uv. Install with `pipx install uv` and rerun.

**`bench start` fails with `ModuleNotFoundError: No module named 'tdn_print_manager'`** —
the venv install lost track of the editable install. Re-run
`bench setup requirements` from the bench dir.

**`install-app` fails with `Error 111 connecting to 127.0.0.1:11000`** —
bench's redis isn't running. Start `bench start` in another terminal first
(it launches redis on ports 11000/13000), then run install-app there.

**wkhtmltopdf produces PDFs with broken fonts or page breaks** — you're on
the unpatched apt version. Reinstall the upstream `.deb` from step 3.
