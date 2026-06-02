# CLAUDE.md

Guidance for working in the `tdn_print_manager` Frappe app.

## What this is

`tdn_print_manager` is a **Frappe/ERPNext v16 app** implementing a print shop
**MES (Manufacturing Execution System)**. It is being built by porting
customizations (Server Scripts, Client Scripts, Custom DocTypes/Fields) from a
legacy "Jerrys" ERPNext v15 tenant into a proper, version-controlled, testable
app. See `claude-docs/tdn_print_manager_findings.md` for the full inventory and
migration triage of the legacy customizations.

Three functional subsystems:

1. **Specification & Pricing Engine** — Items carry configurable specs
   (material, lamination, print sides, corners, bundle size). Specs drive
   pricing through a JSON pricing matrix (Bundle Based / Area Based modes).
2. **Job Sheet / Production Routing** — Sales Order submission auto-generates
   Job Sheets with route steps (one per BOM operation). Job Sessions track work
   units through a claim → start → end lifecycle (split / merge / forward).
3. **Dashboard API** — Whitelisted endpoints consumed by an **Angular
   dashboard**, which is the primary UI for production-floor workers. ERPNext
   Desk is used by admins for setup only.

## Current state

The app is **early-stage**. Only the **Specifications** module is built so far
(`specification_type`, `specification_value`, `item_specification`,
`quotation_item_specification` doctypes + the Item/Quotation Item custom
fields). The `api/`, `pricing/`, `production/`, and `overrides/` modules
described in the findings doc are **planned, not yet implemented**.

### Deferred: Desk-side Quotation Item spec editing

Editing per-line specs on a Quotation *in ERPNext Desk* does not work and is
**deferred** — the data model is fine, only Desk editing is blocked.

`custom_item_specifications` is a `Table` field on **Quotation Item** (a child
doctype), so its grid renders *inside* the Quotation Item row-form. Frappe's
single global `cur_grid` + freeze overlay can't handle a row-form nested in a
row-form, so the row editor silently no-ops. This is a framework limitation,
not an app bug: **no** standard doctype (0 of 341 in Frappe + ERPNext) puts a
`Table` field on a child doctype. The same field works on **Item** only because
Item is a top-level doctype.

Deferring is safe because Quotations are created primarily in the **Angular
app**, which writes this child table via the API and never touches the Desk
grid (the findings doc rates the Desk spec widget low priority). Do **not**
retry patching the grid (a `grid_fix.js` / `editable_grid` attempt was removed).
If Desk editing is ever truly needed: build a custom injected-HTML widget in
`quotation.js`, or reshape to a flat top-level table on the Quotation parent.

## Repository layout

```
tdn_print_manager/                 (git root — only THIS dir is committed)
├── CLAUDE.md                      this file
├── README.md, license.txt, pyproject.toml
├── claude-docs/                   INSTALL.md, SETUP.md, findings doc
└── tdn_print_manager/             the Python package
    ├── hooks.py                   Frappe app hooks
    ├── modules.txt                registered modules
    ├── setup/install.py           custom-field setup (run via after_migrate)
    ├── specifications/doctype/    the only built module so far
    └── public/                    static assets (css/js) — empty so far
```

The surrounding `frappe-bench/` (bench infra, site data, venv) is **not** in
git — each developer recreates it with `bench init`. See `claude-docs/`.

## Environment & stack

| Component | Version |
|---|---|
| Python | 3.14.x (Frappe v16 pins `>=3.14,<3.15`) |
| Node | 24.x |
| MariaDB | 10.11.x |
| Redis | 7.x |
| wkhtmltopdf | 0.12.6.1 **patched-Qt** (apt version is broken) |
| Frappe / ERPNext | v16 (branch `version-16`) |
| bench | 5.29+ |

- Bench dir: `~/work/now/tdn-print-manager/frappe-bench/`
- Site: `tdn.localhost` → http://tdn.localhost:8000
- Dev login: `Administrator` / `admin`  (MariaDB root: `frappe-dev-root`)

## Common commands

Run all of these from inside `frappe-bench/`. Use `nvm use 24` first if Node
isn't defaulting to 24.

```bash
bench start                                   # run web/redis/scheduler/worker/esbuild (foreground)
bench --site tdn.localhost migrate            # apply schema changes (runs after_migrate hook)
bench --site tdn.localhost console            # interactive Python shell with frappe loaded
bench --site tdn.localhost run-tests --app tdn_print_manager
bench build --app tdn_print_manager           # rebuild JS/CSS bundles
bench --site tdn.localhost clear-cache
```

After editing `setup/install.py` custom fields, run `bench migrate` to apply
them (`after_migrate = "tdn_print_manager.setup.install.setup_custom_fields"`).

## Conventions

- **Code style** is enforced by `pre-commit` (ruff, eslint, prettier,
  pyupgrade). Install once: `cd apps/tdn_print_manager && pre-commit install`.
- **Python:** ruff, line length 110, **tabs** for indentation, double quotes,
  target `py314`. (See `pyproject.toml`.)
- **Custom fields** on stock ERPNext doctypes are created in
  `setup/install.py` and applied via the `after_migrate` hook — not committed
  as fixtures (yet). Prefix new fields with `custom_`.
- **Module structure** mirrors Frappe: each doctype lives in
  `<module>/doctype/<snake_case_name>/` with `.json` + `.py` + `__init__.py`.
  New modules must be registered in `modules.txt`.
- **Native vs custom fields:** fields on the app's own custom doctypes should
  be native doctype fields; only fields added to *stock* ERPNext doctypes go
  through `create_custom_fields`.

## Porting principles (from the legacy tenant)

When porting legacy "Jerrys" scripts, the findings doc is the source of truth.
Key rules:

- **Strip tenant naming** — all "Jerrys"-prefixed names become generic.
- **No hardcoded tenant values** — e.g. the legacy warehouse `'Stores - JP'`
  must become a dynamic lookup.
- **Replace `App Role Permission`** custom doctype with stock Frappe Roles.
- **Server Scripts → app code:** API endpoints go to `tdn_print_manager/api/`,
  DocType events go to `overrides/` registered via `doc_events` in `hooks.py`.
- **Client Scripts → `public/js/`**, loaded via hooks; merge duplicate scripts
  and drop dangerous global monkey-patches (see findings doc DROP list).
- **Business-critical logic** (pricing engine, `end_session` state machine)
  must be extracted into testable Python modules **with unit tests**.

## Docs

- `claude-docs/INSTALL.md` — from-scratch install on a fresh Ubuntu machine.
- `claude-docs/SETUP.md` — stack versions, app metadata, directory layout.
- `claude-docs/tdn_print_manager_findings.md` — complete inventory of legacy
  customizations and the KEEP / REDESIGN / DROP / INVESTIGATE triage. **Read
  this before porting anything.**
