# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import json
from frappe.utils.data import getdate
from erpnext.controllers.accounts_controller import update_child_qty_rate
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

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

@frappe.whitelist()
def check_default_warehouses(doc):
    doc = json.loads(doc)
    
    message = ""
    for item in doc['items']:
        default_warehouse = frappe.get_value("Item", item.get('item_code'), "default_warehouse_readonly")
        if default_warehouse and not item.get('alternative_position') and item.get('warehouse') != default_warehouse:
            message += "{0} (Position {1})<br>".format(item.get('item_code'), item.get('idx'))
            
    if message:
        message = "Folgende Artikel haben aktuell nicht das Standardlager:<br><br>{0}".format(message)
        return message
    else:
        return None

@frappe.whitelist()
def create_overbilling_invoice(doc, cdt, cdn):
    doc = json.loads(doc)
    
    #Create Invoice from Sales Order, delete all Items and add specific Item
    invoice = make_sales_invoice(doc.get('name'))
    
    invoice.items.clear()
    
    for item in doc.get('items'):
        if item.get('name') == cdn:
            invoice.append("items", {
                                'reference_doctype': "Sales Invoice Item",
                                'item_code': item.get('item_code'),
                                'item_name': item.get('item_name'),
                                'qty': item.get('qty'),
                                'typ': item.get('typ'),
                                'textposition': item.get('textposition'),
                                'alternative_position': item.get('alternative_position'),
                                'interne_position': item.get('interne_position'),
                                'kalkulationssumme_interner_positionen': item.get('kalkulationssumme_interner_positionen'),
                                'is_supplement': item.get('is_supplement'),
                                'close_position': item.get('close_position'),
                                'artikel_nach_aufwand': item.get('artikel_nach_aufwand'),
                                'description': item.get('description'),
                                'remarks': item.get('remarks'),
                                'uom': item.get('uom'),
                                'delivered_by_supplier': item.get('delivered_by_supplier'),
                                'warehouse': item.get('warehouse'),
                                'sales_order': doc.get('name'),
                                'so_detail': item.get('name'),
                            })
    
    invoice.save()
    frappe.db.commit()
    
    #Create and remove Link to new Invoice
    link = "/desk#Form/Sales Invoice/{0}".format(invoice.get('name'))
    
    return link

@frappe.whitelist()
def check_service_project_tasks(doc):
    doc = json.loads(doc)
    
    #Get all used Issues for this Project
    project_tasks = frappe.db.sql("""
                                    SELECT
                                        `tabSales Order Item`.`name`,
                                        `tabSales Order Item`.`task`
                                    FROM
                                        `tabSales Order Item`
                                    LEFT JOIN 
                                        `tabSales Order` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                                    WHERE
                                        `tabSales Order`.`project_clone` = '{project}'
                                    AND
                                        `tabSales Order`.`name` != '{sales_order}'
                                    AND
                                        `tabSales Order`.`docstatus` != 2;""".format(project=doc.get('project_clone'), sales_order=doc.get('name')), as_dict=True)
    
    for item in doc.get('items'):
        #If UOM is "Std" - Check if Task is set an Unique
        if item.get('uom') == "Std":
            if not item.get('task'):
                return "Bitte Aufgabe in Zeile {0} angeben".format(item.get('idx'))
            else:
                #Check if Task is set in another Sales Order
                for task in project_tasks:
                    if task.get('name') != item.get('name') and item.get('task') == task.get('task'):
                        return "Aufgabe {0} (Zeile: {1}) wird in diesem Projekt bereits verwendet".format(task.get('task'), item.get('idx'))
                #Check if Task is set in another Item of the Same Sales Order
                for check_item in doc.get('items'):
                    if check_item.get('name') != item.get('name') and item.get('task') == check_item.get('task'):
                        return "Aufgabe {0} (Zeile: {1}) wird in diesem Projekt bereits verwendet".format(check_item.get('task'), item.get('idx'))
    
    return False

@frappe.whitelist()
def get_revenue_type(item_code, revenue_group=None):
    item_doc = frappe.get_doc("Item", item_code)
    
    #Return Revenue Type from Item, if avalaiable
    if item_doc.get('revenue_type'):
        return item_doc.get('revenue_type')
    
    #Return nothing, if no revenue_group is given
    if not revenue_group:
        return None
    
    #Else get right Revenue Type
    for_hardware = 0
    for_support = 0
    if item_doc.get('is_support'):
        for_support = 1
    else:
        for_hardware = 1
    
    revenue_groups = frappe.get_all("Revenue Type", filters={'group': revenue_group, 'for_hardware': for_hardware, 'for_support': for_support}, fields=["name"])
    
    if len(revenue_groups) > 0:
        return revenue_groups[0].get('name')
    else:
        return None
    
    
