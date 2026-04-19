# Copyright (c) Konnecct
"""Override Frappe portal sign-up to skip welcome/verification email and sign the user in immediately.

Upstream `sign_up` emails a password-reset link; without outgoing email that step blocks real users.
Konnecct: require chosen password on the signup form; legacy API without password still gets a random
password and ``konnecct_must_set_password`` so CRM can offer a first-time set-password flow.
"""

from frappe import _
from frappe.auth import LoginManager
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, escape_html, random_string, cstr
from frappe.website.utils import is_signup_disabled

import frappe

from crm.api.user import validate_new_password_strength
from crm.konnecct_workspace import provision_new_user_workspace

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
@rate_limit(limit=25, seconds=60 * 60)  # IP-based limit for anonymous signup
def sign_up(
	email: str,
	full_name: str,
	redirect_to: str,
	password: str | None = None,
	confirm_password: str | None = None,
) -> tuple[int, str]:
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

	chosen_password = (password or "").strip()
	confirm = (confirm_password or "").strip()

	if chosen_password or confirm:
		if not chosen_password or not confirm:
			return 0, _("Password and confirmation are required")
		if chosen_password != confirm:
			return 0, _("Passwords do not match")
		try:
			validate_new_password_strength(chosen_password)
		except frappe.ValidationError as e:
			return 0, cstr(e) or _("Password is too weak")
		new_password_value = chosen_password
		must_set_flag = 0
	else:
		new_password_value = random_string(32)
		must_set_flag = 1

	user_data: dict = {
		"doctype": "User",
		"email": email,
		"first_name": escape_html(full_name),
		"enabled": 1,
		"new_password": new_password_value,
		"user_type": "System User",
		"send_welcome_email": 0,
	}
	# Set on the new doc before insert — do not use db.set_value here; it bumps ``modified``
	# in the DB while this doc is still in memory and the following ``save()`` raises
	# TimestampMismatchError ("Document has been modified after you have opened it").
	if frappe.db.has_column("User", "konnecct_must_set_password"):
		user_data["konnecct_must_set_password"] = must_set_flag

	user = frappe.get_doc(user_data)
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = bool(must_set_flag)
	user.flags.no_welcome_mail = True
	# Roles must exist before ``insert()`` or Frappe shows "No Roles Specified" (User.check_roles_added).
	user.append_roles("Sales User")
	_restrict_modules_to_fcrm(user)
	user.insert()

	try:
		provision_new_user_workspace(user.name)
	except Exception:
		# If this fails, add the user to a workspace from Desk or run `provision_new_user_workspace` from bench console.
		frappe.log_error(title="Konnecct workspace provisioning failed")

	target = sanitize_redirect(redirect_to) if redirect_to else "/crm"
	frappe.cache.hset("redirect_after_login", user.name, target)

	frappe.local.login_manager = LoginManager()
	frappe.local.login_manager.login_as(user.name)

	if must_set_flag:
		return 1, _("Welcome to Konnecct. Set a password in CRM under Settings → Profile → Change Password.")
	return 1, _("Welcome to Konnecct.")
