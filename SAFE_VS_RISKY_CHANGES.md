# Safe vs risky changes: Konnecct (Frappe CRM fork)

Use this as a **practical risk guide** when rebranding to **Konnecct** and evolving toward a hosted product. It complements [BRANDING_SURFACE_MAP.md](BRANDING_SURFACE_MAP.md) and [MULTITENANCY_NOTES.md](MULTITENANCY_NOTES.md).

## Easy (low risk, high visibility)

**Goal:** User-visible branding and marketing without touching core data models.

- **Frappe hooks display strings:** `crm/hooks.py` — `app_title`, `app_description`, `app_publisher`, `app_email` (as appropriate), `add_to_apps_screen` title/logo path (keep path valid).
- **Package display title:** `crm/__init__.py` — `__title__`.
- **SPA title and PWA text:** `frontend/index.html`, `frontend/vite.config.js` manifest fields.
- **Logos:** `frontend/src/components/Icons/CRMLogo.vue`, `crm/public/images/logo.svg`; add or replace files under `/assets/crm/manifest/` if you want correct favicons and installable PWA icons.
- **About modal:** `frontend/src/components/Modals/AboutModal.vue` — product name, copyright line, outbound links (point to your docs and support).
- **Permission messages:** `crm/www/crm.py`, `frontend/src/pages/NotPermitted.vue`.
- **Invitation emails:** `crm/fcrm/doctype/crm_invitation/crm_invitation.py`, `crm/templates/emails/crm_invitation.html`.
- **Desk workspace label:** `crm/fcrm/workspace/frappe_crm/frappe_crm.json` — human-readable `label` / `title` (avoid renaming internal `name` without understanding Desk sync implications; label/title changes are usually safer).
- **README and `.github` assets:** `README.md`, `.github/logo.svg`, screenshots (purely repo presentation).
- **Package metadata:** `pyproject.toml`, root `package.json` — descriptions and URLs (no runtime effect on a running site).
- **Doc links in Vue:** Settings and help URLs (`docs.frappe.io/crm` → your docs) when you have replacements.

**Caveat:** Any string wrapped in `_()` or `__()` may need **translation catalog** updates (see Medium).

## Medium difficulty (plan and test)

**Goal:** Consistent branding across languages, builds, and Desk.

- **Translations:** `crm/locale/main.pot` and all `crm/locale/*.po` — changing English sources requires regenerating or manually syncing msgids; Crowdin (`crowdin.yml`) may need a project retarget.
- **PWA assets:** Ensure every path referenced in `frontend/index.html` and `vite.config.js` exists after `bench build` / `yarn build` so installs and iOS splash screens do not 404.
- **Twilio integration naming:** `crm_twilio_settings.py` — `friendly_resource_name` changes what Twilio objects are called; safe for branding but verify integration docs.
- **CI/CD forks:** `.github/workflows/*` still pointing at `frappe/crm` will confuse future you; update when you cut releases from your fork.
- **`standard_dropdown_items`:** `crm/hooks.py` — items like “Login to Frappe Cloud” may be wrong for Konnecct; removing or replacing is product-specific (test Desk/nav behavior on Frappe v15/v16).

## Risky (easy to break the install or upgrades)

**Defer until you have a migration checklist.**

- **Renaming the Python package / app name from `crm`:** Would break:
  - Import paths (`import crm...`)
  - Asset URLs (`/assets/crm/...`), Vite `base`, `pyproject.toml` `out_dir`
  - Bench app directory name and `apps.txt`
  - Hooks module paths, patches, CI `APPS_JSON`
- **Renaming DocType `name` values in JSON** (e.g. workspace or module identifiers) without following Frappe’s migrate/rename patterns.
- **Editing auto-generated type blocks** in DocType Python files marked as auto-generated.
- **Disabling or heavily changing permission hooks** without a full security review (data leaks).
- **Forking or pinning `frappe-ui` incorrectly** — the Vite plugin in `frontend/vite.config.js` can use the submodule or npm package; a wrong version can break the build.

## Probably leave alone (early in your fork)

Unless you have a specific bug or feature need:

- **Core Frappe permission models** (System Manager / Sales roles) until you design tenant or admin semantics.
- **Patch files and `patches.txt`** — historical upgrade path for existing databases.
- **Large-scale refactors** that merge modules or rename DocTypes “for cleanliness.”
- **Submodule URL** for `frappe-ui` until you intend to maintain a hard fork.

## Suggested phased approach for Konnecct

1. **Phase 1 — Visual and copy rebrand:** Hooks, SPA, About, emails, README, workspace label; add PWA icons if missing.
2. **Phase 2 — Fork hygiene:** URLs in components, CI workflows, package `repository` fields, telemetry names if you care about analytics cleanliness.
3. **Phase 3 — Hosting product:** Site provisioning automation, backups, your docs site—not this repo alone.
4. **Phase 4 — Optional true multi-tenancy on one DB:** Only with a dedicated design (see [MULTITENANCY_NOTES.md](MULTITENANCY_NOTES.md)).

## Related documents

- [CODEBASE_AUDIT.md](CODEBASE_AUDIT.md)
- [BRANDING_SURFACE_MAP.md](BRANDING_SURFACE_MAP.md)
- [MULTITENANCY_NOTES.md](MULTITENANCY_NOTES.md)
