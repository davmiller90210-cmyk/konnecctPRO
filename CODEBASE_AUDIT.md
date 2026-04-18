# Codebase audit: Konnecct (Frappe CRM fork)

This document describes how the repository is structured, how the frontend and backend connect, and which areas matter most when turning the product into **Konnecct**. It reflects the tree as of the audit date; paths are relative to the repository root.

## Executive summary

The project is a **Frappe Framework app** whose Python package and bench app name are **`crm`**. The customer-facing UI is a **Vue 3 + Vite** single-page application under `frontend/`. Built static assets are emitted into `crm/public/frontend/`, and the server entry HTML is `crm/www/crm.html`, both driven by the bench asset settings in `pyproject.toml`. Runtime behavior is **one Frappe site (one database) per deployment** unless you add custom multi-tenant logic elsewhere.

## Top-level layout

| Path | Purpose |
|------|---------|
| `crm/` | Frappe app: DocTypes, hooks, API, www controllers, templates, locale, public assets |
| `frontend/` | Vue SPA: components, router, stores, Vite config |
| `pyproject.toml` | Python package metadata, bench asset pipeline, Ruff, Frappe version constraints |
| `package.json`, `yarn.lock` | Root scripts that delegate to `frontend/` |
| `frappe-ui/` | Git submodule for optional local Frappe UI / Vite plugin override |
| `docker/` | Docker Compose (MariaDB, Redis, bench image) for containerized dev |
| `.devcontainer/` | VS Code / dev container configuration |
| `.github/` | CI workflows, helpers, screenshots, logo used in README |
| `docs/` | Internal developer notes (not end-user product documentation) |
| `scripts/` | Shell helpers (e.g. environment init) |
| `LICENSE` | License text |

## Backend (`crm/`)

- **`crm/hooks.py`** — Central Frappe configuration: `app_name`, `app_title`, desk app tile (`add_to_apps_screen`), website route rules (`/crm/<path:app_path>` → `crm` page), doc events, scheduler, overrides (e.g. Contact, Email Template), `standard_dropdown_items` (includes “Login to Frappe Cloud”, About, etc.).
- **`crm/fcrm/`** — Main CRM module: DocTypes (leads, deals, organizations, settings, invitations, etc.), **Desk workspace** JSON under `crm/fcrm/workspace/`.
- **`crm/lead_syncing/`** — Lead sync / Facebook-related DocTypes and jobs.
- **`crm/api/`** — Whitelisted Python methods consumed by the SPA (`frappeRequest`, `/api/method/...`). Includes session helpers, permissions (`check_app_permission`), invitations, live demo helpers, etc.
- **`crm/www/crm.py`** — Context and boot payload for the `/crm` page; enforces `check_app_permission`; exposes `site_name`, demo/FC flags, translations for boot, telemetry capture.
- **`crm/templates/emails/`** — Email HTML templates (e.g. CRM invitation).
- **`crm/public/`** — Static files served as `/assets/crm/...` (e.g. `crm/public/images/logo.svg`). See `BRANDING_SURFACE_MAP.md` for PWA manifest paths.
- **`crm/locale/`** — GNU gettext translations: `main.pot` source, many `*.po` files, Crowdin config at repo root (`crowdin.yml`).
- **`crm/patches/`**, **`crm/patches.txt`** — Schema/data migrations across versions.
- **`crm/modules.txt`** — Lists app modules (`FCRM`, `Lead Syncing`).

## Frontend (`frontend/`)

- **`frontend/src/main.js`** — App bootstrap: Pinia, Vue Router, Frappe UI, translation plugin, telemetry (`app_name: 'crm'`).
- **`frontend/src/router.js`** — Route table for leads, deals, contacts, settings, mobile views, etc. (history base is effectively under `/crm` when deployed).
- **`frontend/src/components/`** — UI including `Layouts/AppSidebar.vue`, `Modals/AboutModal.vue`, settings, telephony, etc.
- **`frontend/index.html`** — Document title, Apple web app title, links to favicon/splash assets under `/assets/crm/manifest/`.
- **`frontend/vite.config.js`** — Vite + Vue; **PWA manifest** (`vite-plugin-pwa`) with `name`, `short_name`, `description`, icons; Frappe UI plugin copies built HTML to `crm/www/crm.html`.

## Build and asset pipeline

From `pyproject.toml` (`[tool.bench.assets]`):

- **`build_dir`**: `./frontend`
- **`out_dir`**: `../crm/public/frontend`
- **`index_html_path`**: `../crm/www/crm.html`

The root `package.json` scripts run `yarn dev` / `yarn build` inside `frontend/`. The frontend `package.json` build runs Vite with `--base=/assets/crm/frontend/` and copies `index.html` to `../crm/www/crm.html`.

**`.gitignore`** excludes `crm/public/frontend` and `crm/www/crm.html`, so a fresh clone may not contain built assets until you run a build in a bench or CI context.

## Frontend vs backend request flow

1. User opens `/crm` on a Frappe site (after authentication as required by the site).
2. Frappe serves the page with boot data from `crm/www/crm.py`.
3. The SPA loads assets from `/assets/crm/frontend/...` and calls Frappe APIs via `frappe-ui` / `frappeRequest`.

## Product branding and customization (highest leverage)

These files are the usual first stops for renaming the product to **Konnecct** (without renaming the Python package):

- `crm/hooks.py` — `app_title`, desk tile title/logo/route- `frontend/index.html` — `<title>`, PWA-related meta
- `frontend/vite.config.js` — PWA manifest text and icons
- `frontend/src/components/Icons/CRMLogo.vue` — in-app logo SVG
- `crm/public/images/logo.svg` — logo used in hooks for desk/app selector
- `frontend/src/components/Modals/AboutModal.vue` — name, copyright, outbound links
- `crm/fcrm/workspace/frappe_crm/frappe_crm.json` — Desk workspace label
- `README.md`, `.github/logo.svg` — repository and marketing presentation
- `crm/locale/main.pot` and `crm/locale/*.po` — translated strings

Detailed mapping: **`BRANDING_SURFACE_MAP.md`**.

## Multi-tenancy and roles (pointer)

The app does not implement SaaS-style row-level tenants in hooks. **`CRM Organization`** is a CRM account/customer record, not an isolation boundary for multiple customers on one site. See **`MULTITENANCY_NOTES.md`**.

## Related documents

- [BRANDING_SURFACE_MAP.md](BRANDING_SURFACE_MAP.md)
- [MULTITENANCY_NOTES.md](MULTITENANCY_NOTES.md)
- [SAFE_VS_RISKY_CHANGES.md](SAFE_VS_RISKY_CHANGES.md)
