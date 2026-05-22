# tdn_print_manager — Customisation Inventory & Analysis

**Generated:** 2026-05-22
**Source:** Jerrys ERPNext tenant site (jerrys.erp.3dn.store), Frappe v15 + ERPNext v15
**Purpose:** Complete inventory and analysis of existing Server Scripts, Client Scripts, Custom DocTypes, Custom Fields, Property Setters, and other customisations. This document is the foundation for building the `tdn_print_manager` Frappe app.

---

## 1. Inventory Summary

| Type | Count | Notes |
|------|-------|-------|
| Server Scripts | 17 | 12 API endpoints, 5 DocType Event hooks |
| Client Scripts | 8 | Quotation (4), Item (2), Job Sheet (1), Sales Order (1) |
| Custom DocTypes | 21 | 8 standalone, 13 child tables |
| Custom Fields | 68 | On 22 different doctypes |
| Property Setters | 107 | On 28 different doctypes |
| Notifications | 2 | Material Request receipt + Fiscal Year (stock) |
| Workflows | 0 | |
| Custom Roles | 0 | |
| Custom Print Formats | 1 | IRS 1099 Form (unrelated to 3DN) |

---

## 2. System Overview

This is a **Print Shop MES (Manufacturing Execution System)** with three functional subsystems:

1. **Specification & Pricing Engine** — Items have configurable specs (material, lamination, print sides, corners, bundle size). Specs drive pricing via a JSON-based pricing matrix. Supports "Bundle Based" and "Area Based" pricing modes, with single/double side variants and tier-based pricing.

2. **Job Sheet / Production Routing** — Sales Order submission auto-generates Job Sheets with route steps (one per BOM operation). Job Sessions track individual work units through a claim→start→end lifecycle. Sessions can be split (partial completion spawns remainder), merged (forwarded qty combines with existing queued sessions at next step), and track time/qty.

3. **Dashboard API** — 8 API endpoints consumed by the Angular dashboard (the primary UI for production floor workers). Covers session management, department dashboards, available job listing, and order status rollup.

**Key context:** "Jerrys" is one tenant (a print shop customer). All "Jerrys" prefixed scripts contain platform logic that should work for any tenant — only the naming is tenant-specific. The Angular dashboard is the primary UI for production workers; ERPNext Desk is used by admins for setup (item specs, pricing, employee management).

---

## 3. Custom DocTypes

### Standalone DocTypes (8)

