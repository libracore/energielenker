# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import json
from frappe.utils.data import getdate

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
def check_for_webshop_points(doc, event="submit"):
    sales_order_doc = json.loads(doc)
    validation = True
    #get points item
    points_item = frappe.db.get_value("Webshop Settings", "Webshop Settings", "so_item")
    
    #check if there are webshop points in items
    qty = 0
    
    for item in sales_order_doc['items']:
        if item.get('item_code') == points_item:
            qty = item.get('qty')
            validation = False
            
    
    #return nothing, if there are no points in sales order
    if validation:
        return validation
    
    #check if customer has account
    try:
        account_doc = frappe.get_doc("Charging Point Key Account", sales_order_doc.get('customer'))
        validation = True
    except:
        if event == "cancel":
            frappe.throw("Konto für diesen Kunden fehlt!")
        return validation

    #if there are points and an account, add/remove points to account
    account_doc.avaliable_points += qty if event == "submit" else qty * -1
    #create log entry
    log_entry = {
        'date': getdate(),
        'activity': sales_order_doc['name'],
        'amount': qty if event == "submit" else qty * -1,
        'user': sales_order_doc['owner']
    }
    account_doc.append('past_activities', log_entry)
    #save document
    account_doc.save()
    frappe.db.commit()
    
    return validation
    
@frappe.whitelist()
def create_delivery_note(sales_order_name):
    #get today
    today = getdate()
    
    #get Sales Order and check for webshop points
    dn_creation = False
    sales_order_doc = frappe.get_doc('Sales Order', sales_order_name)
    points_item = frappe.db.get_value("Webshop Settings", "Webshop Settings", "so_item")
    for item in sales_order_doc.items:
        if item.get('item_code') == points_item:
            dn_creation = True
        
    if not dn_creation:
        return
    else:
        #create new Delivery Note
        new_dn = frappe.get_doc({
            'doctype': 'Delivery Note',
            'customer': sales_order_doc.get('customer'),
            'zur_berechnung_freigegeben': 1,
            'po_no': sales_order_doc.get('po_no'),
            'ansprechpartner': sales_order_doc.get('ansprechpartner'),
            'contact_person': "",
            'contact_display': ""
            })
        
        if not new_dn.shipping_address_name:
            new_dn.shipping_address_name = sales_order_doc.get('customer_address')
        
        for item in sales_order_doc.items:
            entry = {
                'reference_doctype': 'Delivery Note Item',
                'item_code': item.item_code,
                'qty': item.qty,
                'uom': item.uom,
                'against_sales_order': sales_order_name,
                'so_detail': item.name,
                'vk_wert': item.amount
            }
            new_dn.append('items', entry)
        
        new_dn = new_dn.insert(ignore_permissions=True)
        new_dn.submit()
        
        return

@frappe.whitelist()
def validate_customer(customer):
    valdiation = frappe.db.get_value("Customer", customer, "blocked_customer")
    return valdiation
    
