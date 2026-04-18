#!/bin/bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-crm.localhost}"

# Gunicorn must listen on 0.0.0.0 so Caddy (another container) can reach :8000.
# Default is often 127.0.0.1 → Caddy gets "connection refused" / 502.
ensure_gunicorn_listens_all_interfaces() {
	local bench_dir="${1:-/home/frappe/frappe-bench}"
	local cc="${bench_dir}/sites/common_site_config.json"
	export _FRAPPE_COMMON_SITE_CONFIG="${cc}"
	python3 <<'PY'
import json
import os
import pathlib

p = pathlib.Path(os.environ["_FRAPPE_COMMON_SITE_CONFIG"])
cfg = {}
if p.exists():
	cfg = json.loads(p.read_text(encoding="utf-8"))
cfg["bind_address"] = "0.0.0.0"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"bind_address=0.0.0.0 written to {p}")
PY
}

cd /home/frappe

if [ -d "frappe-bench/apps/frappe" ]; then
	echo "Bench already exists, starting..."
	cd frappe-bench
	ensure_gunicorn_listens_all_interfaces "$(pwd)"
	exec bench start
fi

echo "Creating new bench (site: ${SITE_NAME})..."

bench init --skip-redis-config-generation frappe-bench --version version-15

cd frappe-bench

bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

bench get-app crm --branch main

bench new-site "${SITE_NAME}" \
	--force \
	--mariadb-root-password 123 \
	--admin-password admin \
	--no-mariadb-socket

bench --site "${SITE_NAME}" install-app crm
bench --site "${SITE_NAME}" set-config developer_mode 1
bench --site "${SITE_NAME}" set-config mute_emails 1
bench --site "${SITE_NAME}" set-config server_script_enabled 1
bench --site "${SITE_NAME}" clear-cache
bench use "${SITE_NAME}"

ensure_gunicorn_listens_all_interfaces "$(pwd)"

exec bench start
