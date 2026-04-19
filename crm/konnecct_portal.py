# Copyright (c) Konnecct
"""Portal /login and /signup branding and signup flags (Website Settings).

Kept in a small module so `bench execute crm.konnecct_portal.apply_website_portal_settings`
is obvious and importable from install hooks.
"""

import frappe


def apply_website_portal_settings():
	"""Konnecct: branding, signups allowed, login and signup links visible."""
	doc = frappe.get_single("Website Settings")
	doc.app_name = "Konnecct"
	doc.title_prefix = "Konnecct"
	doc.disable_signup = 0
	doc.hide_footer_signup = 0
	doc.hide_login = 0
	doc.footer_powered = "Konnecct"
	logo_url = "/assets/crm/images/logo.svg"
	doc.brand_html = (
		f'<div class="website-brand" style="text-align:center">'
		f'<img src="{logo_url}" alt="Konnecct" style="max-height:48px;width:auto;"/></div>'
	)
	doc.save(ignore_permissions=True)
	frappe.clear_cache()
