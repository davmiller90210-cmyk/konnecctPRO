# Copyright (c) Konnecct
"""Return absolute path to Konnecct signup HTML (see `signup_form_template` hook in hooks.py)."""

import frappe


def get_signup_form_path() -> str:
	return frappe.get_app_path("crm", "templates", "signup.html")
