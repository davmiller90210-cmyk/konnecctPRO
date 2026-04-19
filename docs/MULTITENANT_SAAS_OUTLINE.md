# Multi-tenant SaaS outline (Konnecct / Frappe CRM fork)

This document **outlines** how to evolve from **one shared CRM per site** to **many isolated “workspaces” (tenants)** for unrelated customers. It is a **product and engineering roadmap**, not an implemented design.

For how the stack behaves **today**, see [MULTITENANCY_NOTES.md](../MULTITENANCY_NOTES.md).

---

## 1. Goal and non-goals

**Goal**

- Unrelated **organizations** (tenants) use the **same hostname** (or a single product domain), each seeing **only their own** CRM data (leads, deals, contacts, tasks, settings scoped to tenant).
- **Users** belong to one or more tenants; **roles** may differ per tenant if you need it later.

**Non-goals (initial phases)**

- Full **Frappe Cloud–style** billing, usage metering, and self-serve plan changes (can be layered later).
- Replacing Frappe’s **site** model entirely; the site remains one **MariaDB database** unless you choose the **multi-site** alternative below.

---

## 2. Two architecture families (pick one as primary)

### A) Multi-site (Frappe-native, strongest isolation)

- **One Frappe site per tenant** (subdomain or custom domain → `bench` site + DB).
- **Pros:** Frappe permissions, backups, and upgrades stay standard; no row-level filter bugs across the whole schema.
- **Cons:** Operational cost (N sites), routing/SSL automation, cross-tenant reporting only via external warehouse.

**When to choose A:** You control hosting and can automate `bench new-site`, DNS, and TLS.

### B) Single-site row-level tenancy (application-enforced)

- **One database**, add **`tenant_id`** (or `workspace_id`) to tenant-owned tables and enforce it **everywhere** data is read or written.
- **Pros:** One backup, one migrate, simpler hosting bill at small scale.
- **Cons:** High engineering risk: **every** API, report, background job, notification, and integration must respect tenant or you leak data.

**When to choose B:** You must keep **one URL / one site** and accept the cost of a long, audit-heavy build.

The rest of this outline assumes **B** unless noted; many sections also apply if you later **split hot tenants** into **A** for large accounts.

---

## 3. Core data model (single-site tenancy)

### 3.1 Tenant (workspace) DocType

- New DocType, e.g. **`Konnecct Workspace`** (or `CRM Tenant`):
  - `name` (or explicit `slug`), `title`, `owner_user`, `status` (trial/active/suspended), `plan`, timestamps.
  - Optional: branding, domain allowlist, feature flags.

### 3.2 Membership

- **`Konnecct Workspace Member`** (or use **User** custom fields + child table):
  - Links `workspace` ↔ `User`, `role` within workspace (admin / member), `invited_by`, `joined_at`.
- **Signup / invite** must create or attach membership **before** the user sees CRM data.

### 3.3 Row ownership

- Add **`workspace`** (Link to tenant) on at minimum:
  - **CRM Lead, CRM Deal, CRM Contact (if applicable), CRM Task, CRM Organization** (as *your* tenant’s orgs, distinct from “customer company” orgs if you keep both concepts), **FCRM Note**, **CRM Call Log**, **CRM View Settings**, and any other doctype that must not leak across tenants.
- **Single-tenant migration:** backfill `workspace` for all existing rows to a **“Default”** workspace so production does not break mid-deploy.

### 3.4 Naming and uniqueness

- Decide whether **globally unique** `name` per lead/deal across all tenants is required for URLs/APIs, or namespaced per workspace (`{workspace}-{serial}`) to avoid collisions.

---

## 4. Session and request context

- On login (and after signup), resolve **current workspace**:
  - **Cookie / session key** `frappe.session.data["konnecct_workspace"]` or dedicated **Workspace Settings** single per user default + switcher.
- **Workspace switcher** in CRM UI: only list workspaces the user belongs to.
- **Server:** central helper `frappe.local.konnecct_workspace` (or similar) set in `before_request` / auth hook from session; **throw** if missing when hitting tenant-scoped APIs.

---

## 5. Permission and query enforcement (critical)

### 5.1 `permission_query_conditions` (list views, reports)

- Register in `hooks.py` for each tenant-owned doctype: SQL fragment `and `tabLead`.workspace = %(workspace)s` with bound param from session.
- **Same for** `get_list`, exports, search, dashboard queries.

