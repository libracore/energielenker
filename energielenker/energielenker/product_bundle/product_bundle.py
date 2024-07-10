# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def mark_items(parent_item, items):
    items = json.loads(items)
    
    for item in items:
        item_doc = frappe.get_doc("Item", item.get('item_code'))
        item_doc.part_of_product_bundle = parent_item
        item_doc.save()
    return
