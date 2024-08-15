# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import json

def validate_navision_of_items(sales_invoice, event):
    navision_deviation = ''
    for item in sales_invoice.items:
        try:
            item_navision = frappe.db.sql("""SELECT `navision_kontonummer` FROM `tabItem Default` WHERE `parent` = '{item}' AND `company` = '{company}'""".format(item=item.item_code, company=sales_invoice.company), as_dict=True)[0].navision_kontonummer
        except:
            item_navision = ''
        item.navision_kontonummer = item_navision
        if item_navision and item_navision != sales_invoice.navision_kontonummer:
            navision_deviation += str(item.idx) + "<br>"
    sales_invoice.navision_deviation = navision_deviation
    return

@frappe.whitelist()
def get_vat_template(customer):
    template = None
    territory = frappe.db.get_value("Customer", customer, "territory")

    if territory in ("Deutschland", "Nord", "Ost", "West", "Süd"):
        template = frappe.db.get_value("Sales Taxes and Charges Template", {"is_default": 1}, "name")
    else:
        data = frappe.db.sql("""
                                    SELECT
                                        `tabSales Taxes and Charges Template`.`name`
                                    FROM
                                        `tabSales Taxes and Charges Template`
                                    LEFT JOIN
                                        `tabSales Taxes and Charges` ON `tabSales Taxes and Charges`.`parent` = `tabSales Taxes and Charges Template`.`name`
                                    WHERE
                                        `tabSales Taxes and Charges`.`rate` = '0'
                                    AND
                                        `tabSales Taxes and Charges Template`.`disabled` = 0""", as_dict=True)
                                    
        if len(data) > 0:
            template = data[0].get('name')
            
    return template
