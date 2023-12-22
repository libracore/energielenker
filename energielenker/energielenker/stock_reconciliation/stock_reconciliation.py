# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_valuation_rate(stock_rec):
    ba = frappe.get_doc("Stock Reconciliation", stock_rec)
    default_currency = frappe.db.get_default("currency")
    for item in ba.items:
        if not item.valuation_rate:
            # try if there is a buying price list in default currency
            buying_rate = frappe.db.get_value("Item Price", {"item_code": item.item_code,
                "buying": 1, "currency": default_currency}, "price_list_rate")
            if buying_rate:
                item.valuation_rate = buying_rate
            else:
                # get valuation rate from Item
                valuation_rate = frappe.get_value('Item', item.item_code, 'valuation_rate')
                if valuation_rate:
                    item.valuation_rate = frappe.get_value('Item', item.item_code, 'valuation_rate')
    ba.save()
    return

@frappe.whitelist()
def get_single_valuation_rate(item):
    default_currency = frappe.db.get_default("currency")
    valuation_rate = 0
    # try if there is a buying price list in default currency
    buying_rate = frappe.db.get_value("Item Price", {"item_code": item,
        "buying": 1, "currency": default_currency}, "price_list_rate")
    if buying_rate:
        valuation_rate = buying_rate
    else:
        # get valuation rate from Item
        _valuation_rate = frappe.get_value('Item', item, 'valuation_rate')
        if _valuation_rate:
            valuation_rate = frappe.get_value('Item', item, 'valuation_rate')
    return valuation_rate