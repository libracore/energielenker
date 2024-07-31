# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_default_cost_center(user):
    fallback = True
    employee_default_cost_center = frappe.db.sql("""SELECT `default_cost_center` FROM `tabEmployee` WHERE `user_id` = '{0}'""".format(user), as_dict=True)
    frappe.log_error("{0}".format(employee_default_cost_center), "...")
    if len(employee_default_cost_center) > 0:
        if employee_default_cost_center[0].default_cost_center:
            fallback = False
            return employee_default_cost_center[0].default_cost_center
    if fallback:
        return frappe.db.get_value("energielenker Settings", "energielenker Settings", "default_cost_center")

def autoclose_purchase_order()
    affected_supplier = frappe.db.get_value("energielenker Settings", "energielenker Settings", "supplier_to_autoclose")
    
    orders = frappe.db.sql("""
                            SELECT
                                `name`
                            FROM
                                `tabPurchase Order`
                            WHERE
                                `supplier` = '{supplier}'
                            AND
                                `docstatus` = 1
                            AND
                                `status` NOT IN ("Completed", "Closed", "On Hold")"""
