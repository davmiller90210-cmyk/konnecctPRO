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
