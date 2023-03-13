# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def fetch_payment_schedule_from_so(so, event):
    if so.project:
        from energielenker.energielenker.zahlungsplan.zahlungsplan import so_to_project
        so_to_project(project=so.project, sales_order=so.name, payment_schedule=so.payment_schedule)
    return

@frappe.whitelist()
def get_employee(user=None):
    if not user:
        user = frappe.session.user
    
    employee = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}' LIMIT 1""".format(user=user), as_dict=True)
    if len(employee) > 0:
        return employee[0].name
    else:
        return 'MA00023'


@frappe.whitelist()
def make_issue_from_sales_order(sales_order, subject, priority, details): #, ignore_communication_links=False):
	""" raise a issue from sales order """

	doc = frappe.get_doc("Sales Order", sales_order)
	issue = frappe.get_doc({
		"doctype": "Issue",
		"subject": subject,
		"priority": priority,
		"customer": doc.customer,
		"issue_type": 'Reklamation',
		"raised_by": doc.owner or "",
		"address": doc.customer_address,
		"description": details or "",
		"sales_order": sales_order,
	}).insert(ignore_permissions=True)

	# ~ link_communication_to_document(doc, "Issue", issue.name, ignore_communication_links)

	return issue.name
