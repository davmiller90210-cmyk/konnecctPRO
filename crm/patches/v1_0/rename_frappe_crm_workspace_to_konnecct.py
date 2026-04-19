import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	"""Rename legacy Desk workspace title key from upstream name to Konnecct."""
	if not frappe.db.exists("Workspace", "Frappe CRM"):
		return
	if frappe.db.exists("Workspace", "Konnecct"):
		return
	rename_doc("Workspace", "Frappe CRM", "Konnecct", force=True)
