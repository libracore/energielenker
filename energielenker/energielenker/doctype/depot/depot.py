# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.communication.email import make as make_email
from frappe.utils import cint

class Depot(Document):
    pass

@frappe.whitelist()
def get_items_html(depot, event):
    warehouse = frappe.db.get_value("Depot", depot,"to_warehouse")
    sales_order = frappe.db.get_value("Depot", depot,"sales_order")
    data = frappe.db.sql("""SELECT 
                                `transactions`.`item_code`,
                                `transactions`.`item_name`,
                                `transactions`.`uom`,
                                SUM(`transactions`.`qty`) AS `balance_qty`
                            FROM (
                                SELECT 
                                    `item_code`,
                                    `item_name`,
                                    `uom`,
                                    SUM(IF (`tabStock Entry Detail`.`s_warehouse` = "{warehouse}", (-1) * `tabStock Entry Detail`.`qty`, `tabStock Entry Detail`.`qty`)) AS `qty`
                                FROM `tabStock Entry Detail`
                                LEFT JOIN `tabStock Entry` ON `tabStock Entry`.`name` = `tabStock Entry Detail`.`parent`
                                WHERE `tabStock Entry`.`source_depot` = "{depot}"
                                  AND `tabStock Entry`.`docstatus` = 1
                                GROUP BY `tabStock Entry Detail`.`item_code`
                                UNION SELECT
                                    `item_code`,
                                    `item_name`,
                                    `uom`,
                                    SUM((-1) * `qty`)
                                FROM `tabDelivery Note Item`
                                WHERE `tabDelivery Note Item`.`source_depot` = "{depot}"
                                  AND `tabDelivery Note Item`.`docstatus` = 1
                                GROUP BY `tabDelivery Note Item`.`item_code`
                            ) AS `transactions`
                            GROUP BY `transactions`.`item_code`;""".format(depot=depot, warehouse=warehouse), as_dict=True)
                            
    if event == "depot":
        items = {
            'items': data
        }
        
        html = frappe.render_template("energielenker/energielenker/doctype/depot/depot_items.html", items)
        
        return html
    elif event == "delivery_note":
        return data, depot, sales_order, warehouse
    else:
        return data

@frappe.whitelist()
def book_back_items(depot, warehouse, project):
    items = get_items_html(depot, "book_back")
    entry = False
    for item in items:
        if item.get('balance_qty') > 0:
            entry = True
            break
    if entry:
        stock_entry = make_back_stock_entry(depot, items, warehouse, project)
        return stock_entry
    else:
        return

def make_back_stock_entry(depot, items, warehouse, project):
    material_transfer_items = []
    for item in items:
        if item.get('balance_qty') > 0:
            material_transfer_items.append({
                'item_code': item.get('item_code'),
                'qty': item.get('balance_qty'),
                'uom': item.get('uom'),
                't_warehouse': frappe.db.get_value("Item", item.get('item_code'), "default_warehouse_readonly")
            })
    material_transfer = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": 'Material Transfer',
        "from_warehouse": warehouse,
        "items": material_transfer_items,
        "project": project,
        "source_depot": depot
    }).insert()

    return material_transfer.name

@frappe.whitelist()
def write_off_items(depot, warehouse, project):
    items = get_items_html(depot, "write_off")
    entry = False
    for item in items:
        if item.get('balance_qty') > 0:
            entry = True
            break
    if entry:
        stock_entry = make_off_stock_entry(depot, items, warehouse, project)
        return stock_entry
    else:
        return

def make_off_stock_entry(depot, items, warehouse, project):
    material_transfer_items = []
    for item in items:
        if item.get('balance_qty') > 0:
            material_transfer_items.append({
                'item_code': item.get('item_code'),
                'qty': item.get('balance_qty'),
                'uom': item.get('uom')
            })
    material_transfer = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": 'Material Issue',
        "from_warehouse": warehouse,
        "items": material_transfer_items,
        "project": project,
        "source_depot": depot
    }).insert()

    return material_transfer.name
    
