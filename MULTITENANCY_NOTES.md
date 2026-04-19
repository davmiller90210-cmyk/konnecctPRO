# Multi-tenancy and SaaS readiness: Konnecct (Frappe CRM fork)

This document explains how isolation works **today** in this stack (Frappe + this app) and what it would mean to run **Konnecct** as a platform where **you** are the global operator and **customers** only control their own workspaces.

## How Frappe thinks about “tenants”

In Frappe / bench, the primary isolation boundary is the **site**:

- One **site** has its own **database** (and typically its own file storage for uploads).
- Users, roles, DocTypes, and business data for that site live in that database.
- Multiple sites can run on one bench server, each with its own hostname or port map.

So **out of the box, Frappe is multi-site, not multi-tenant inside one database**. This app follows that model unless you add extra application logic.

## What this app does today

### Single database per site

All CRM documents (leads, deals, contacts, tasks, etc.) share one MariaDB schema for the site. There is **no** tenant id field enforced globally via `crm/hooks.py` (the template hooks for `permission_query_conditions` / `has_permission` are present only as comments).

### “CRM Organization” is not a SaaS tenant

The DocType **CRM Organization** (`crm/fcrm/doctype/crm_organization/`) models a **sales account** (prospect/customer company): name, industry, territory, logo, etc. The API `get_organizations()` in `crm/api/session.py` lists **all** CRM Organization records for the site (subject to normal Frappe read permissions on that DocType), not “the current customer’s tenant slice.”

Do **not** confuse this with a **workspace** in the SaaS sense (a customer’s isolated Konnecct instance).

For **passwords, signup, and which roles can open integration settings**, see the **“Auth, passwords, and roles (Konnecct)”** section in [README.md](README.md).

For a **roadmap outline** to true multi-tenant SaaS (row-level tenancy vs multi-site), see [docs/MULTITENANT_SAAS_OUTLINE.md](docs/MULTITENANT_SAAS_OUTLINE.md).

### Who can open the CRM app

`crm/api/__init__.py` defines `check_app_permission()`:

- **Administrator** always allowed.
- Otherwise the user must see the **FCRM** module in their allowed modules and have one of **System Manager**, **Sales Manager**, or **Sales User**.

That is **role-based access** for one organization using one CRM on one site—not subscription tiers or tenant admins for many unrelated companies on shared rows.

### Desk workspace JSON

`crm/fcrm/workspace/frappe_crm/frappe_crm.json` defines a **Frappe Desk workspace** (shortcuts and layout for the Desk UI module). It is unrelated to multi-company SaaS isolation.

## Two SaaS shapes you might mean

### A) One Frappe site per customer (aligned with Frappe Cloud–style hosting)

**Model:** Each paying customer gets **their own site** (their own DB). You operate bench, backups, upgrades, and DNS.

**Pros:**

- Strong **data isolation** by construction.
- Fits Frappe’s permission, backup, and migration model.
- “Workspace isolation” is simply **separate sites**.

**Cons:**

- Operational overhead per site (unless automated with a control plane you build or buy).
- Cross-tenant analytics and licensing need a **separate meta layer** (billing DB, usage metrics).

**Platform owner access:** Typically **server / bench Administrator**, break-glass logins, or a small **support app** on each site—not something this repo defines as product behavior.

### B) One site, many customers (true row-level multi-tenancy)

**Model:** A single database serves many unrelated customers; each customer should only see their rows.

**What you would need (high level):**

1. A **tenant key** (e.g. `workspace`, `tenant`, or `team` DocType) on all relevant DocTypes (or a parallel linking model).
2. **Permission query conditions** and/or **has_permission** hooks so List, Report, Search, and REST APIs cannot leak other tenants’ data.
3. Updates to **every** custom query in `crm/api/` and the frontend stores to respect the tenant filter.
4. **Background jobs**, notifications, email ingestion, telephony, and file attachments scoped by tenant.
5. **User membership** model: users belong to one or more tenants; System Manager on one tenant must not imply global access unless intended.

This is a **large, cross-cutting** change. This repository does **not** implement it.

## Frappe “Workspace” vs your “workspace” wording

- **Frappe Workspace:** A Desk UI layout (shortcuts, links).
- **Your product goal (“workspace isolation”):** Likely **either** a separate Frappe site per customer **or** a new tenant entity in the data model. Be explicit in specs to avoid building the wrong thing.

## Practical recommendation for Konnecct

1. **Short term:** Treat **one site = one customer organization** for isolation unless you have a strong reason to share one DB.
2. **Platform operator:** Invest in **automation** (provision site, install `crm` app, set admin, DNS, SSL) and **observability** across sites; keep “god mode” as **hosting-level** access with audit policies.
3. **If you need true multi-tenant on one DB:** Plan a **dedicated project** with threat modeling (IDOR, export, search, reports) and regression tests; do not rely on ad hoc filters in a few API methods.

## Related reading in this repo

- [CODEBASE_AUDIT.md](CODEBASE_AUDIT.md) — structure and request flow.
- [SAFE_VS_RISKY_CHANGES.md](SAFE_VS_RISKY_CHANGES.md) — what to avoid changing while iterating on branding.
