# Copyright (c) Konnecct
"""Custom fields and hooks for Konnecct auth (password lifecycle)."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

KONNECCT_USER_CUSTOM_FIELDS = {
	"User": [
		{
			"fieldname": "konnecct_must_set_password",
			"label": "Konnecct must set password",
			"fieldtype": "Check",
			"default": "0",
			"insert_after": "email",
			"read_only": 1,
			"hidden": 1,
			"description": "Set when the user was created without choosing a password; cleared after they set one in CRM.",
		},
	]
}


def ensure_konnecct_user_auth_fields() -> None:
	create_custom_fields(KONNECCT_USER_CUSTOM_FIELDS, update=True)
