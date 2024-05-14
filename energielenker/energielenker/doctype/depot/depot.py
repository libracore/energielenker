# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

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
        return data, depot, sales_order
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
