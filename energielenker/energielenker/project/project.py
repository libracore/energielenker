# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from energielenker.energielenker.timesheet_manager import \
    get_employee_rate_external
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils.data import get_datetime


class PowerProject():
	def __init__(self, project):
		self.project = project
		self.subprojects = []
		
		for row in project.subprojects:
			pp = PowerProject(frappe.get_doc("Project", row.subproject))
			pp.project.update_costing()
			pp.update_kpis()
			self.subprojects.append(pp.project)

	def update_kpis(self):
		self.update_custom_kpis()
		self.update_erpnext_kpis()
		self.update_dates()
		self.project.calculate_gross_margin()

	def update_custom_kpis(self):
		custom_kpis = [
			"open_quotation_amount",
			"expected_time",
			"expected_billable_amount",
			"open_time",
			"open_billable_amount",
			"time_trend",
			"billable_amount_trend",
			"expected_purchase_cost",
			"purchase_cost_trend",
			"overall_trend"
		]

		for kpi in custom_kpis:
			self.update_custom_kpi(kpi)

	def update_erpnext_kpis(self):
		erpnext_kpis = [
			"actual_time",
			"total_costing_amount",
			"total_expense_claim",
			"total_purchase_cost",
			"total_sales_amount",
			"total_billable_amount",
			"total_billed_amount",
			"total_consumed_material_cost",
		]

		for kpi in erpnext_kpis:
			self.update_erpnext_kpi(kpi)

	def update_dates(self):
		dates = [
			("actual_start_date", False),
			("actual_end_date", True)
		]

		for (date, startdate) in dates:
			self.update_date(date, startdate)

	def update_date(self, date, startdate):
		dates = [subproject.get(date) for subproject in self.subprojects if subproject.get(date)]
		project_date = self.project.get(date)

		if project_date:
			dates.append(get_datetime(project_date))

		if dates:
			self.project.set(date, max(dates) if startdate else min(dates))

	def update_custom_kpi(self, kpi):
		value_project = getattr(self, "get_{kpi}".format(kpi=kpi))()
		self.update_kpi(kpi, value_project)

	def update_erpnext_kpi(self, kpi):
		value_project = self.project.get(kpi) or 0
		self.update_kpi(kpi, value_project)

	def update_kpi(self, kpi, value_project):
		value_subprojects = 0

		for subproject in self.subprojects:
			value_subprojects += subproject.get(kpi)

		self.project.set(kpi, value_project + value_subprojects)

	def get_overall_trend(self):
		return self.get_purchase_cost_trend() + self.get_billable_amount_trend()

	def get_purchase_cost_trend(self):
		return self.get_expected_purchase_cost() - (self.project.total_purchase_cost or 0)

	def get_expected_purchase_cost(self):
		return frappe.get_all(
			"Purchase Order Item",
			filters={
				"project": self.project.name,
				"docstatus": ["=", "1"]
			},
			fields=["sum(base_net_amount) as sum"],
		)[0].sum or 0

	def get_time_trend(self):
		return self.get_expected_time() - (self.project.actual_time or 0) - self.get_open_time()

	def get_billable_amount_trend(self):
		return (
			self.get_expected_billable_amount()
			- (self.project.total_billable_amount or 0)
			- self.get_open_billable_amount()
		)

	def get_open_quotation_amount(self):
		return frappe.get_all(
			"Quotation",
			filters={
				"project": self.project.name,
				"status": ["in", ["Open", "Replied"]]
			},
			fields=["sum(grand_total) as sum"],
		)[0].sum or 0

	def get_expected_time(self):
		return frappe.get_all(
			"Task",
			filters={
				"project": self.project.name
			},
			fields=["sum(expected_time) as sum"]
		)[0].sum or 0

	def get_open_billable_amount(self):
		open_tasks = frappe.get_all(
			"Task",
			filters={
				"project": self.project.name,
				"status": ["not in", ["Completed", "Cancelled"]]
			},
			fields=["expected_time", "actual_time", "completed_by"],
		)
		
		open_billable_amount = 0

		for task in open_tasks:
			open_billable_amount += (
				max(task.expected_time - task.actual_time, 0) 
				* self.get_employee_rate(task.completed_by)
			)
		
		return open_billable_amount

	def get_expected_billable_amount(self):
		tasks = frappe.get_all(
			"Task",
			filters={
				"project": self.project.name
			},
			fields=["expected_time", "completed_by"]
		)
		
		expected_billable_amount = 0

		for task in tasks:
			expected_billable_amount += (
				task.expected_time 
				* self.get_employee_rate(task.completed_by)
			)
		
		return expected_billable_amount

	def get_employee_rate(self, employee):
		employee = frappe.get_value("Employee", {"user_id": employee}, "name")

		return (
			get_employee_rate_external(employee) 
			if employee
			else self.project.default_external_rate
		)

	def get_open_time(self):
		open_tasks = frappe.get_all(
			"Task",
			filters={
				"project": self.project.name,
				"status": ["not in", ["Completed", "Cancelled"]]
			},
			fields=["expected_time", "actual_time"],
			as_list=True
		)

		return sum(map(lambda task: max(task[0] - task[1], 0), open_tasks))

def autoname(project, event):
	project.name = make_autoname(project.naming_series)

def onload(project, event):
	PowerProject(project).update_kpis()

def validate(project, event):
	validate_subprojects(project)
	PowerProject(project).update_kpis()

def validate_subprojects(project):
	for row in project.subprojects:
		if project.name == row.subproject:
			frappe.throw(_("Project cannot be a subproject of itself."))

		parent_project = frappe.get_value(
			"Subproject",
			{"subproject": row.subproject},
			"parent"
		)

		if parent_project and parent_project != project.name:
			frappe.throw(_("Subproject {} is already part of project {}.")
				.format(row.subproject, parent_project))

		if subproject_is_a_parent_of_project(row.subproject, project.name):
			frappe.throw(_("Subproject {} is actually a parent of project {}.")
				.format(row.subproject, project.name))

def subproject_is_a_parent_of_project(subproject, project):
	subprojects_of_subproject = get_subprojects(subproject)

	if not subprojects_of_subproject:
		return False

	if project in subprojects_of_subproject:
		return True

	for subproject in subprojects_of_subproject:
		if subproject_is_a_parent_of_project(subproject, project):
			return True

	return False

def get_subprojects(project):
	subprojects = frappe.get_all(
		"Subproject",
		filters={
			"parent": project,
		},
		fields=["subproject"],
		as_list=True
	)

	return [subproject[0] for subproject in subprojects]

@frappe.whitelist()
def get_contact_details(doc):
	from frappe.contacts.doctype.address.address import get_condensed_address

	contact = frappe.get_doc("Contact", doc).as_dict()

	contact["email_ids"] = frappe.get_list("Contact Email", filters={
			"parenttype": "Contact",
			"parent": contact.name,
			"is_primary": 0
		}, fields=["email_id"])

	contact["phone_nos"] = frappe.get_list("Contact Phone", filters={
			"parenttype": "Contact",
			"parent": contact.name,
			"is_primary_phone": 0,
			"is_primary_mobile_no": 0
		}, fields=["phone"])

	if contact.address:
		address = frappe.get_doc("Address", contact.address)
		contact["address"] = get_condensed_address(address)

	return {"contact_list": [contact]}
