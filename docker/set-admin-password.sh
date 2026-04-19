#!/usr/bin/env bash
# Reset the Frappe "Administrator" password on an existing Docker site.
# Usage (from this directory):
#   ./set-admin-password.sh 'YourNewLongRandomPassword'
#   ADMIN_PASSWORD='...' ./set-admin-password.sh
set -euo pipefail

cd "$(dirname "$0")"

if [[ -f .env ]]; then
	set -a
	# shellcheck disable=SC1091
	source .env
	set +a
fi

SITE_NAME="${SITE_NAME:-crm.localhost}"
PASS="${1:-${ADMIN_PASSWORD:-}}"

if [[ -z "$PASS" ]]; then
	echo "Usage: ./set-admin-password.sh 'your-new-password'"
	echo "   or: ADMIN_PASSWORD='your-new-password' ./set-admin-password.sh"
	exit 1
fi

docker compose exec \
	-e SITE_FOR_BENCH="${SITE_NAME}" \
	-e PASS_FOR_BENCH="${PASS}" \
	frappe \
	bash -lc 'cd /home/frappe/frappe-bench && bench --site "$SITE_FOR_BENCH" set-admin-password "$PASS_FOR_BENCH"'

echo "Administrator password updated for site ${SITE_NAME}."
