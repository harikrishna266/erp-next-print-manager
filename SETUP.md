# Setup

App-level configuration and conventions. For step-by-step instructions to
install and run the app on a fresh machine, see [INSTALL.md](INSTALL.md).

## Stack

The versions this app is built and tested against:

| Component | Version |
|---|---|
| Python | 3.14.x (Frappe v16 pins `>=3.14,<3.15`) |
| Node | 24.x (Frappe v16 needs `>=24`) |
| yarn | 1.22.x |
| MariaDB | 10.11.x |
| Redis | 7.x |
| wkhtmltopdf | 0.12.6.1 with patched Qt |
| Frappe | v16.x (branch `version-16`) |
| ERPNext | v16.x (branch `version-16`) |
| bench | 5.29+ |
| uv | 0.11+ |

## Directory layout

```
~/work/tdn-print-manager/                          workspace (not a git repo)
└── frappe-bench/                                  bench infrastructure (not committed)
    ├── apps/
    │   ├── frappe/                                upstream
    │   ├── erpnext/                                upstream
    │   └── tdn_print_manager/                     this repo
    │       ├── SETUP.md                           this file
    │       ├── INSTALL.md                         from-scratch install steps
    │       └── tdn_print_manager_findings.md      customization audit of the source ERPNext tenant
    ├── sites/tdn.localhost/                       site data + DB creds
    └── env/                                       Python 3.14 venv
```

Only `apps/tdn_print_manager/` is in git. The bench, the site data, and the
venv are local infrastructure each developer recreates with `bench init`.

## App metadata

| | |
|---|---|
| App name | `tdn_print_manager` |
| App title | TDN Print Manager |
| Publisher | Blurd Technologies Private Limited |
| Email | contact@3dn.app |
| License | MIT |
| Default branch | `main` |

## Local credentials (dev only)

- MariaDB root: `frappe-dev-root`
- Frappe Administrator: `admin`

Local-dev placeholders. Change them for any non-dev environment, and don't
commit a `site_config.json` with real secrets.
