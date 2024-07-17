# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def mark_items(parent_item, items):
    #translate string to json
    items = json.loads(items)
    
    #check if subitems are marked, and mark it if it is not
    for item in items:
        item_doc = frappe.get_doc("Item", item.get('item_code'))
        
        entry_exists = False
        for entry in item_doc.product_bundle:
            if entry.item_code == parent_item:
                entry_exists = True
                break
        
        if not entry_exists:
            item_doc.append("product_bundle", {'item_code': parent_item})
            
        item_doc.save()
        frappe.db.commit()
        
    #mark parent item if needed
    parent_item_doc = frappe.get_doc("Item", parent_item)
    check = parent_item_doc.is_product_bundle
    if check == 0:
        parent_item_doc.is_product_bundle = 1
        parent_item_doc.save()
        frappe.db.commit()
    return
    
def delete_redord(self, event):
    parent_item_doc = frappe.get_doc("Item", self.new_item_code)
    parent_item_doc.is_product_bundle = 0
    parent_item_doc.save()
    frappe.db.commit()
    
    for item in self.items:
        remove_mark(self.new_item_code, item.item_code)
    return
    
@frappe.whitelist()
def remove_mark(parent_item, item=None):
    if item:
        item_doc = frappe.get_doc("Item", item)
        item_doc.product_bundle = [entry for entry in item_doc.product_bundle if entry.item_code != parent_item]
        item_doc.save()
        frappe.db.commit()
    return