### 5.2 `has_permission` (single-doc access)

- Deny read/write if `doc.workspace != session_workspace` (and allow bypass for true system roles only if you introduce a **platform super-admin**).

### 5.3 Whitelisted methods

- Audit **`crm.api.*`** (and `frappe.client.*` usage from frontend): every method that loads or mutates business data must **filter by workspace** or call shared helpers that do.

### 5.4 Background jobs

- **Scheduler** and **RQ jobs** must receive `workspace` in job args; never assume “whole site” is one tenant.
- **Notifications / realtime** publish to tenant-scoped channels only.

### 5.5 Integrations (Twilio, WhatsApp, email, ERPNext)

- Either **one integration stack per workspace** (separate single doctypes become child tables or separate DocTypes keyed by workspace), or **explicit policy** (e.g. integrations platform-wide only for internal use — document clearly).

---

## 6. Signup and onboarding (product flow)

1. **Sign up** → create **User** + **default workspace** (or join via invite token to existing workspace).
2. **First screen:** name the workspace / company; store on tenant DocType.
3. **Invite flow:** generate links scoped to `workspace` (similar to today’s CRM Invitation but with **workspace** FK).
4. **Public signup policy:** disable open signup on the main domain if tenants must be **invite-only**; or allow signup only into **new** isolated workspaces (not joining existing data).

---

## 7. Routing and domains (optional layers)

- **Path-based:** `app.konnecct.com/w/acme/crm` — map `acme` → workspace; requires router + SPA base path changes.
- **Subdomain without new Frappe site:** `acme.konnecct.com` same site, middleware sets workspace from subdomain → same as session resolution.
- **Subdomain + Frappe site (hybrid):** small tenants on **B**, large tenants migrated to **A**.

---

## 8. Frontend (Vue CRM)

- **API client:** send `workspace` (or rely on cookie set by backend) on each request; handle **403** when workspace missing or user removed.
- **Stores:** scope caches (leads, deals lists) by workspace id; clear on switch.
- **Settings:** which screens are **per-workspace** vs **platform** (if any).

---

## 9. Migration and rollout phases (suggested)

| Phase | Scope | Outcome |
|-------|--------|--------|
| **0 – Decision** | Confirm **A vs B**, legal/compliance, and “default workspace” for existing data | Written ADR |
| **1 – Model** | Tenant + membership DocTypes; optional `workspace` column nullable | Ship behind feature flag |
| **2 – Backfill** | One default workspace; assign all existing rows + users | No user-visible change yet |
| **3 – Enforce** | Hooks on read paths; fix failing tests / manual QA matrix | Tenancy enforced |
| **4 – UX** | Signup, switcher, invites, admin suspend | Product matches SaaS story |
| **5 – Hardening** | Security review, pen-test checklist, performance (indexes on `workspace`) | Production-ready |

---

## 10. Testing and audit checklist

- Cross-tenant **read** attempt on every major DocType (must fail).
- **Create** without workspace (must fail or auto-assign per policy).
- **Export**, **print**, **report**, **global search**.
- **Impersonation** / support tools: explicit “act as tenant X” with audit log.
- **Backup/restore** single tenant export (optional later).

---

## 11. Relation to current Konnecct code

- Today: **`check_app_permission`** and CRM roles gate **app access**, not **tenant** rows — see [crm/api/__init__.py](../crm/api/__init__.py).
- **Signup** ([crm/konnecct_signup.py](../crm/konnecct_signup.py)) creates a **global** `Sales User`; multi-tenant signup must create **workspace + membership** and set session context.
- **MULTITENANCY_NOTES.md** remains the source of truth for **current** behavior; this file is the **target** outline only.

---

## 12. Open decisions (record answers before coding)

1. Can one **email** belong to multiple workspaces? (Usually yes.)
2. **CRM Organization** today = customer company — do you add **`workspace`** there too, or rename concepts to avoid confusion?
3. **Desk vs portal:** will tenants use **Desk** at all, or only **`/crm`** SPA?
4. **Data residency** and **delete tenant** (GDPR): export + purge playbook.

When these are answered, the first implementation slice is typically **Phase 1–2** (model + backfill + feature flag), then **Phase 3** with a security review gate.
