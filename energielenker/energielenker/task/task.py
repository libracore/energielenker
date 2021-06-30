# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from energielenker.energielenker.project.project import PowerProject


def on_update(task, event):
	if task.project and not task.flags.from_project:
		update_project(task.project)

def update_project(project):
	project = frappe.get_cached_doc("Project", project)
	PowerProject(project).update_kpis()

	parent_project = frappe.get_value(
		"Subproject",
		{"subproject": project.name},
		"parent"
	)

	if parent_project:
		update_project(parent_project)
