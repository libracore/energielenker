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
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("User"), "fieldname": "owner", "fieldtype": "Data", "width": 150}
    ]
    return columns

def get_data():
    delivery_notes = frappe.db.sql("""
                                    SELECT
                                        `tabDelivery Note`.`name` AS `delivery_note`,
                                        `tabDelivery Note`.`customer` AS `customer`,
                                        `tabDelivery Note`.`owner` AS `owner`
                                    FROM
                                        `tabDelivery Note`
                                    LEFT JOIN
                                        `tabDelivery Note Item` ON `tabDelivery Note Item`.`parent` = `tabDelivery Note`.`name`
                                    LEFT JOIN
                                        `tabDelivery Note Assignment User` ON `tabDelivery Note Assignment User`.`user` = `tabDelivery Note`.`owner`
                                    LEFT JOIN
                                        `tabDelivery Note Assignment Item` ON `tabDelivery Note Assignment Item`.`item_code` = `tabDelivery Note Item`.`item_code`
                                    WHERE
                                        `tabDelivery Note`.`docstatus` = 1
                                    AND
                                        `tabDelivery Note`.`delivery_note_assigned` = 0
                                    AND
                                        `tabDelivery Note Assignment User`.`user` IS NOT NULL
                                    AND
                                        `tabDelivery Note Assignment Item`.`item_code` IS NULL
                                    GROUP BY
                                        `delivery_note`;""", as_dict=True)
    
    return delivery_notes
