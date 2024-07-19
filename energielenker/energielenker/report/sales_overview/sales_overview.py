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
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 400},
        {"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Int", "width": 100},
        {"label": _("Net amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Average"), "fieldname": "average", "fieldtype": "Currency", "width": 150}
    ]
    return columns

def get_data(filters):
    if filters.type == "Sold Items":
        #prepare data
        data = []
        
        #get all items to be considered
        required_items = frappe.db.sql("""
                                        SELECT
                                            `item_code`,
                                            `item_name`,
                                            `lot_calculation`
                                        FROM
                                            `tabSales Overview Item`
                                        ORDER BY
                                            `item_code`""", as_dict=True)
        
        #get information for every item to consider and append it to data
        if len(required_items) > 0:
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
                    if len(details) > 0:
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
                                    'net_amount' : total_amount,
                                    'average' : total_amount / total_quantity
                                }
                                
                        data.append(entry)
                #prepare data for items where not lot calculation is required
                else:
                    #get all entries
                    details = frappe.db.sql("""
                                            SELECT
                                                CONCAT(`item_code`, ' ', `item_name`) AS `description`,
                                                SUM(`qty`) AS `quantity`,
                                                SUM(`amount`) AS `net_amount`,
                                                SUM(`amount`) / SUM(`qty`) AS `average`
                                            FROM
                                                `tabSales Order Item`
                                            WHERE
                                                `item_code` = '{item}'
                                            AND
                                                `transaction_date` BETWEEN '{from_date}' AND '{to_date}'
                                            AND
                                                `docstatus` = 1
                                            GROUP BY
                                                `item_code`""".format(item=required_item.get('item_code'), from_date=filters.from_date, to_date=filters.to_date), as_dict=True)
                                                
                    #if there is an entry, append it to data. Else apennd it with qty and amount 0
                    if len(details) > 0:
                        data.append(details[0])
                    else:
                        description = required_item.get('item_code') + " " + required_item.get('item_name')
                        data.append({
                                        'description': description,
                                        'quantity': 0,
                                        'net_amount' : 0
                                    })
        
        #get amount of project with EZA-Regler
        projects = frappe.db.sql("""
                                SELECT
                                    `project_type` AS `description`,
                                    COUNT(`name`) AS `quantity`,
                                    SUM(`total_amount`) AS `net_amount`,
                                    SUM(`total_amount`) / COUNT(`name`) AS `average`
                                FROM
                                    `tabProject`
                                WHERE
                                    `project_type` = 'EZA-Regler (ehem. Netzregelung)'
                                AND
                                    `creation` BETWEEN '{from_date}' AND '{to_date}'
                                AND
                                    `status` != 'Cancelled'
                                GROUP BY
                                    `project_type`""".format(from_date=filters.from_date, to_date=filters.to_date), as_dict=True)
                                    
        data.append(projects[0])
        #get Data for Cost Center
    else:
        if filters.type == "Sales Invoice per Cost Center":
            tab = "Sales Invoice"
            doc_date = "posting_date"
        elif filters.type == "Sales Order per Cost Center":
            tab = "Sales Order"
            doc_date = "transaction_date"
            
        data = []
            
        lines = frappe.db.sql("""
                                SELECT
                                    `cost_center` AS `description`,
                                    COUNT(`name`) AS `quantity`,
                                    SUM(`total`) AS `net_amount`,
                                    SUM(`total`) / COUNT(`name`) AS `average`
                                FROM
                                    `tab{tab}`
                                WHERE
                                    `{doc_date}` BETWEEN '{from_date}' AND '{to_date}'
                                AND
                                    `docstatus` = 1
                                GROUP BY
                                    `cost_center`""".format(tab=tab, doc_date=doc_date, from_date=filters.from_date, to_date=filters.to_date), as_dict=True)
                                    
        for line in lines:
            line['indent'] = 0
            data.append(line)
            sub_lines = frappe.db.sql("""
                                        SELECT
                                            `customer` AS `description`,
                                            COUNT(`name`) AS `quantity`,
                                            SUM(`total`) AS `net_amount`,
                                            SUM(`total`) / COUNT(`name`) AS `average`
                                        FROM
                                            `tab{tab}`
                                        WHERE
                                            `{doc_date}` BETWEEN '{from_date}' AND '{to_date}'
                                        AND
                                            `cost_center` = '{cc}'
                                        AND
                                            `docstatus` = 1
                                        GROUP BY
                                            `customer`
                                        ORDER BY
                                            `net_amount` DESC""".format(tab=tab, doc_date=doc_date, from_date=filters.from_date, to_date=filters.to_date, cc=line.get('description').replace("'", "''")), as_dict=True)
            
            for sub_line in sub_lines:
                sub_line['indent'] = 1
                data.append(sub_line)
    
    return data
