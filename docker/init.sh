#!/bin/bash
set -euo pipefail

SITE_NAME="${SITE_NAME:-crm.localhost}"

cd /home/frappe

if [ -d "frappe-bench/apps/frappe" ]; then
	echo "Bench already exists, starting..."
	cd frappe-bench
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

exec bench start
