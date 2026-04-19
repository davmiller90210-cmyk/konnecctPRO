#!/usr/bin/env bash
# Copy Konnecct files from this repo into the running Frappe Docker container,
# run migrate (custom fields / patches), then clear-cache + restart.
#
# Usage (on your VM, after: cd ~/konnecctPRO && git pull origin develop):
#   bash scripts/sync_konnecct_into_docker_frappe.sh
#
# Env:
#   KONNECCT_REPO  — default: $HOME/konnecctPRO
#   COMPOSE_DIR    — default: $HOME/konnecctPRO/docker
#   SITE_NAME      — default: app.konnecct.com

set -euo pipefail

KONNECCT_REPO="${KONNECCT_REPO:-$HOME/konnecctPRO}"
COMPOSE_DIR="${COMPOSE_DIR:-$HOME/konnecctPRO/docker}"
SITE_NAME="${SITE_NAME:-app.konnecct.com}"

DEST_PKG="/home/frappe/frappe-bench/apps/crm/crm"
DEST_LOGIN_JS="${DEST_PKG}/templates/includes/login/login.js"
DEST_SIGNUP_HTML="${DEST_PKG}/templates/signup.html"

if [[ ! -d "$COMPOSE_DIR" ]]; then
	echo "Missing COMPOSE_DIR: $COMPOSE_DIR" >&2
	exit 1
fi
if [[ ! -d "$KONNECCT_REPO/crm" ]]; then
	echo "Missing repo crm folder: $KONNECCT_REPO/crm (git pull first?)" >&2
	exit 1
fi

cd "$COMPOSE_DIR"
CID="$(docker compose ps -q frappe)"
if [[ -z "${CID:-}" ]]; then
	echo "Frappe container not running. From $COMPOSE_DIR run: docker compose up -d" >&2
	exit 1
fi

copy() {
	local name="$1"
	local src="$KONNECCT_REPO/crm/$name"
	if [[ ! -f "$src" ]]; then
		echo "Skip (missing on host): $src" >&2
		return 0
	fi
	docker cp "$src" "$CID:$DEST_PKG/$name"
	echo "OK: $name -> container:$DEST_PKG/$name"
}

copy_rel() {
	local rel="$1"
	local src="$KONNECCT_REPO/crm/$rel"
	if [[ ! -f "$src" ]]; then
		echo "Skip (missing on host): $src" >&2
		return 0
	fi
	local dest="${DEST_PKG}/${rel}"
	docker compose exec frappe bash -lc "mkdir -p $(dirname "${dest}")"
	docker cp "$src" "${CID}:${dest}"
	echo "OK: $rel -> container:${dest}"
}

echo "Using container $CID, site $SITE_NAME"
copy hooks.py
copy konnecct_signup.py
copy konnecct_signup_template.py
copy konnecct_portal.py
copy install.py
copy_rel api/user.py
copy_rel setup/__init__.py
copy_rel setup/konnecct_auth_fields.py
copy_rel patches.txt
copy_rel patches/v1_0/add_konnecct_user_password_flag.py

LOGIN_SRC="${KONNECCT_REPO}/crm/templates/includes/login/login.js"
if [[ -f "$LOGIN_SRC" ]]; then
	docker compose exec frappe bash -lc "mkdir -p $(dirname "${DEST_LOGIN_JS}")"
	docker cp "$LOGIN_SRC" "${CID}:${DEST_LOGIN_JS}"
	echo "OK: login.js -> container:${DEST_LOGIN_JS}"
else
	echo "Skip (missing on host): $LOGIN_SRC" >&2
fi

SIGNUP_SRC="${KONNECCT_REPO}/crm/templates/signup.html"
if [[ -f "$SIGNUP_SRC" ]]; then
	docker compose exec frappe bash -lc "mkdir -p $(dirname "${DEST_SIGNUP_HTML}")"
	docker cp "$SIGNUP_SRC" "${CID}:${DEST_SIGNUP_HTML}"
	echo "OK: signup.html -> container:${DEST_SIGNUP_HTML}"
else
	echo "Skip (missing on host): $SIGNUP_SRC" >&2
fi

docker compose exec frappe bash -lc "cd ~/frappe-bench && bench --site ${SITE_NAME} migrate && bench --site ${SITE_NAME} clear-cache && bench restart"

echo "Done. Rebuild / deploy the CRM frontend if you changed Vue (e.g. bench build --app crm or your CI image)."
