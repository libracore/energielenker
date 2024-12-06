# Copyright (c) 2025, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
    
def get_columns():
    columns = [
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Creation"), "fieldname": "creation", "fieldtype": "Date", "width": 100}
    ]
    
    ibn_remote_items = get_ibn_remote_items()
    
    for item in ibn_remote_items:
        columns.append({"label": _("{0} - {1}".format(item.get('item_code'), item.get('item_name'))), "fieldname": item.get('item_code').replace("-", "_"), "fieldtype": "Check", "width": 120})
    
    return columns
    
def get_data(filters):
    #get related items
    ibn_remote_items = get_ibn_remote_items()
    condition = ''
    for index, item in enumerate(ibn_remote_items):
        if index == 0:
            condition += '"{0}"'.format(item.get('item_code'))
        else:
            condition += ', "{0}"'.format(item.get('item_code'))
    #get data
    data = frappe.db.sql("""SELECT DISTINCT
                                `tabSales Order`.`name` as `sales_order`,
                                `tabSales Order`.`customer` AS `customer`,
                                `tabSales Order`.`creation` AS `creation`
                            FROM
                                `tabSales Order`
                            LEFT JOIN
                                `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                            WHERE
                                `tabSales Order Item`.`item_code` IN ({items})
                            AND
                                `tabSales Order`.`customer` = 'Stadt Freiburg'
                            AND
                                `tabSales Order`.`docstatus` = 1""".format(items=condition), as_dict=True)
   
    frappe.log_error(data, "data")
   
    return data

def get_ibn_remote_items():
    items = frappe.db.sql("""
                            SELECT
                                `item_code`,
                                `item_name`
                            FROM
                                `tabIBN remote Items`""", as_dict=True)
                                
    return items
