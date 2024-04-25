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


@frappe.whitelist() 
def get_email_recipient_and_message(contact):
    data = frappe.db.sql("""SELECT
                            `email_id`
                            FROM `tabContact Email`
                            WHERE `parent` = '{contact}'
                            ORDER BY `is_primary` DESC""".format(contact=contact), as_dict=True)
    recipient = ""
    if len(data) > 0:
        if data[0].email_id:
            recipient = data[0].email_id
    
    html = "HALLO MASCHINE"
    
    # ~ template = frappe.db.get_value("emh settings", "emh settings", "invoice_email_template")

    # ~ html = frappe.db.get_value("Email Template", template, "response")
    
    return {
        'recipient': recipient,
        'message': html
        }
