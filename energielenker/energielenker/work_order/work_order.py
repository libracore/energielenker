# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_values(bom):
    data = frappe.db.sql("""SELECT
                    `tabBOM`.`item`,
                    `tabBOM`.`sales_order`,
                    `tabBOM`.`project`,
                    `tabItem`.`default_warehouse_readonly`
                FROM `tabBOM`
                LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBOM`.`item`
                WHERE `tabBOM`.`name` = '{bom}'""".format(bom=bom), as_dict=True)
                
    frappe.log_error(data, "data")
    
    return data
