# Branding surface map: Konnecct (Frappe CRM fork)

This file lists **where the product name, logos, external links, and related metadata appear** so you can rebrand to **Konnecct** systematically. Entries are based on repository search (source and config files), not on generated build output.

## Login and unauthenticated experience

| Surface | Location | Notes |
|---------|----------|--------|
| **Website login (`/#login`)** | Frappe website stack + **Website Settings** (DB) | Copy and logo are driven by `app_name`, `brand_html`, etc. Konnecct sets these in `crm/install.py` (`apply_website_portal_settings`) on install/migrate. |
| **Permission denied (server)** | `crm/www/crm.py` | Uses Konnecct in the permission error string. |
| **Permission denied (SPA)** | `frontend/src/pages/NotPermitted.vue` | Konnecct copy. |

## Browser chrome, PWA, and public metadata

| Surface | File(s) |
|---------|---------|
| **Document title** | `frontend/index.html` (`<title>Konnecct</title>`) |
| **Apple web app title** | `frontend/index.html` (`apple-mobile-web-app-title`) |
| **Favicon / touch icon / splash screens** | `frontend/index.html` — links under `/assets/crm/manifest/` (many `apple-touch-startup-image` entries) |
| **Web app manifest (PWA)** | `frontend/vite.config.js` — `VitePWA` block: `name`, `short_name`, `description`, `start_url: '/crm'`, icon paths under `/assets/crm/manifest/` |

**PWA asset paths:** The HTML and Vite config reference `/assets/crm/manifest/*.png` and splash `.jpg` files. In this repository, `crm/public/` currently contains at least `images/logo.svg`; the **manifest image files may be produced by your build pipeline, shipped separately, or missing until you add them**. Verify on a built bench site under `sites/assets/crm/manifest/` or equivalent.

## Frappe Desk and hooks (app identity)

| Surface | File | Fields / behavior |
|---------|------|-------------------|
| **App title, publisher, description, license, email** | `crm/hooks.py` | `app_title`, `app_publisher`, `app_description`, `app_email`, `app_license`, `app_icon_url`, `app_icon_title`, `app_icon_route` |
| **Desk “Apps” tile** | `crm/hooks.py` | `add_to_apps_screen`: `name`, `logo`, `title`, `route`, `has_permission` |
| **Python package display title** | `crm/__init__.py` | `__title__` |
| **Desk workspace name** | `crm/fcrm/workspace/frappe_crm/frappe_crm.json` | `name` / `label` / `title` → Konnecct; existing sites: patch `rename_frappe_crm_workspace_to_konnecct` |
| **Standard navbar dropdown** | `crm/hooks.py` | `standard_dropdown_items` includes “Login to hosting dashboard”, “About”, “Log out” |

## Logos and imagery

| Surface | File |
|---------|------|
| **In-app SVG logo component** | `frontend/src/components/Icons/CRMLogo.vue` |
| **Desk / app selector logo (asset)** | `crm/public/images/logo.svg` (referenced from `crm/hooks.py`) |
| **README / GitHub** | `.github/logo.svg`, `.github/screenshots/*` |
| **Email provider art (Frappe Mail)** | `frontend/src/images/frappe-mail.svg` (used from `frontend/src/components/Settings/emailConfig.js`) |

## In-app UI: sidebar, help, about, settings

| Surface | File | What to update |
|---------|------|----------------|
| **Help modal docs URL** | `frontend/src/components/Layouts/AppSidebar.vue` | `docsLink="https://konnecct.com/docs"` |
| **Mobile bookmark title** | `frontend/src/components/Layouts/AppSidebar.vue` | `__('Konnecct mobile')` |
| **About dialog** | `frontend/src/components/Modals/AboutModal.vue` | Product name Konnecct; links to konnecct.com; attribution mentions upstream Frappe CRM |
| **ERPNext integration copy** | `frontend/src/components/Settings/ERPNextSettings.vue` | “Connect ERPNext to Konnecct” |
| **Assignment rules docs** | `frontend/src/components/Settings/AssignmentRules/AssignmentRuleView.vue` | `https://konnecct.com/docs/assignment-rule` |
| **Email settings (hosted mail)** | `frontend/src/components/Settings/emailConfig.js` | UI labels “Mail site URL” / hosted mail copy; **service** value sent to the server remains `Frappe Mail` where the framework expects it |
| **Hosting dashboard** | `frontend/src/composables/frappecloud.js` | “Open hosting dashboard?” (provider URL from site info) |

