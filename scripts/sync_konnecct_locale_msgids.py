#!/usr/bin/env python3
"""Align crm/locale gettext files with Konnecct Phase 1 English source strings.

Canonical workflow (when frappe-bench is available)::

    cd frappe-bench
    bench generate-pot-file --app crm

That regenerates ``crm/locale/main.pot`` from the codebase. Use this script when
bench is not available: it applies the same msgid renames Phase 1 introduced in
Vue/Python sources, and updates translator comments that referred to the old
product name.

Run from repo root::

    python scripts/sync_konnecct_locale_msgids.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIR = ROOT / "crm" / "locale"

# Order matters: longer / more specific strings first.
MSGID_REPLACEMENTS: list[tuple[str, str]] = [
(
		"You do not have enough permissions to access Frappe CRM. Please contact your administrator if you believe this is an error.",
		"You do not have enough permissions to access Konnecct. Please contact your administrator if you believe this is an error.",
	),
	("Connect ERPNext to Frappe CRM", "Connect ERPNext to Konnecct"),
	("Frappe CRM mobile", "Konnecct mobile"),
	(
		"Are you sure you want to login to your Frappe Cloud dashboard?",
		"You will open your hosting provider dashboard in a new tab.",
	),
	("Login to Frappe Cloud?", "Open hosting dashboard?"),
	("You do not have permission to access Frappe CRM", "You do not have permission to access Konnecct"),
	("GitHub Repository", "Source code"),
	("Frappe CRM", "Konnecct"),
]

COMMENT_REPLACEMENTS: list[tuple[str, str]] = [
	("Frappe CRM Workspace", "Konnecct Workspace"),
]

MAIN_POT_HEADER_REPLACEMENTS: list[tuple[str, str]] = [
	("# Translations template for Frappe CRM.", "# Translations template for Konnecct."),
	(
		"# This file is distributed under the same license as the Frappe CRM project.",
		"# This file is distributed under the same license as the Konnecct project.",
	),
	('"Project-Id-Version: Frappe CRM VERSION\\n"', '"Project-Id-Version: Konnecct VERSION\\n"'),
	('"Report-Msgid-Bugs-To: shariq@frappe.io\\n"', '"Report-Msgid-Bugs-To: hello@konnecct.com\\n"'),
]


def patch_text(path: Path, text: str) -> str:
	for old, new in MSGID_REPLACEMENTS:
		text = text.replace(old, new)
	for old, new in COMMENT_REPLACEMENTS:
		text = text.replace(old, new)
	if path.name == "main.pot":
		for old, new in MAIN_POT_HEADER_REPLACEMENTS:
			text = text.replace(old, new)
	return text


def main() -> None:
	if not LOCALE_DIR.is_dir():
		raise SystemExit(f"Missing locale dir: {LOCALE_DIR}")

	updated = 0
	for pattern in ("*.pot", "*.po"):
		for path in sorted(LOCALE_DIR.glob(pattern)):
			orig = path.read_text(encoding="utf-8")
			new = patch_text(path, orig)
			if new != orig:
				path.write_text(new, encoding="utf-8")
				updated += 1
				print("updated", path.relative_to(ROOT))
	print(f"done ({updated} files changed)")


if __name__ == "__main__":
	main()
