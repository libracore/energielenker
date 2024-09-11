# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import json
from frappe.utils.data import getdate
from erpnext.controllers.accounts_controller import update_child_qty_rate

@frappe.whitelist() 
def overwrite_before_update_after_submit():
    #************************************************************************************
    #overwrite before_update_after_submit to also update_projektbewertung_ignorieren_in_project_in_project
    from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
    SalesOrder.before_update_after_submit = so_before_update_after_submit
    #************************************************************************************

def so_before_update_after_submit(self):
    #original method but adding update_projektbewertung_ignorieren_in_project_or_in_so
    from energielenker.energielenker.zahlungsplan.zahlungsplan import update_projektbewertung_ignorieren_in_project_or_in_so
    update_projektbewertung_ignorieren_in_project_or_in_so(self=self, event="so_update", pb_ignorieren=self.projektbewertung_ignorieren)
    self.validate_po()
    self.validate_drop_ship()
    self.validate_supplier_after_submit()
    self.validate_delivery_date()

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
    issue.issue_type = "Reklamation"
    issue.flags.ignore_mandatory = True
    issue.insert(ignore_permissions=True)
    
    return issue.name
    
@frappe.whitelist()
def amend_so_issue(sales_order, amended_from):
    """ amend sales_order field in issue if sales order got ammended"""    
    issues = frappe.get_list(
        "Issue",
        filters={"sales_order": amended_from, "status": ["!=", "Closed"]},
        fields=["name"]
    )
    
    if issues:
        for issue in issues:
            doc = frappe.get_doc("Issue", issue)
            doc.sales_order = sales_order
            doc.save()
            frappe.msgprint("Offene Anfrage <a href='#Form/Issue/{0}'><b>{0}</b></a> hat jetzt aktuellen Kundenauftragsbezug.".format(doc.name))

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

@frappe.whitelist()
def fetch_supplier(item):
    i = frappe.get_doc("Item", item)
    if len(i.supplier_items) > 0:
        return i.supplier_items[0].supplier
    return None

@frappe.whitelist()
def update_zusatzgeschaft_in_sales_invoices(sales_order_name, zusatzgeschaft):
    sales_invoices = frappe.get_all("Sales Invoice", filters={"sales_order": sales_order_name})

    for sales_invoice in sales_invoices:
        doc = frappe.get_doc("Sales Invoice", sales_invoice.name)
        doc.zusatzgeschaft = zusatzgeschaft 
        doc.save(ignore_permissions=True)

    return "Zusatzgeschaft updated in Sales Invoices."

@frappe.whitelist()
def validate_customer(customer):
    valdiation = frappe.db.get_value("Customer", customer, "blocked_customer")
    return valdiation
    
@frappe.whitelist()
def get_lead_source(customer):
    lead_source = frappe.db.sql("""
                                SELECT
                                    `tabLead`.`source`
                                FROM
                                    `tabLead`
                                LEFT JOIN
                                    `tabCustomer` ON `tabCustomer`.`lead_name` = `tabLead`.`name`
                                WHERE
                                    `tabCustomer`.`name` = '{cust}'""".format(cust=customer), as_dict=True)
                                    
    if len(lead_source) > 0:
        return lead_source[0].get('source')
    else:
        return None
    
@frappe.whitelist()
def close_so_position(parent_doctype, trans_items, parent_doctype_name):
    frappe.log_error(trans_items, "trans_items")
    update_child_qty_rate(parent_doctype, trans_items, parent_doctype_name)
    
    item = json.loads(trans_items)
    sales_order_doc = frappe.get_doc("Sales Order", parent_doctype_name)
    sales_order_line = item[0].get('idx') - 1
    
    if not sales_order_doc.get('with_closed_position'):
        sales_order_doc.with_closed_position = 1
        
    if not sales_order_doc.items[sales_order_line].get('closed_position'):
        sales_order_doc.items[sales_order_line].closed_position = 1
        
    sales_order_doc.save()
    return