| Name | Module | Autoname | Purpose |
|------|--------|----------|---------|
| Job Sheet | Custom | JS-.YYYY.-.##### | Production job tracker per SO item. Has route_steps (child), tracks current step, department, status. |
| Job Session | Custom | JSESS-{YYYY}-{######} | Individual work session. Lifecycle: Queued→Claimed→In Progress→Completed. Tracks worker, workstation, qty, duration. |
| Job Sheet Session | Custom | JSS-.YYYY.-.##### | Purpose unclear — may be a linking table between Job Sheet and Job Session, or superseded by Job Session itself. **INVESTIGATE.** |
| Branch Workstation Map | Custom | {default_workstation}-{branch} | Maps a default workstation to its branch-specific equivalent. Used by generate_job_sheet to resolve workstations per branch. |
| Item Spec Pricing | Custom | field:pricing_key | Standalone pricing records keyed by a pricing_key. Relationship to the pricing matrix JSON is unclear. **INVESTIGATE.** |
| Specification Value | Custom | field:value | A possible value for a specification (e.g. "230 GSM Artboard", "Mat", "Round"). Named by its value. |
| Specification Type | Custom | field:type_name | A category of specification (e.g. "Material", "Lamination", "Corners", "Print Sides", "Bundle Size"). |
| App Role Permission | Custom | field:role | Custom permission flags per role (can_create_quotation, can_place_order, etc.). **REPLACE with stock Frappe Roles.** |

### Child Table DocTypes (13)

| Name | Module | Parent DocType(s) | Purpose |
|------|--------|--------------------|---------|
| Job Sheet Route Step | Custom | Job Sheet | One step in the production route. Fields: step_index, operation, department, workstation, status, qty tracking (total, completed_here, forwarded). |
| Job Sheet Note | Custom | Job Sheet | Notes attached to a Job Sheet. |
| Item Specification | Custom | Item, Quotation Item | Links a Specification Type to a Specification Value on an Item or Quotation Item. |
| Item BOM Operation | Custom | Item | Spec-value-keyed BOM operation. Fields: operation, default_workstation, specification_value, sequence, time_in_mins. |
| Item BOM Material | Custom | Item | Spec-value-keyed BOM material. Fields: raw_material_item, specification_value, calc_method, qty_per_unit, uom, wastage_pct. |
| Item Bundle Tier | Custom | Item | Legacy bundle pricing tiers. Fields: bundle_qty, single_side_rate, double_side_rate. |
| Quotation Item Specification | Custom | Quotation Item | Selected spec values for a quotation line item. |
| Operation Branch Department | Custom | Operation | Maps an Operation to a Department per Branch. Fields: branch, department, is_default. |
| Workstation Supported Operation | Custom | Workstation | Lists which Operations a Workstation can perform. |
| Employee Department Assignment | Custom | Employee | Allows an employee to be assigned to multiple departments (for job queue scoping). |
| Print BOM Material | Manufacturing | Unknown | **INVESTIGATE** — module is Manufacturing, not Custom. May be an older version of Item BOM Material. |
| Spec Value Operation | Manufacturing | Unknown | **INVESTIGATE** — module is Manufacturing. |
| Item Group Base Operation | Manufacturing | Item Group | Base operations inherited by items in the group. |

---

## 4. Server Scripts — Detailed Analysis

### API Endpoints (12)

#### get_my_session_info
- **Path:** `/api/method/get_my_session_info`
- **Purpose:** Returns current user's branch, designation, roles, and permission flags for the Angular dashboard.
- **Reads from:** Employee (branch, designation), Has Role, App Role Permission (custom permission doctype).
- **Triage:** KEEP but REDESIGN. Replace App Role Permission reads with stock Frappe role checks.
- **New path:** `tdn_print_manager.api.auth.get_session_info`

#### jerrys_list_available
- **Path:** `/api/method/jerrys_list_available`
- **Purpose:** Lists Queued Job Sessions visible to the current user, filtered by branch/department permissions.
- **Reads from:** Job Session, Job Sheet, Has Role, User (home_branch — **field may not exist, check**), User Permission.
- **Note:** Reads `home_branch` from User doctype. This field is NOT in the custom_fields dump. Either it's set elsewhere or this read silently returns None.
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.dashboard.list_available`

#### jerrys_dept_dashboard
- **Path:** `/api/method/jerrys_dept_dashboard`
- **Purpose:** Three-panel department dashboard: (1) Claimable sessions, (2) In-progress Job Sheets at this department, (3) Coming-next Job Sheets whose route includes this department downstream.
- **Reads from:** Job Session, Job Sheet, Job Sheet Route Step (raw SQL for "coming next").
- **Note:** The "coming next" query uses raw SQL joining tabJob Sheet Route Step with tabJob Sheet. Bypasses Frappe permissions (fine for single-tenant, note for multi-tenant).
- **Triage:** KEEP, port to app. Most complex read-only API.
- **New path:** `tdn_print_manager.api.dashboard.dept_dashboard`

#### jerrys_start_session
- **Path:** `/api/method/jerrys_start_session`
- **Purpose:** Transition a Claimed session to In Progress. Validates workstation (department match, supported operations, not in use). Updates Job Sheet status and route step to Active.
- **Reads/writes:** Job Session, Job Sheet, Workstation, Workstation Supported Operation.
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.session.start_session`

#### jerrys_workstations_for_session
- **Path:** `/api/method/jerrys_workstations_for_session`
- **Purpose:** Lists workstations available for a session (filtered by department, operation support, not currently in use).
- **Reads from:** Job Session, Workstation, Workstation Supported Operation, Job Session (to check busy).
- **Uses raw SQL** for the workstation query.
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.session.workstations_for_session`

#### jerrys_end_session
- **Path:** `/api/method/jerrys_end_session`
- **Purpose:** End a session with outcome: Pause, Release, or Cancel. Handles qty tracking, remainder spawning, forward-to-next-step with merge logic, step completion detection, Job Sheet status advancement, and auto Stock Entry creation on final step completion.
- **Reads/writes:** Job Session, Job Sheet, Job Sheet Route Step, Stock Entry, BOM Item, Sales Order.
- **Concurrency:** Uses `SELECT FOR UPDATE` on Job Session row.
- **ISSUES:**
  - Stock Entry warehouse is hardcoded to `'Stores - JP'` (Jerry's specific). Must be dynamic.
  - ~150 lines of complex state machine logic. Hardest to test/debug as a Server Script.
  - Auto-submits Stock Entry with `ignore_permissions=True`.
- **Triage:** KEEP but REDESIGN. This is the highest-priority script to port properly — needs unit tests.
- **New path:** `tdn_print_manager.api.session.end_session`

#### jerrys_claim_session
- **Path:** `/api/method/jerrys_claim_session`
- **Purpose:** Claim a Queued session. Checks branch/department permissions, assigns worker.
- **Concurrency:** Uses `SELECT FOR UPDATE`.
- **Reads from:** Job Session, Has Role, User/Employee (branch), User Permission (department).
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.session.claim_session`

#### jerrys_order_status
- **Path:** `/api/method/jerrys_order_status`
- **Purpose:** Per-order rollup for Production Admins. Shows each SO item's Job Sheet status, route steps, completion percentages.
- **Permission:** Restricted to Production Admin / System Manager roles.
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.dashboard.order_status`

#### generate_job_sheet
- **Path:** `/api/method/generate_job_sheet`
- **Purpose:** Creates BOM + Work Order + Job Cards for each SO item. Uses spec-driven materials and operations from Item's custom tables. Resolves workstations per branch via Branch Workstation Map. Handles legacy fallback for materials (Item BOM Material → Item Group base materials → Specification Value BOM materials).
- **ISSUE:** Dual-path conflict with `Jerrys SO Submit`. SO Submit auto-creates Job Sheets on submit. generate_job_sheet creates BOMs + Work Orders (but not Job Sheets). User confirmed SO Submit is the primary path. generate_job_sheet may be a manual "create BOM/WO" button used in parallel.
- **Note:** Contains a detailed comment referencing "Phase 3/Phase 4" of the build, with a backup reference.
- **Triage:** KEEP but REDESIGN. Clarify relationship with SO Submit hook. Consider merging into one path.
- **New path:** `tdn_print_manager.api.job_sheet.generate`

#### get_item_spec_values
- **Path:** `/api/method/get_item_spec_values`
- **Purpose:** Returns Specification Values for a given Item + Specification Type, filtered by text search. Used by the Quotation Item spec widget's dropdown link queries.
- **Uses raw SQL** joining Item Specification with Specification Value.
- **Triage:** KEEP, port to app.
- **New path:** `tdn_print_manager.api.auth.get_item_spec_values`

#### _inject_item_bom
- **Path:** `/api/method/_inject_item_bom`
- **Purpose:** TEST SCRIPT. Hardcodes BOM materials and operations for "Stantard Visiting Card" (typo) with Jerry's-specific workstation names.
- **Triage:** DROP. Test/seed data script in production.

#### _test_inject_quotation_specs
- **Path:** `/api/method/_test_inject_quotation_specs`
- **Purpose:** TEST SCRIPT. Injects hardcoded spec values into a specific Quotation Item by name.
- **Triage:** DROP. Test script in production.

### DocType Event Hooks (5)

#### Jerrys SO Submit (Sales Order → After Submit)
- **Purpose:** Auto-generates Job Sheets on SO submission. For each SO item: looks up BOM, reads operations, resolves departments via Operation Branch Department mapping, creates Job Sheet with route_steps, seeds first Queued Job Session.
- **Guarded by:** `jobs_generated` check field on Sales Order.
- **ISSUE:** Relationship with `generate_job_sheet` API is unclear. Both create production artifacts. User confirmed auto-generation is the primary path.
- **Triage:** KEEP, port to `doc_events` hook.
- **New location:** `tdn_print_manager.overrides.sales_order.on_submit`

#### calculate_quotation_item_pricing (Quotation → Before Save)
- **Purpose:** Server-side pricing calculation. For each Quotation Item with specs: loads Item's pricing matrix, determines pricing mode (Bundle/Area), resolves tier, calculates per-piece rate from selected spec values, handles min_charge, supports v1 and v2 matrix formats plus legacy Bundle Tier fallback.
- **Complexity:** ~150 lines with multiple pricing paths (v2 bundle, v2 area, v1 bundle, v1 area, legacy bundle tiers).
- **Triage:** KEEP but REDESIGN. Extract into a proper Python module (`tdn_print_manager.pricing.pricing_engine`) with unit tests. The pricing logic is the most business-critical code in the system.
- **New location:** `tdn_print_manager.overrides.quotation.before_save` (calls into pricing_engine module)

#### Jerrys Item Spec Cascade Clean (Item → Before Save)
- **Purpose:** Two functions: (1) When spec values are removed from an Item, cascade-deletes related BOM Material and BOM Operation rows. (2) Always refreshes the pricing matrix JSON — cleans orphan rows, adds empty rows for new specs, recomputes base_specs as the cheapest value per spec type.
- **Triage:** KEEP, port to `doc_events` hook.
- **New location:** `tdn_print_manager.overrides.item.before_save`

#### Job Sheet Fetch Customer Info (Job Sheet → Before Save)
- **Purpose:** Denormalizes customer_name and customer_phone from Sales Order → Job Sheet.
- **Note:** Stale data risk if customer info changes after Job Sheet creation. Acceptable for a print shop workflow.
- **Triage:** KEEP, simple hook.
- **New location:** `tdn_print_manager.overrides.job_sheet.before_save` (or in the Job Sheet doctype controller)

#### propagate_job_card_routing (Job Card → Before Insert)
- **Purpose:** Copies branch and department from Workstation (and falls back to Work Order's branch) onto newly created Job Cards.
- **Date comment:** "Applied 2026-04-19. Phase 3/4 of the Print MIS build."
- **Triage:** KEEP, port to `doc_events` hook.
- **New location:** `tdn_print_manager.overrides.job_card.before_insert`

---

## 5. Client Scripts — Detailed Analysis

### Item Form (2 scripts)

#### Jerrys Filter Spec Value Dropdown
- **DocType:** Item, Form view
- **Purpose:** Filters the `specification_value` Link field dropdown in BOM Material and BOM Operation child tables to only show values that exist in the Item's Specification table.
- **Triage:** KEEP, port to `public/js/item.js`

#### Pricing Matrix Editor
- **DocType:** Item, Form view
- **Purpose:** Renders an editable pricing table inside the `custom_pricing_matrix` Long Text field. Supports v1/v2, Bundle Based/Area Based modes. Handles sync on spec changes, orphan cleanup, duplicate detection.
- **Size:** ~350 lines. Uses IIFE pattern, stores functions on `window._pme` to survive minification.
- **Triage:** KEEP, port to `public/js/item.js`. Low priority (admin-only UI).

### Quotation Form (4 scripts)

#### Quotation - Item Specification Filter
- **DocType:** Quotation, Form view
- **Purpose:** THE BIG ONE (~400 lines). Injects a custom spec-selection widget into each Quotation Item's form. Dropdowns for each spec type, dimension inputs for Area Based pricing, live price calculation, pre-selects saved values, defaults to base_specs for new items.
- **ISSUES:**
  - Monkey-patches grid row show_form, frappe.model.set_value
  - setTimeout chains for DOM readiness
  - Builds HTML strings manually
  - Fights with other Quotation Client Scripts for grid control
- **Note:** Since quotations are primarily created in the Angular app, this widget is only used when admins open a Quotation in Desk. LOW PRIORITY for day-one launch.
- **Triage:** KEEP but REDESIGN. Port to `public/js/quotation.js`. Simplify where possible.

#### Quotation - Bundle Size Fix
- **DocType:** Quotation, Form view
- **Purpose:** Globally monkey-patches `frappe.model.set_value` to prevent the grid row editor from closing when Bundle Size selection triggers a qty change.
- **ISSUE:** Global side-effect. Patches a core Frappe function for all doctypes, not just Quotation.
- **Triage:** DROP. Solve the root cause in the redesigned spec widget instead.

#### Quotation - Items Edit Button Only
- **DocType:** Quotation, Form view
- **Purpose:** Prevents Quotation Item grid rows from auto-expanding on click. Users must click the pencil/edit icon specifically. Patches grid row toggle_view.
- **Note:** User confirmed this is intentional — they want pencil-only expansion because accidental row expansion interferes with the spec widget.
- **Triage:** KEEP, port to `public/js/quotation.js`. Merge with other Quotation scripts into one file.

#### Quotation-Disable-Auto-Edit-Dialog
- **DocType:** Quotation, Form view
- **Purpose:** Prevents the edit dialog from auto-opening when adding a new Quotation Item row. Overrides `grid.add_new_row` with `show_form=false`.
- **ISSUE:** Duplicates functionality with "Items Edit Button Only". Both override `add_new_row`.
- **Triage:** MERGE with "Items Edit Button Only" into one clean implementation in `public/js/quotation.js`.

### Job Sheet Form (1 script)

#### Jerrys Job Sheet Execution Log
- **DocType:** Job Sheet, Form view
- **Purpose:** On Job Sheet form refresh, fetches all Job Sessions for this Job Sheet and renders an HTML table in the `execution_log_html` field. Shows step, operation, department, worker, status, outcome, qty, timing.
- **Triage:** KEEP, port to `public/js/job_sheet.js`

### Sales Order Form (1 script)

#### Sales Order - Generate Job Sheet
- **DocType:** Sales Order, Form view
- **Purpose:** Adds a "Generate Job Sheet" button under "Create" menu on submitted Sales Orders. Calls `generate_job_sheet` API with confirmation dialog.
- **ISSUE:** Relationship with auto-generation on SO Submit needs clarification.
- **Triage:** KEEP, port to `public/js/sales_order.js`

---

## 6. Custom Fields — Detailed Analysis

### Fields on Stock ERPNext DocTypes (3DN business logic — FIXTURE in app)

**Item (10 fields):**
- `custom_product_id` (Data) — Product ID
- `custom_bom_spec_operations` (Table → Item BOM Operation) — Spec-keyed BOM operations
- `custom_bom_spec_materials` (Table → Item BOM Material) — Spec-keyed BOM materials
- `custom_bundle_tiers` (Table → Item Bundle Tier) — Legacy bundle pricing tiers
- `custom_pricing_matrix` (Long Text) — JSON pricing matrix blob
- `custom_base_price` (Currency) — Base price
- `custom_pricing_engine` (Select) — "Bundle Based" or "Area Based"
- `custom_bom_materials` (Table) — Legacy BOM materials (pre-spec-keyed)
- `custom_item_specifications` (Table → Item Specification) — Spec type/value pairs
- `custom_specifications` (Tab Break) — UI tab for the specs section

**Work Order (7 fields):**
- `custom_total_area_sqft` (Float), `custom_piece_height_ft` (Float), `custom_piece_width_ft` (Float) — Area dimensions
- `custom_corner` (Data), `custom_bundle_size` (Int), `custom_print_sides` (Data) — Print job specs
- `custom_branch` (Link → Branch)

**Quotation Item (6 fields):**
- `custom_total_area_sqft` (Float), `custom_piece_height_ft` (Float), `custom_piece_width_ft` (Float) — Area dimensions
- `custom_item_specifications` (Table → Quotation Item Specification)
- `custom_item_specifications_section` (Section Break)
- `custom_orientation` (Link → Specification Value) — **INVESTIGATE: is this used?**

**Job Card (5 fields):**
- `custom_department` (Link → Department), `custom_branch` (Link → Branch)
- `custom_corner` (Data), `custom_bundle_size` (Int), `custom_print_sides` (Data)

**Quotation (4 fields):**
- `custom_tagged_user` (Data) — **REDESIGN: should be Link to User or Employee**
- `custom_item_specifications_section` (Section Break), `custom_item_specifications` (Table → Quotation Item Specification)
- `custom_branch` (Link → Branch)

**Branch (4 fields):**
- `custom_branch_name` (Data, required), `custom_company` (Link → Company)
- `custom_default_warehouse` (Link → Warehouse), `custom_cost_center` (Link → Cost Center)

**Workstation (4 fields):**
- `supported_operations` (Table → Workstation Supported Operation)
- `department` (Link → Department) — **DUPLICATE: both `department` and `custom_department` exist**
- `custom_department` (Link → Department) — **DUPLICATE**
- `custom_branch` (Link → Branch)

**Sales Order (2 fields):**
- `jobs_generated` (Check, read-only) — **NOTE: not prefixed with custom_. Standardize to `custom_jobs_generated`.**
- `custom_branch` (Link → Branch)

**Sales Order Item (3 fields):**
- `custom_total_area_sqft` (Float), `custom_piece_height_ft` (Float), `custom_piece_width_ft` (Float)

**BOM Operation (2 fields):**
- `department` (Link → Department), `branch` (Link → Branch, label "Branch (override)")

**Item Group (2 fields):**
- `custom_base_materials` (Table), `custom_base_operations` (Table → Item Group Base Operation)

**Operation (1 field):**
- `branch_department_map` (Table → Operation Branch Department)

**Employee (1 field):**
- `custom_dept_assignments` (Table → Employee Department Assignment)

**Department (1 field):**
- `custom_branch` (Link → Branch)

**Job Sheet (1 field):**
- `execution_log_html` (HTML, read-only) — Rendered by Client Script

### Fields on Custom DocTypes (should be NATIVE fields in the app, not Custom Fields)

**Job Session (4 fields):** workstation (Link), is_full_session (Check), parent_session (Link), qty_max (Float)
**Job Sheet Route Step (3 fields):** qty_forwarded (Float), qty_completed_here (Float), qty_total (Float)

These are currently Custom Fields because the doctypes were created through the UI first, then fields were added later. In the app, they become native doctype fields.

### Fields that are NOT 3DN logic (DO NOT fixture)

**Print Settings (3):** print_taxes_with_zero_amount, print_uom_after_quantity, compact_item_print — Generic ERPNext print settings
**Address (2):** is_your_company_address, tax_category — Likely stock ERPNext or India localization
**Contact (1):** is_billing_contact — Stock ERPNext
**Communication (1):** company — Stock ERPNext
**Email Account (1):** company — Stock ERPNext

---

## 7. Property Setters (107 total)

Grouped by doctype (top 10 by count):
- Sales Invoice: 12 setters
- Delivery Note: 10
- Sales Order: 10
- Quotation: 9
- Purchase Receipt: 9
- Purchase Order: 8
- Purchase Invoice: 8
- Supplier Quotation: 7
- Item: 6
- Sales Invoice Item: 4

Most are cosmetic/workflow tweaks: making fields mandatory/hidden/read-only, changing labels, setting defaults. These should be reviewed individually before fixturing — many may be Jerrys-specific preferences rather than platform requirements. Lower priority than scripts and doctypes.

---

## 8. Notifications

1. **Material Request Receipt Notification** — Fires on Value Change when status is Received/Partially Received. Sends item receipt summary. **ASK USERS if they use this.**
2. **Notification for new fiscal year** — Stock ERPNext notification. **DROP from app scope.**

---

## 9. Other

- **Custom Print Format: IRS 1099 Form** — US tax form, completely unrelated to 3DN/print shop. **DROP.**
- **Custom Roles: 0** — None created.
- **Workflows: 0** — None created.

---

## 10. Triage Summary

### KEEP (port as-is or with minor changes)
- `jerrys_list_available` → `tdn_print_manager.api.dashboard.list_available`
- `jerrys_dept_dashboard` → `tdn_print_manager.api.dashboard.dept_dashboard`
- `jerrys_start_session` → `tdn_print_manager.api.session.start_session`
- `jerrys_workstations_for_session` → `tdn_print_manager.api.session.workstations_for_session`
- `jerrys_claim_session` → `tdn_print_manager.api.session.claim_session`
- `jerrys_order_status` → `tdn_print_manager.api.dashboard.order_status`
- `get_item_spec_values` → `tdn_print_manager.api.auth.get_item_spec_values`
- `Job Sheet Fetch Customer Info` → `tdn_print_manager.overrides.job_sheet.before_save`
- `propagate_job_card_routing` → `tdn_print_manager.overrides.job_card.before_insert`
- `Jerrys Item Spec Cascade Clean` → `tdn_print_manager.overrides.item.before_save`
- Client Script: `Jerrys Job Sheet Execution Log` → `public/js/job_sheet.js`
- Client Script: `Sales Order - Generate Job Sheet` → `public/js/sales_order.js`
- Client Script: `Jerrys Filter Spec Value Dropdown` → `public/js/item.js`

### KEEP but REDESIGN
- `jerrys_end_session` — Needs unit tests, dynamic warehouse lookup (hardcoded 'Stores - JP')
- `calculate_quotation_item_pricing` — Extract to pricing_engine module with tests
- `generate_job_sheet` — Clarify relationship with SO Submit, possibly merge paths
- `Jerrys SO Submit` — Port to doc_events hook
- `get_my_session_info` — Replace App Role Permission with stock Frappe roles
- Client Script: `Quotation - Item Specification Filter` — Simplify, merge with other Quotation scripts
- Client Script: `Pricing Matrix Editor` — Port as-is but move to proper app JS
- `custom_tagged_user` — Change from Data to Link field
- Workstation `department` / `custom_department` — Consolidate to one field
- `jobs_generated` on Sales Order — Rename to `custom_jobs_generated`

### DROP
- `_inject_item_bom` — Test/seed data script
- `_test_inject_quotation_specs` — Test/seed data script
- `Quotation - Bundle Size Fix` — Dangerous global monkey-patch
- `Quotation-Disable-Auto-Edit-Dialog` — Duplicate of Items Edit Button Only
- IRS 1099 Form print format
- Notification for new fiscal year
- App Role Permission custom doctype (replaced by stock roles)
- Custom Fields on Print Settings, Communication, Email Account, Address, Contact

### INVESTIGATE (need user answers)
- Material Request Receipt Notification — is it used?
- `custom_orientation` on Quotation Item — is it used?
- Job Sheet Session doctype — what is its purpose vs Job Session?
- Print BOM Material, Spec Value Operation — are these used or superseded?
- Item Spec Pricing — relationship to pricing matrix?
- The `home_branch` field read from User doctype — does this field exist?
- Many of the 107 Property Setters — which are platform vs Jerrys-specific?

---

## 11. App Architecture

**App name:** `tdn_print_manager`
**Target:** ERPNext v16

### Module Structure
```
tdn_print_manager/
├── print_shop/        # Core data model: specs, workstations, routing
├── pricing/           # Pricing engine, quotation-level specs
├── production/        # Job Sheets, Sessions, runtime workflow
├── api/               # Whitelisted API methods (dashboard consumes these)
│   ├── auth.py        # get_session_info, get_item_spec_values
│   ├── session.py     # claim, start, end, workstations_for_session
│   ├── dashboard.py   # dept_dashboard, list_available, order_status
│   └── job_sheet.py   # generate
├── overrides/         # doc_events hooks on stock ERPNext doctypes
│   ├── sales_order.py
│   ├── quotation.py
│   ├── item.py
│   └── job_card.py
├── public/js/         # Desk-side Client Scripts
│   ├── quotation.js
│   ├── item.js
│   ├── sales_order.js
│   └── job_sheet.js
└── fixtures/          # Custom Fields, Property Setters
```

### Key Design Decisions
1. Angular dashboard is primary UI for production workers. Desk is admin/setup only.
2. Job Sheets auto-generate on SO submit (confirmed by user).
3. Quotations primarily created in Angular app, not Desk. Desk-side spec widget is low priority.
4. App Role Permission doctype replaced by stock Frappe Roles.
5. All "Jerrys" naming becomes generic.
6. Hardcoded values (warehouse 'Stores - JP') become dynamic lookups.

### API Path Migration
| Old | New |
|-----|-----|
| `get_my_session_info` | `tdn_print_manager.api.auth.get_session_info` |
| `jerrys_list_available` | `tdn_print_manager.api.dashboard.list_available` |
| `jerrys_dept_dashboard` | `tdn_print_manager.api.dashboard.dept_dashboard` |
| `jerrys_start_session` | `tdn_print_manager.api.session.start_session` |
| `jerrys_workstations_for_session` | `tdn_print_manager.api.session.workstations_for_session` |
| `jerrys_end_session` | `tdn_print_manager.api.session.end_session` |
| `jerrys_claim_session` | `tdn_print_manager.api.session.claim_session` |
| `jerrys_order_status` | `tdn_print_manager.api.dashboard.order_status` |
| `generate_job_sheet` | `tdn_print_manager.api.job_sheet.generate` |
| `get_item_spec_values` | `tdn_print_manager.api.auth.get_item_spec_values` |
