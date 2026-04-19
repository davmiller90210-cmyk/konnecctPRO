# Docker stack (Frappe + Caddy HTTPS)

## Quick start (public HTTPS with Let’s Encrypt)

1. Point **DNS** for your hostname (e.g. `app.konnecct.com`) **A/AAAA** to this server’s public IP.
2. Open host firewall: **80**, **443** (and **443/udp** if you use HTTP/3).
3. From this directory:

```bash
cp .env.example .env
# Edit .env: set DOMAIN and SITE_NAME to your hostname (usually the same value).
docker compose up -d
```

4. Open `https://YOUR_DOMAIN/crm` — Caddy will obtain a **free** TLS certificate from **Let’s Encrypt** automatically.

Login: user **`Administrator`**. The password is:

- **`ADMIN_PASSWORD`** from your `.env` when the bench is **first** created (`init.sh` passes it to `bench new-site`; default is **`admin`** if unset).
- On a **site that already exists**, changing `.env` does **not** update the user; run from this directory:

  ```bash
  ./set-admin-password.sh 'YourNewLongRandomPassword'
  ```

  (Requires Bash — e.g. Git Bash or WSL on Windows. Uses `SITE_NAME` from `.env`.)

**Production:** set a strong `ADMIN_PASSWORD` in `.env` **before** the first `docker compose up`, or run `set-admin-password.sh` after install.

First-time `init.sh` installs the **Konnecct** app from this repository’s GitHub fork (`develop`), not the default upstream `crm` marketplace app — see `bench get-app` in [init.sh](init.sh).

## Portal signup when outbound email is not configured

Frappe’s default `sign_up` tells users to check email for a registration link. Konnecct overrides that API in [`crm/konnecct_signup.py`](../crm/konnecct_signup.py) (see `override_whitelisted_methods` in [`crm/hooks.py`](../crm/hooks.py)): **no welcome mail**, **immediate login**, **password + confirm on the signup form** (see [`crm/templates/signup.html`](../crm/templates/signup.html)), and the new user is provisioned like a **CRM invitation** (**System User** + **Sales User**, FCRM module only) so they can open **`/crm`**. Users who were created without a chosen password get a first-time **Set password** path in CRM (see [`crm/api/user.py`](../crm/api/user.py)). The login script [`crm/templates/includes/login/login.js`](../crm/templates/includes/login/login.js) redirects successful signups to **`/crm`**. Use [`scripts/sync_konnecct_into_docker_frappe.sh`](../scripts/sync_konnecct_into_docker_frappe.sh) (runs **`bench migrate`**) or **`bench migrate`** after pulling so the User custom field is created.

**Security:** public sign-up with **Sales User** means anyone who can register can use CRM data — fine for a trusted team; disable signups in **Website Settings** if the site is on the open internet. **Integrations** (Twilio, WhatsApp, etc.) stay **Sales Manager / System Manager** only unless you change DocType permissions and the CRM Settings UI deliberately.

## Host vs container (read this once)

- On the **host** you have **`~/konnecctPRO`** — your Git repo. There is **no** `~/frappe-bench` on the host unless you installed bench yourself; **that is normal.**
- **`frappe-bench` exists only inside the `frappe` Docker container** at `/home/frappe/frappe-bench`. You never `cd` there on the host; you run **`docker compose exec frappe ...`** and paths like `~/frappe-bench` are **inside** that container.
- The Python package for the app is **`crm`**, so new files from this repo live at  
  **`/home/frappe/frappe-bench/apps/crm/crm/`** (inner `crm` folder — next to `hooks.py`).

If `git remote` inside the container shows only **`upstream` → `github.com/frappe/crm`**, the container is still on **upstream CRM**, not your Konnecct fork — so modules like `crm.konnecct_portal` will **not** exist until you copy or replace that code.

---

## Fix portal branding / signup (pick one path)

### A) Copy `konnecct_portal.py` from your host clone into the container

**If you see `no such file or directory` for `../crm/konnecct_portal.py`**, your **`~/konnecctPRO` on the server is behind GitHub.** Update it first:

```bash
cd ~/konnecctPRO
git pull origin develop
test -f crm/konnecct_portal.py && echo OK || echo "Still missing — check branch / remote"
```

From **`~/konnecctPRO/docker`** on the host (adjust site name if needed):

```bash
docker compose cp ../crm/konnecct_portal.py frappe:/home/frappe/frappe-bench/apps/crm/crm/konnecct_portal.py
docker compose exec frappe bash -lc 'cd ~/frappe-bench && bench --site app.konnecct.com execute crm.konnecct_portal.apply_website_portal_settings && bench --site app.konnecct.com clear-cache'
```

If `docker compose cp` is not available, use the container name from `docker compose ps` (e.g. `crm-frappe-1`):

```bash
docker cp ~/konnecctPRO/crm/konnecct_portal.py crm-frappe-1:/home/frappe/frappe-bench/apps/crm/crm/konnecct_portal.py
```

### B) No new files: apply Website Settings from a one-shot console (always works)

```bash
docker compose exec frappe bash -lc 'cd ~/frappe-bench && bench --site app.konnecct.com console' <<'PY'
import frappe
d = frappe.get_single("Website Settings")
d.app_name = "Konnecct"
d.title_prefix = "Konnecct"
d.disable_signup = 0
d.hide_footer_signup = 0
d.hide_login = 0
d.footer_powered = "Konnecct"
d.brand_html = '<div class="website-brand" style="text-align:center"><img src="/assets/crm/images/logo.svg" alt="Konnecct" style="max-height:48px;width:auto;"/></div>'
d.save(ignore_permissions=True)
frappe.db.commit()
frappe.clear_cache()
print("Konnecct website settings OK")
PY
```