@frappe.whitelist()
def set_open_depots(sales_order, project):
    #get amount of open depots for this sales order
    sales_orders = frappe.db.sql("""
                                    SELECT COUNT(*) AS `quantity`
                                    FROM `tabDepot`
                                    WHERE `sales_order` = '{so}'
                                    AND `status` = 'Open'""".format(so=sales_order), as_dict=True)
    #get and update sales order
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    sales_order_doc.open_depots = sales_orders[0].quantity
    sales_order_doc.save()
    
    #get amount of open depots for this project
    if project:
        projects = frappe.db.sql("""
                                        SELECT COUNT(*) AS `quantity`
                                        FROM `tabDepot`
                                        WHERE `project` = '{project}'
                                        AND `status` = 'Open'""".format(project=project), as_dict=True)
        #get and update project
        project_doc = frappe.get_doc("Project", project)
        project_doc.open_depots = projects[0].quantity
        project_doc.save()
    
    return
    
@frappe.whitelist()
def create_delivery_note(depot, warehouse, sales_order, project):
    #get sales order, contact and items
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    items = get_items_html(depot, "dn_button")
    if sales_order_doc.shipping_contact:
        contact = sales_order_doc.shipping_contact
        contact_display = sales_order_doc.shipping_contact_display
    elif sales_order_doc.contact_person_two:
        contact = sales_order_doc.contact_person_two
        contact_display = sales_order_doc.contact_display_two
    else:
        contact = ""
        contact_display = ""
    #create new Delivery Note
    new_dn = frappe.get_doc({
        'doctype': 'Delivery Note',
        'customer': sales_order_doc.customer,
        'auftrags_projektb': sales_order_doc.auftrags_projektb,
        'ansprechpartner': sales_order_doc.ansprechpartner,
        'k_ansprechperson': sales_order_doc.k_ansprechperson,
        'po_no': sales_order_doc.po_no,
        'taxes_and_charges': sales_order_doc.taxes_and_charges,
        'taxes': sales_order_doc.taxes,
        'shipping_address_name': sales_order_doc.shipping_address_name,
        'contact_person': contact,
        'contact_display': contact_display,
        'project': project,
        'po_date': sales_order_doc.po_date
        })
    
    items_without_so = []
    
    for item in items:
        if item.get('balance_qty') > 0:
            so_detail = get_so_detail(item.get('item_code'), sales_order)
            if not so_detail:
                so_detail = ""
                items_without_so.append(item.get('item_code'))
            entry = {
                'reference_doctype': 'Delivery Note Item',
                'item_code': item.get('item_code'),
                'qty': item.get('balance_qty'),
                'uom': item.get('uom'),
                'against_sales_order': sales_order,
                'so_detail': so_detail,
                'source_depot': depot,
                'warehouse': warehouse
            }
            new_dn.append('items', entry)
    
    new_dn = new_dn.insert()
    
    #get name of new Delivery Note and return it
    delivery_note = new_dn.name
    
    if len(items_without_so) > 0:
        message = "Achtung, folgende Artikel befinden sich nicht in {0}:".format(sales_order)
        for item_without_so in items_without_so:
            message += "<br>- {0}".format(item_without_so)
    else:
        message = False
    
    return delivery_note, message

def get_so_detail(dn_item, sales_order):
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    for so_item in sales_order_doc.items:
        if so_item.get('item_code') == dn_item:
            if so_item.get('delivered_qty') < so_item.get('qty'):
                return so_item.get('name')
    return False

def daily_depot_check():
    #check settings
    reminder_active = frappe.db.get_value("energielenker Settings", "energielenker Settings", "send_depot_reminder")
    if cint(reminder_active) == 0:
        return
    
    #find all open depots with closed/completed/cancelled Sales Order
    open_depots = frappe.db.sql("""
                                SELECT
                                    `depot`.`name` AS `depot_name`,
                                    `so`.`name` AS `so_name`
                                FROM
                                    `tabDepot` AS `depot`
                                LEFT JOIN
                                    `tabSales Order` AS `so` ON `depot`.`sales_order` = `so`.`name`
                                WHERE
                                    `so`.`status` IN ("Closed", "Cancelled", "Completed")
                                AND
                                    `depot`.`status` IN ("Open")""", as_dict=True)
    
    #If depots were found, create html for e-mail
    if len(open_depots) > 0:
        html = "Guten Morgen Herr Ruhkamp,<br><br>folgende Kommissionen sind offen, haben aber einen geschlossenen Kundenauftrag:<br>"
        for open_depot in open_depots:
            html += "<br>- {0} / {1}".format(open_depot.get('depot_name'), open_depot.get('so_name'))
        
        make_email(
        recipients= ["ruhkamp@energielenker.de", "pham@energielenker.de"],
        sender= "Administrator",
        subject="Offene Kommissionen mit geschlossenen Kundenaufträgen",
        content=html,
        send_email=True)

    return
