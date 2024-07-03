# Copyright (c) 2013, libracore and contributors
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
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Int", "width": 100},
        {"label": _("Net amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 150}
    ]
    return columns

def get_data(filters):
    #prepare data
    data = []
    
    #get all items to be considered
    required_items = frappe.db.sql("""
                                    SELECT
                                        `item_code`,
                                        `lot_calculation`
                                    FROM
                                        `tabSales Overview Item`""", as_dict=True)
    
    #get information for every item to consider and append it to data
    for required_item in required_items:
        #check if there is a lot calculation is required
        if required_item.get('lot_calculation') == 1:
            #get all entries
            details = frappe.db.sql("""
                                    SELECT
                                        `item_code`,
                                        `item_name`,
                                        `uom`,
                                        `qty`,
                                        `amount`
                                        
                                    FROM
                                        `tabSales Order Item`
                                    WHERE
                                        `item_code` = '{item}'
                                    AND
                                        `transaction_date` BETWEEN '{from_date}' AND '{to_date}'
                                    AND
                                        `docstatus` = 1""".format(item=required_item.get('item_code'), from_date=filters.from_date, to_date=filters.to_date), as_dict=True)
            
            #loop through items and calculate quantity
            remove_sequence = "er-Los"
            total_quantity = 0
            total_amount = 0
            for detail in details:
                #If uom is piece, just add the quantity to the total
                if detail.get('uom') == "Stück":
                    total_quantity += detail.get('qty')
                    total_amount += detail.get('amount')
                #If there is a lot, remove the "er-los", convert to int, multiply with qty and add it to the total
                else:
                    quantity = int(detail.get('uom')[:-len(remove_sequence)]) * detail.get('qty')
                    total_quantity += quantity
                    total_amount += detail.get('amount')
            
            #create entry and append it to data
            description = detail.get('item_code') + " " + detail.get('item_name')
            entry = {
                        'description': description,
                        'quantity': total_quantity,
                        'net_amount' : total_amount
                    }
                    
            data.append(entry)
                
    return data
