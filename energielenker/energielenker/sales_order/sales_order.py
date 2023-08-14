# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

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
def make_issue_from_sales_order(sales_order, subject, priority, details):
    """ create issue from sales order """
    
    doc = frappe.get_doc("Sales Order", sales_order)
    issue = frappe.new_doc("Issue")
    issue.subject = subject
    issue.priority = priority
    issue.customer = doc.customer
    issue.raised_by = doc.owner or ""
    issue.address = doc.customer_address
    issue.description = details or ""
    issue.sales_order = sales_order
    issue.flags.ignore_mandatory = True
    issue.insert(ignore_permissions=True)
    
    return issue.name

def update_delivery_status(so, event):
    """Update item wise delivery status from Sales Order for drop shipping"""
    tot_qty, delivered_qty = 0.0, 0.0
    sales_order = so
    for item in sales_order.items:
        if item.delivered_by_supplier:
            item_delivered_qty = item.qty
            item.db_set("delivered_qty", flt(item_delivered_qty), update_modified=False)

        delivered_qty += item.delivered_qty
        tot_qty += item.qty

    if tot_qty != 0:
        sales_order.db_set("per_delivered", flt(delivered_qty/tot_qty) * 100,
            update_modified=False)
