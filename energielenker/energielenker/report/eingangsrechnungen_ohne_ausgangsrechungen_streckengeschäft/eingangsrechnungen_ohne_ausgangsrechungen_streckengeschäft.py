# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe

def execute(filters=None):
	columns = get_columns()
    data = get_data()
	return columns, data
	

def get_columns():
    columns = [
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Sales Orders"), "fieldname": "sales_orders", "fieldtype": "Data", "width": 100}
    ]
    return columns