### C) Git: point the container’s `apps/crm` at your fork (only if histories are compatible)

Inside the container, `apps/crm` may still be a clone of **`frappe/crm`** only. Adding **`origin`** → your **`konnecctPRO`** fork and pulling **`develop`** can fail if the repos do not share history (monorepo vs single-app repo). If `git pull` fails, use **A** or **B** above.

```bash
docker compose exec frappe bash -lc 'cd ~/frappe-bench/apps/crm && git remote -v'
docker compose exec frappe bash -lc 'cd ~/frappe-bench/apps/crm && git remote add origin https://github.com/davmiller90210-cmyk/konnecctPRO.git 2>/dev/null; git fetch origin && git checkout develop && git pull origin develop'
docker compose exec frappe bash -lc 'cd ~/frappe-bench && bench --site app.konnecct.com migrate && bench --site app.konnecct.com clear-cache && bench restart'
```

(Replace `app.konnecct.com` with your `SITE_NAME` from `.env` if different.)

**Optional dev mount:** uncomment the `../crm` volume on the `frappe` service in [docker-compose.yml](docker-compose.yml) so the container’s `apps/crm` tracks `konnecctPRO/crm` from the host (only after the bench exists; restart Compose).

## Environment variables

| Variable    | Purpose |
|------------|---------|
| `DOMAIN`   | Hostname served by Caddy; used for TLS (must match DNS). |
| `SITE_NAME`| Frappe site name — use the **same** value as `DOMAIN` for a public site so the `Host` header matches. |
| `ADMIN_PASSWORD` | Initial **Administrator** password on **first** bench creation only; use `./set-admin-password.sh` to change later. |

## Already created the stack with `crm.localhost`?

Data is in Docker volumes. Either:

- Add your public domain to the existing site (inside the `frappe` container):

  ```bash
  docker compose exec frappe bash -lc 'cd ~/frappe-bench && bench setup add-domain crm.localhost app.konnecct.com && bench --site crm.localhost clear-cache'
  ```

  (Replace domains to match your site.)

- Or remove volumes and recreate with `DOMAIN` / `SITE_NAME` set in `.env` (destructive).

## Ports

- **80 / 443**: Caddy (HTTP redirects to HTTPS; ACME HTTP-01 uses port 80).
- Frappe **8000** / **9000** are **not** published on the host; only reachable inside the Compose network via Caddy.

## Troubleshooting TLS

- `docker compose logs -f caddy` — look for ACME / certificate errors.
- Ensure **no other process** binds ports 80/443 on the host.
- Let’s Encrypt must reach your server on **port 80** from the internet for the default HTTP challenge.

## `FileNotFoundError` when running `bench` (e.g. `set-admin-password`)

The `bench` command runs Frappe using **`frappe-bench/env/bin/python`**. If that file is missing (common after **`docker compose pull`** upgraded the `frappe/bench` image, or a half-finished first boot), you see:

`FileNotFoundError: [Errno 2] No such file or directory` inside `bench/cli.py` → `os.execv(...)`.

**Fix (pick one):**

1. **Restart the Frappe container** after `git pull` so [init.sh](init.sh) runs again — it now **rebuilds the virtualenv** when `apps/frappe` exists but `env/bin/python` does not (your DB and site files stay in MariaDB / the bench tree).

   ```bash
   cd ~/konnecctPRO/docker
   git pull
   docker compose up -d --force-recreate frappe
   docker compose logs -f frappe
   ```

   Wait until logs show Gunicorn/workers running, then retry your `bench` command.

2. **One-shot repair** (if you cannot restart yet):

   ```bash
   cd ~/konnecctPRO/docker
   docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && rm -rf env && python3 -m venv env && ./env/bin/pip install --upgrade pip setuptools wheel && ./env/bin/pip install -e ./apps/frappe && for d in apps/*/; do [ "$d" = "apps/frappe/" ] && continue; [ -f "${d}pyproject.toml" ] || [ -f "${d}setup.py" ] || continue; ./env/bin/pip install -e "$d"; done'
   ```

Then, for example:

```bash
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site "${SITE_NAME:-app.konnecct.com}" set-admin-password '\''your-password-here'\'''
```

(Replace site name and password; or `source` your `.env` first.)

## 502 Bad Gateway from Caddy (`connection refused` to :8000)

Frappe’s Gunicorn defaults to **127.0.0.1:8000** inside the container, so **Caddy cannot connect** from another container. `init.sh` sets `bind_address` to **0.0.0.0** in `sites/common_site_config.json`.

**If you created the bench before that fix**, apply once and restart Frappe:

```bash
docker compose exec frappe bash -lc 'cd ~/frappe-bench && python3 <<PY
import json, pathlib
p = pathlib.Path("sites/common_site_config.json")
cfg = json.loads(p.read_text()) if p.exists() else {}
cfg["bind_address"] = "0.0.0.0"
p.write_text(json.dumps(cfg, indent=2) + "\n")
print("OK:", p)
PY
bench restart'
```

Or recreate the stack after `git pull` so `init.sh` runs the helper (existing volumes keep DB; only config file changes).
