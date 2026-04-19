# Copyright (c) Konnecct
"""Grant full app-level access to the designated Konnecct owner account (one-time migrate)."""

import frappe

# Site operator / product owner — System Manager + CRM roles, all modules unblocked.
APP_OWNER_EMAIL = "azzamjamil00@gmail.com"


def execute():
	user_name = frappe.db.get_value("User", {"email": APP_OWNER_EMAIL}, "name")
	if not user_name:
		frappe.log_error(
			f"No User found with email {APP_OWNER_EMAIL}; skipped app-owner role grant.",
			"Konnecct app owner patch",
		)
		return

	user = frappe.get_doc("User", user_name)
	user.flags.ignore_permissions = True
	user.user_type = "System User"
	user.append_roles("System Manager", "Sales Manager", "Sales User")
	user.set("block_modules", [])
	user.save()
