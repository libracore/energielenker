# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProjectTeam(Document):
	pass

@frappe.whitelist()
def get_members(doc):
	team = frappe.get_doc("Project Team", doc)
	
	return [[member.employee, member.full_name] for member in team.members]
