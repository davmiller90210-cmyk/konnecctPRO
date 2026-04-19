# Copyright (c) Konnecct
"""Override Frappe portal sign-up to skip welcome/verification email and sign the user in immediately.

Upstream `sign_up` emails a password-reset link; without outgoing email that step blocks real users.
"""

from frappe import _
from frappe.auth import LoginManager
from frappe.utils import cint, escape_html, random_string
from frappe.website.utils import is_signup_disabled

import frappe

try:
	# Frappe v15+ (see frappe/core/doctype/user/user.py sign_up)
	from frappe.www.login import sanitize_redirect
except ImportError:  # pragma: no cover - older benches
	from frappe.website.utils import sanitize_redirect


def _restrict_modules_to_fcrm(user) -> None:
	"""Match `CRMInvitation.accept` for Sales User — only the FCRM module is unblocked."""
	block_modules = frappe.get_all(
		"Module Def",
		fields=["name as module"],
		filters={"name": ["!=", "FCRM"]},
	)
	if block_modules:
		user.set("block_modules", block_modules)


@frappe.whitelist(allow_guest=True)
def sign_up(email: str, full_name: str, redirect_to: str) -> tuple[int, str]:
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.enabled:
			return 0, _("Already Registered")
		return 0, _("Registered but disabled")

	max_signups = cint(frappe.get_system_settings("max_signups_allowed_per_hour") or 300)
	if frappe.db.get_creation_count("User", 60) >= max_signups:
		frappe.respond_as_web_page(
			_("Temporarily Disabled"),
			_(
				"Too many users signed up recently, so the registration is disabled. Please try back in an hour"
			),
			http_status_code=429,
		)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(full_name),
			"enabled": 1,
			"new_password": random_string(10),
			# Same model as CRM Invitation: team members use the /crm app, not only portal /me.
			"user_type": "System User",
			"send_welcome_email": 0,
		}
	)
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = True
	user.flags.no_welcome_mail = True
	user.insert()

	user.append_roles("Sales User")
	_restrict_modules_to_fcrm(user)
	user.save(ignore_permissions=True)

	target = sanitize_redirect(redirect_to) if redirect_to else "/crm"
	frappe.cache.hset("redirect_after_login", user.name, target)

	frappe.local.login_manager = LoginManager()
	frappe.local.login_manager.login_as(user.name)

	return 1, _("Welcome to Konnecct. Set a password anytime under My Account → Reset Password.")
