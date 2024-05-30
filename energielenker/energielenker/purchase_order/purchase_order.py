# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
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

@frappe.whitelist()
def get_material_request_items(supplier):
    items = frappe.db.sql("""
                        SELECT
                            `tabMaterial Request Item`.`item_code`,
                            `tabMaterial Request Item`.`parent` AS `material_request`,
                            `tabMaterial Request Item`.`qty` - `ordered_qty` AS `quantity`
                        FROM
                            `tabMaterial Request Item`
                        LEFT JOIN
                            `tabMaterial Request` ON `tabMaterial Request Item`.`parent` = `tabMaterial Request`.`name`
                        WHERE
                            `tabMaterial Request`.`material_request_type` = 'Purchase'
                        AND
                            `tabMaterial Request`.`docstatus` = 1
                        AND
                            (`tabMaterial Request`.`status` = 'Pending' OR `tabMaterial Request`.`status` = 'Partially Ordered')
                        AND
                            (SELECT `default_supplier` FROM `tabItem Default` WHERE `tabItem Default`.`parent` = `tabMaterial Request Item`.`item_code`) = '{supplier}'""".format(supplier=supplier), as_dict=True)
                            
    frappe.log_error(items, "items")
                        
    return items
