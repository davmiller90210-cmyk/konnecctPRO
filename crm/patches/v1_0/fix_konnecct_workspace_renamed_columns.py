# Copyright (c) Konnecct
"""After renaming Link fields (avoid Frappe reserved names), backfill data from legacy columns if present."""

import frappe


def execute():
	if not frappe.db.has_table("tabKonnecct Workspace"):
		return

	# Standard metadata `owner` is the document creator — use it when workspace_owner is empty.
	if frappe.db.has_column("Konnecct Workspace", "workspace_owner"):
		frappe.db.sql(
			"""
			UPDATE `tabKonnecct Workspace`
			SET `workspace_owner` = `owner`
			WHERE IFNULL(`workspace_owner`, '') = ''
				AND IFNULL(`owner`, '') != ''
			"""
		)

	if not frappe.db.has_table("tabKonnecct Workspace Member"):
		return

	if frappe.db.has_column("Konnecct Workspace Member", "member_user") and frappe.db.has_column(
		"Konnecct Workspace Member", "user"
	):
		frappe.db.sql(
			"""
			UPDATE `tabKonnecct Workspace Member`
			SET `member_user` = `user`
			WHERE IFNULL(`member_user`, '') = ''
				AND IFNULL(`user`, '') != ''
			"""
		)
