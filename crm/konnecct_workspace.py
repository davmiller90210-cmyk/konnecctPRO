# Copyright (c) Konnecct
"""Row-level workspace tenancy for CRM Lead / CRM Deal (MVP).

Workspace membership is stored on **Konnecct Workspace** (owner + child **Konnecct Workspace Member**).
The current workspace for UI defaults is ``frappe.defaults`` key ``konnecct_workspace``.
"""

from __future__ import annotations

import frappe
from frappe import _


def _bypasses_workspace_tenancy(user: str | None = None) -> bool:
	"""Users who manage the whole site see all workspaces and all scoped CRM rows."""
	user = user or frappe.session.user
	if user == "Administrator":
		return True
	return "System Manager" in frappe.get_roles(user)


def get_user_workspace_names(user: str | None = None) -> list[str]:
	"""Return workspace names the user may access (owner or listed member)."""
	user = user or frappe.session.user
	if user in ("Guest",):
		return []

	names: set[str] = set()
	names.update(frappe.get_all("Konnecct Workspace", filters={"owner": user}, pluck="name") or [])
	for (parent,) in (
		frappe.db.sql(
			"SELECT `parent` FROM `tabKonnecct Workspace Member` WHERE `user`=%s",
			user,
		)
		or []
	):
		names.add(parent)
	return sorted(names)


def get_current_workspace(user: str | None = None) -> str | None:
	user = user or frappe.session.user
	ws = frappe.defaults.get_user_default("konnecct_workspace", user)
	if not ws:
		return None
	if ws not in get_user_workspace_names(user):
		return None
	return ws


def set_user_default_workspace(workspace: str, user: str | None = None) -> None:
	user = user or frappe.session.user
	if workspace not in get_user_workspace_names(user):
		frappe.throw(_("Not a member of workspace {0}").format(workspace))
	frappe.defaults.set_user_default("konnecct_workspace", workspace, user)


def set_current_workspace(workspace: str, user: str | None = None) -> None:
	set_user_default_workspace(workspace, user)


def create_workspace_for_user(user_name: str, title: str | None = None) -> str:
	"""Create a **Konnecct Workspace** owned by the user with a single admin member row."""
	title = title or _("{0}'s workspace").format(user_name)
	ws = frappe.get_doc(
		{
			"doctype": "Konnecct Workspace",
			"title": title,
			"owner": user_name,
			"members": [{"user": user_name, "is_workspace_admin": 1}],
		}
	)
	ws.flags.ignore_permissions = True
	ws.insert()
	return ws.name


def provision_new_user_workspace(user_name: str) -> str:
	"""Used after portal signup: personal workspace + default."""
	ws_name = create_workspace_for_user(user_name)
	frappe.defaults.set_user_default("konnecct_workspace", ws_name, user_name)
	return ws_name


def ensure_default_workspace_for_user(user: str | None = None) -> str | None:
	"""Ensure the user belongs to at least one workspace and has a valid default."""
	user = user or frappe.session.user
	if user in ("Guest", "Administrator"):
		return None

	workspaces = get_user_workspace_names(user)
	if not workspaces:
		provision_new_user_workspace(user)
		workspaces = get_user_workspace_names(user)
	if not workspaces:
		return None

	current = frappe.defaults.get_user_default("konnecct_workspace", user)
	if current and current in workspaces:
		return current

	chosen = workspaces[0]
	frappe.defaults.set_user_default("konnecct_workspace", chosen, user)
	return chosen


def on_login(login_manager=None) -> None:
	ensure_default_workspace_for_user()


def _user_sql_literal(user: str) -> str:
	return frappe.db.escape(user, percent=False)


def _lead_workspace_match_sql(user: str) -> str:
	u = _user_sql_literal(user)
	return f"""(`tabCRM Lead`.`konnecct_workspace` IS NOT NULL AND (`tabCRM Lead`.`konnecct_workspace` IN (SELECT `parent` FROM `tabKonnecct Workspace Member` WHERE `user` = {u}) OR `tabCRM Lead`.`konnecct_workspace` IN (SELECT `name` FROM `tabKonnecct Workspace` WHERE `owner` = {u})))"""


def _deal_workspace_match_sql(user: str) -> str:
	u = _user_sql_literal(user)
	return f"""(`tabCRM Deal`.`konnecct_workspace` IS NOT NULL AND (`tabCRM Deal`.`konnecct_workspace` IN (SELECT `parent` FROM `tabKonnecct Workspace Member` WHERE `user` = {u}) OR `tabCRM Deal`.`konnecct_workspace` IN (SELECT `name` FROM `tabKonnecct Workspace` WHERE `owner` = {u})))"""


def get_lead_permission_query_conditions(user: str) -> str:
	if _bypasses_workspace_tenancy(user):
		return ""
	return _lead_workspace_match_sql(user)


def get_deal_permission_query_conditions(user: str) -> str:
	if _bypasses_workspace_tenancy(user):
		return ""
	return _deal_workspace_match_sql(user)


def get_workspace_permission_query_conditions(user: str) -> str:
	if _bypasses_workspace_tenancy(user):
		return ""
	u = _user_sql_literal(user)
	return f"""(`tabKonnecct Workspace`.`owner` = {u} OR `tabKonnecct Workspace`.`name` IN (SELECT `parent` FROM `tabKonnecct Workspace Member` WHERE `user` = {u}))"""


def has_lead_permission(doc, ptype=None, user=None, perm_type=None, permtype=None, **kwargs) -> bool | None:
	pt = ptype or perm_type or permtype or "read"
	return _has_lead_or_deal_permission(doc, user, pt)


def has_deal_permission(doc, ptype=None, user=None, perm_type=None, permtype=None, **kwargs) -> bool | None:
	pt = ptype or perm_type or permtype or "read"
	return _has_lead_or_deal_permission(doc, user, pt)


def _has_lead_or_deal_permission(doc, user, ptype: str) -> bool | None:
	user = user or frappe.session.user
	if _bypasses_workspace_tenancy(user):
		return True
	if ptype == "create":
		return bool(get_user_workspace_names(user))
	ws = doc.get("konnecct_workspace")
	if not ws:
		return False
	if ws not in get_user_workspace_names(user):
		return False
	return True


def has_workspace_doc_permission(doc, _ptype=None, user=None, _perm_type=None, _permtype=None, **kwargs) -> bool | None:
	user = user or frappe.session.user
	if _bypasses_workspace_tenancy(user):
		return True
	if doc.owner == user:
		return True
	for row in doc.get("members") or []:
		if row.user == user:
			return True
	return False


def set_workspace_on_lead(doc, method=None) -> None:
	_set_workspace_on_doc(doc)


def set_workspace_on_deal(doc, method=None) -> None:
	_set_workspace_on_doc(doc)


def _set_workspace_on_doc(doc) -> None:
	if doc.get("konnecct_workspace"):
		return
	ws = get_current_workspace() or ensure_default_workspace_for_user()
	if ws:
		doc.konnecct_workspace = ws


def merge_workspace_filter_into_filters(doctype: str, filters) -> frappe._dict:
	"""Restrict CRM Lead / CRM Deal list API rows to the session user's workspaces (not site admins)."""
	filters = frappe._dict(filters)
	if doctype not in ("CRM Lead", "CRM Deal"):
		return filters
	if _bypasses_workspace_tenancy():
		return filters

	workspaces = get_user_workspace_names()
	if not workspaces:
		filters["name"] = "__no_konnecct_workspace_access__"
		return filters

	filters["konnecct_workspace"] = ["in", workspaces]
	return filters
