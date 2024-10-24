# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
import re
from erpnext.stock.reorder_item import reorder_item

def get_plz_gebiet(self, event):
    if not self.gebiet and self.customer_address:
        _gebiet = frappe.db.get_value("Address", self.customer_address, "plz")
        if _gebiet:
            gebiet = re.findall(r"[0-9]{2,}", _gebiet)
            if len(gebiet) > 0:
                self.gebiet = gebiet[0][:2]
    return

@frappe.whitelist()
def reorder_item_wrapper():
    reorder_item()
    return

@frappe.whitelist()
def get_label_dimension_settings(label_printer):
    if frappe.db.exists("Label Printer", label_printer):
        dimension_settings = frappe.db.get_value("Label Printer", label_printer, 'dimension_settings')
        return dimension_settings
    else:
        return False

