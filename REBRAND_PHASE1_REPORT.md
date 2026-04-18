# Rebrand Phase 1 report (Frappe CRM to Konnecct)

## Scope

Phase 1: safe, user-facing branding only. The Python package, bench app name, asset base path, and module name remain `crm`. No multitenancy or framework permission rewrites.

## Planned files and safety rationale

| File | Why it is safe |
|------|----------------|
| [crm/hooks.py](crm/hooks.py) | Display metadata (`app_title`, publisher, description, email, desk tile title, icon title) and one navbar label; `app_name` unchanged. |
| [crm/__init__.py](crm/__init__.py) | `__title__` is display-only. |
| [frontend/index.html](frontend/index.html) | Browser / PWA meta titles only. |
| [frontend/vite.config.js](frontend/vite.config.js) | PWA manifest name, short name, description only. |
| [frontend/src/components/Icons/CRMLogo.vue](frontend/src/components/Icons/CRMLogo.vue) | Placeholder logo component. |
| [crm/public/images/logo.svg](crm/public/images/logo.svg), [.github/logo.svg](.github/logo.svg) | Static assets; hooks still point at `/assets/crm/images/logo.svg`. |
| [frontend/src/components/Modals/AboutModal.vue](frontend/src/components/Modals/AboutModal.vue) | About copy and outbound links. |
| [crm/fcrm/workspace/frappe_crm/frappe_crm.json](crm/fcrm/workspace/frappe_crm/frappe_crm.json) | Only `label` and `title` updated; `name` left as `Frappe CRM` to avoid Workspace document rename / migration risk. |
| [crm/fcrm/doctype/crm_invitation/crm_invitation.py](crm/fcrm/doctype/crm_invitation/crm_invitation.py) | Invitation email title string. |
| [crm/templates/emails/crm_invitation.html](crm/templates/emails/crm_invitation.html) | Email body text. |
| [frontend/src/pages/NotPermitted.vue](frontend/src/pages/NotPermitted.vue) | User-visible error string. |
| [crm/www/crm.py](crm/www/crm.py) | Translated permission error only. |
| [README.md](README.md) | Repository branding and intro; technical install commands largely preserved. |
| [frontend/src/components/Layouts/AppSidebar.vue](frontend/src/components/Layouts/AppSidebar.vue) | Help docs URL and mobile bookmark title string. |
| [frontend/src/components/Settings/ERPNextSettings.vue](frontend/src/components/Settings/ERPNextSettings.vue) | User-facing docs link and integration headline. |
| [frontend/src/components/Settings/AssignmentRules/AssignmentRuleView.vue](frontend/src/components/Settings/AssignmentRules/AssignmentRuleView.vue) | Documentation links in settings UI. |
| [crm/fcrm/doctype/crm_form_script/crm_form_script.json](crm/fcrm/doctype/crm_form_script/crm_form_script.json) | User-visible documentation URL field in Desk. |
| [crm/fcrm/doctype/crm_twilio_settings/crm_twilio_settings.py](crm/fcrm/doctype/crm_twilio_settings/crm_twilio_settings.py) | Twilio resource friendly name (branding in external console). |
| [pyproject.toml](pyproject.toml) | Project description, authors, homepage (not import paths). `Repository` / `Bug Reports` URLs still point upstream until you change them. |
| [package.json](package.json) | npm metadata; package `name` remains `crm`. |
| [frontend/src/composables/frappecloud.js](frontend/src/composables/frappecloud.js) | Dialog copy only; integration method names unchanged. |

## Files changed (this phase)

- `crm/hooks.py`
- `crm/__init__.py`
- `crm/www/crm.py`
- `crm/templates/emails/crm_invitation.html`
- `crm/fcrm/doctype/crm_invitation/crm_invitation.py`
- `crm/fcrm/doctype/crm_twilio_settings/crm_twilio_settings.py`
- `crm/fcrm/doctype/crm_form_script/crm_form_script.json`
- `crm/fcrm/workspace/frappe_crm/frappe_crm.json`
- `crm/public/images/logo.svg`
- `pyproject.toml`
- `package.json`
- `README.md`
- `.github/logo.svg`
- `frontend/index.html`
- `frontend/vite.config.js`
- `frontend/src/components/Icons/CRMLogo.vue`
- `frontend/src/components/Modals/AboutModal.vue`
- `frontend/src/components/Layouts/AppSidebar.vue`
- `frontend/src/components/Settings/ERPNextSettings.vue`
- `frontend/src/components/Settings/AssignmentRules/AssignmentRuleView.vue`
- `frontend/src/pages/NotPermitted.vue`
- `frontend/src/composables/frappecloud.js`
- `scripts/sync_konnecct_locale_msgids.py` (maintainer script; correct gettext alignment)
- `crm/locale/main.pot` and all `crm/locale/*.po` (msgids synced to match Phase 1 English sources)

