# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def validate_lagerfuehrung_of_items(purchase_invoice, event):
    for item in purchase_invoice.items:
        item.ist_lagergefuehrt = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
    return
