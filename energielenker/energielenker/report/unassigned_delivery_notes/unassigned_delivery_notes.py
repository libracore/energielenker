# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    columns = [
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150}
    ]
    return columns

def get_data():
    delivery_notes = frappe.db.sql("""
                                    SELECT
                                        `name` AS `delivery_note`,
                                        `customer`
                                    FROM
                                        `tabDelivery Note`
                                    WHERE
                                        `docstatus` = 1
                                    AND
                                        `delivery_note_assigned` = 0;""", as_dict=True)
    
    return delivery_notes
