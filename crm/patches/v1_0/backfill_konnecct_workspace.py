# Copyright (c) Konnecct
"""Create a default Konnecct Workspace, add CRM-role users as members, and backfill Lead/Deal links."""

import frappe

MIGRATION_WORKSPACE_TITLE = "Organization"


def execute():
	if not frappe.db.has_table("tabKonnecct Workspace"):
		return

	ws_name = _get_or_create_migration_workspace()
	_add_crm_role_members(ws_name)
	_backfill_leads_and_deals(ws_name)


def _get_or_create_migration_workspace() -> str:
	existing = frappe.get_all(
		"Konnecct Workspace",
		filters={"title": MIGRATION_WORKSPACE_TITLE},
		pluck="name",
		limit=1,
	)
	if existing:
		return existing[0]

	ws = frappe.get_doc(
		{
			"doctype": "Konnecct Workspace",
			"title": MIGRATION_WORKSPACE_TITLE,
			"owner": "Administrator",
			"members": [],
		}
	)
	ws.flags.ignore_permissions = True
	ws.insert()
	return ws.name


def _crm_role_user_names() -> list[str]:
	roles = ("Sales User", "Sales Manager", "System Manager")
	placeholders = ", ".join(["%s"] * len(roles))
	return frappe.db.sql(
		f"""
		SELECT DISTINCT hr.parent
		FROM `tabHas Role` hr
		INNER JOIN `tabUser` u ON u.name = hr.parent
		WHERE hr.parenttype = 'User'
			AND hr.role IN ({placeholders})
			AND IFNULL(u.user_type, '') != 'Website User'
			AND IFNULL(u.enabled, 0) = 1
			AND u.name NOT IN ('Guest', 'Administrator')
		""",
		roles,
		pluck=True,
	)


def _add_crm_role_members(ws_name: str) -> None:
	ws = frappe.get_doc("Konnecct Workspace", ws_name)
	existing = {m.user for m in ws.members}
	changed = False
	for user in _crm_role_user_names():
		if user not in existing:
			ws.append(
				"members",
				{
					"user": user,
					"is_workspace_admin": 1 if user == ws.owner else 0,
				},
			)
			existing.add(user)
			changed = True
	if changed:
		ws.flags.ignore_permissions = True
		ws.save()


def _backfill_leads_and_deals(ws_name: str) -> None:
	if frappe.db.has_column("CRM Lead", "konnecct_workspace"):
		frappe.db.sql(
			"""
			UPDATE `tabCRM Lead`
			SET `konnecct_workspace` = %s
			WHERE IFNULL(`konnecct_workspace`, '') = ''
			""",
			ws_name,
		)
	if frappe.db.has_column("CRM Deal", "konnecct_workspace"):
		frappe.db.sql(
			"""
			UPDATE `tabCRM Deal`
			SET `konnecct_workspace` = %s
			WHERE IFNULL(`konnecct_workspace`, '') = ''
			""",
			ws_name,
		)
