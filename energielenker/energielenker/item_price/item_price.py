# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from erpnext.manufacturing.doctype.bom.bom import BOM

@frappe.whitelist()
def update_bom_item_cost(name, item_code, rate, rm_cost_as_per, price_list=None):
    # Update hidden previous_price_list_rate
    item_price = frappe.get_doc("Item Price", name)
    frappe.db.set(item_price, 'previous_price_list_rate', item_price.price_list_rate)
  
    # Basic filters
    filters = {
        'item_code': item_code,
        'rm_cost_as_per': rm_cost_as_per
    }

    # Add price_list filter if provided
    if price_list:
        filters['buying_price_list'] = price_list

    # Fetch BOMs containing the item and matching criteria
    boms = frappe.get_all('BOM', filters=filters, fields=['name'])

    # Update cost for each BOM
    for bom in boms:
        bom_doc = frappe.get_doc("BOM", bom.name)
        BOM.update_cost(bom_doc, rate)
    