## Translations (gettext)

**Canonical approach:** From a frappe-bench that has this app installed, run:

```bash
bench generate-pot-file --app crm
```

That regenerates `crm/locale/main.pot` from the codebase. Merge updated `.po` files with your translation workflow (e.g. Crowdin).

**In this repo:** `scripts/sync_konnecct_locale_msgids.py` renames msgids (and related translator comments / POT header) to match the Konnecct strings introduced in Phase 1, when bench is not available. Re-run it after any further English copy changes, or replace its output with a fresh `bench generate-pot-file` run.

## Placeholder assets and URLs

- **Logo:** New placeholder mark (dark slate + cyan) in `CRMLogo.vue`, `crm/public/images/logo.svg`, and `.github/logo.svg`. Replace with final Konnecct creative when ready.
- **Marketing URLs:** `https://konnecct.com`, `https://konnecct.com/docs`, `https://konnecct.com/source`, `https://konnecct.com/support` are placeholders until your real site and repo exist.
- **Contact:** `hello@konnecct.com` in hooks and `pyproject.toml` is a placeholder.

## Remaining Frappe / upstream references (classified)

### Safe to change later (product copy / community links)

- [README.md](README.md): Managed hosting paragraph still mentions Frappe Cloud; Telegram/Discuss links point at upstream community; screenshot filenames still `FrappeCRMHeroImage.png`; easy-install / `ghcr.io/frappe/crm` install block is upstream-oriented.
- [frontend/src/components/Settings/emailConfig.js](frontend/src/components/Settings/emailConfig.js): “Frappe Mail Site”, provider name “Frappe Mail”, and setup copy referencing Frappe Mail (and matching `msgid`s in locale files).
- Prior audit docs ([BRANDING_SURFACE_MAP.md](BRANDING_SURFACE_MAP.md), etc.) still describe pre-Phase-1 strings in places; refresh when convenient.

### Technical / internal — keep for now

- Package and paths: `app_name = "crm"`, imports `import crm`, `/assets/crm/`, `telemetryPlugin` `app_name: 'crm'`, onboarding keys `useOnboarding('frappecrm')`.
- [pyproject.toml](pyproject.toml) `Repository` and `Bug Reports` still reference `github.com/frappe/crm` (upstream).
- [package.json](package.json) `repository.url` and `bugs.url` still reference upstream.
- [frontend/src/composables/frappecloud.js](frontend/src/composables/frappecloud.js): `frappecloud.com`, whitelisted method `frappe.integrations.frappe_providers.frappecloud_billing.current_site_info`, function names `loginToFrappeCloud`.
- [crm/www/crm.py](crm/www/crm.py): `is_fc_site`, Frappe Cloud billing import.
- [crm/fcrm/workspace/frappe_crm/frappe_crm.json](crm/fcrm/workspace/frappe_crm/frappe_crm.json): Workspace document `name` remains `"Frappe CRM"`; folder name `frappe_crm` unchanged.
- Frappe / ERPNext compatibility table, framework links, and **LICENSE** / copyright headers in source files (legal attribution).
- [.github/workflows](.github/workflows) and container build args still tied to upstream `frappe/crm` where applicable.

### Needs manual review

- Whether to rename Workspace record `name` from `Frappe CRM` to `Konnecct` via Frappe migrate/rename (data migration, not done in Phase 1).
- Real **homepage**, **docs**, **support**, and **git remote** URLs to substitute for `konnecct.com` placeholders.
- Whether [README.md](README.md) community section (Telegram, Discuss) should point to Konnecct channels or stay as upstream.
- Legal entity line: About modal now says “Based on the open-source Frappe CRM project” — confirm with counsel if you need explicit license stack / trademark language.
- Email sender identity for invitations (still uses site default; only template text changed).

## Follow-up (not Phase 1)

- After new user-visible strings: prefer `bench generate-pot-file --app crm`, or run `python scripts/sync_konnecct_locale_msgids.py` only for Konnecct-specific msgid renames until bench is available.
- Add real PWA manifest PNGs under `/assets/crm/manifest/` if missing on your bench build.
- Update CI `APPS_JSON` / container registry when you publish your own images.

