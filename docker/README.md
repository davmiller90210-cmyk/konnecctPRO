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

Default login (from `init.sh`): **Administrator** / **admin** (change after first login).

## Environment variables

| Variable    | Purpose |
|------------|---------|
| `DOMAIN`   | Hostname served by Caddy; used for TLS (must match DNS). |
| `SITE_NAME`| Frappe site name — use the **same** value as `DOMAIN` for a public site so the `Host` header matches. |

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
