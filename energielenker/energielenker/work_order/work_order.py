# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_bom_values(bom):
    depot = frappe.db.get_value("energielenker Settings", "energielenker Settings", "depot_warehouse")
    data = frappe.db.sql("""SELECT
                    `tabBOM`.`item`,
                    `tabBOM`.`sales_order`,
                    `tabBOM`.`project`,
                    `tabBOM`.`item_so_detail`,
                    `tabItem`.`default_warehouse_readonly`,
                    "{depot}" AS depot_warehouse
                FROM `tabBOM`
                LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBOM`.`item`
                WHERE `tabBOM`.`name` = '{bom}'""".format(bom=bom, depot=depot), as_dict=True)
                
    
    return data