## Backend strings and email

| Surface | File |
|---------|------|
| **Invitation email subject / template args** | `crm/fcrm/doctype/crm_invitation/crm_invitation.py` | `title` → Konnecct |
| **Invitation email body** | `crm/templates/emails/crm_invitation.html` | Konnecct |
| **Twilio resource naming** | `crm/fcrm/doctype/crm_twilio_settings/crm_twilio_settings.py` | `friendly_resource_name` → Konnecct |
| **DocType field: documentation URL** | `crm/fcrm/doctype/crm_form_script/crm_form_script.json` | `documentation_url` → `https://konnecct.com/docs/custom-actions` |

## Telemetry and analytics (non-visual)

| Surface | File |
|---------|------|
| **Telemetry app id** | `frontend/src/main.js` — `telemetryPlugin` with `app_name: 'crm'` |
| **Server-side event name** | `crm/www/crm.py` — `capture("active_site", "crm")` |

These affect analytics pipelines, not user-visible branding.

## Demo and hosting-specific behavior

| Surface | File | Notes |
|---------|------|--------|
| **Live demo login** | `crm/api/live_demo.py` | Demo site redirect behavior; comment references `frappecrm-demo.frappe.cloud` |
| **Frappe Cloud detection** | `crm/www/crm.py` | `is_fc_site` in boot; drives trial/billing-related UI |
| **README demo link** | `README.md` | Points at Frappe demo and Frappe Cloud signup imagery |

## Package metadata and repository identity

| Surface | File |
|---------|------|
| **Python project** | `pyproject.toml` — `name`, `authors`, `description`, `project.urls` (Homepage, Repository, Bug Reports) |
| **Root npm package** | `package.json` — `name`, `description`, `author`, `homepage`, `repository`, `bugs` |
| **Frontend package** | `frontend/package.json` — `name: "crm-ui"` |

## CI and automation (fork maintenance)

These reference upstream `frappe/crm` and Frappe infrastructure; update when you own releases and images.

| Surface | File(s) |
|---------|---------|
| **Container build app URL** | `.github/workflows/builds.yml` — `APPS_JSON` with `https://github.com/frappe/crm` |
| **Release notes** | `.github/workflows/release_notes.yml` — GitHub API targets `frappe/crm` |
| **Translation PR bot** | `.github/helper/update_pot_file.sh` — remotes and PR target repo |

## Translations (broad surface)

| Surface | Path |
|---------|------|
| **Template catalog** | `crm/locale/main.pot` |
| **Per-language catalogs** | `crm/locale/*.po` (29 locale files in this tree) |
| **Crowdin mapping** | `crowdin.yml` |

Many msgids contain “Frappe CRM”, permission errors, workspace labels, and ERPNext connection copy. Changing English source strings requires updating **`main.pot`** (regenerated via bench/Frappe extract) and **`*.po`** files or your Crowdin workflow.

## Copyright headers (legal / attribution)

Almost all Python and JS source files under `crm/` and some `frontend/` files include `Copyright (c) ... Frappe Technologies...`. Rebranding the **product** does not automatically require rewriting every header; legal review may suggest a consistent “Konnecct” or “forked from” policy.

## Quick checklist for “Konnecct” (no package rename)

1. `crm/hooks.py` — `app_title`, desk tile `title`, optional `app_publisher` / `app_description`.
2. `crm/__init__.py` — `__title__`.
3. `frontend/index.html` + `frontend/vite.config.js` — titles and PWA manifest.
4. `frontend/src/components/Icons/CRMLogo.vue` + `crm/public/images/logo.svg` + PWA icons under manifest paths.
5. `frontend/src/components/Modals/AboutModal.vue` — name, copyright, links.
6. `crm/fcrm/workspace/frappe_crm/frappe_crm.json` — workspace label.
7. Invitation flow: `crm_invitation.py` + `crm/templates/emails/crm_invitation.html`.
8. Permission errors: `crm/www/crm.py`, `frontend/src/pages/NotPermitted.vue`.
9. Docs and marketing URLs in Vue components and `README.md`.
10. `crm/locale/main.pot` + `.po` refresh (or Crowdin).

See [SAFE_VS_RISKY_CHANGES.md](SAFE_VS_RISKY_CHANGES.md) for difficulty and risk tiers.
