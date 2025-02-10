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

@frappe.whitelist()
def set_has_work_order_in_sales_order(doc, method):
    try:
        frappe.db.sql("""UPDATE `tabSales Order` SET `has_work_order` = 1 WHERE `name` = '{sales_order}'""".format(sales_order=doc.sales_order))
    except Exception as e:
        frappe.log_error(str(e), "set_has_work_order_in_sales_order")
    return

@frappe.whitelist()
def unset_has_work_order_in_sales_order(doc, method):
    try:
        #first check if there are any other uncancelled work orders for this sales order
        work_orders = frappe.get_all("Work Order", filters={"sales_order": doc.sales_order, "docstatus": 1}, fields=["name"])
        if len(work_orders) > 0:
            return
        
        frappe.db.sql("""UPDATE `tabSales Order` SET `has_work_order` = 0 WHERE `name` = '{sales_order}'""".format(sales_order=doc.sales_order))
    except Exception as e:
        frappe.log_error(str(e), "unset_has_work_order_in_sales_order")
    return