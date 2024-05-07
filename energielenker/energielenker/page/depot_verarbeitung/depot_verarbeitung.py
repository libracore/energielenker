# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def make_material_transfer(depot, items):
    depot = frappe.get_doc("Depot", depot)
    items = json.loads(items)
    material_transfer_items = []
    for key in items:
        
        material_transfer_items.append({
            'item_code': key,
            'qty': items[key],
            'uom': 'Stück',
            's_warehouse': frappe.db.get_value("Item", key, "default_warehouse_readonly")
        })
    material_transfer = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": 'Material Transfer',
        "to_warehouse": depot.to_warehouse,
        "items": material_transfer_items,
        "project": depot.project,
        "source_depot": depot.name
    }).insert()

    return material_transfer.name
