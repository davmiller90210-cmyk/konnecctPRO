# Copyright (c) Konnecct
"""Return Jinja template path for Konnecct signup HTML (see `signup_form_template` in hooks.py).

Must be a loader-relative path like ``crm/templates/signup.html``.
An absolute path from ``get_app_path`` breaks ``frappe.get_template`` (TemplateNotFound).
"""


def get_signup_form_path() -> str:
	return "crm/templates/signup.html"
