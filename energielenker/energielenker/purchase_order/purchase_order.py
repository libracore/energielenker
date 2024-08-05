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

def autoclose_purchase_order():
    affected_supplier = frappe.db.get_value("energielenker Settings", "energielenker Settings", "supplier_to_autoclose")
    
    autoclosed_documents = []
    
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
                                `status` IN ("To Receive and Bill", "To Receive", "To Bill")""".format(supplier=affected_supplier), as_dict=True)
                                
    for order in orders:
        open_lizenzgutscheine = frappe.db.sql("""
                                                SELECT
                                                    `name`
                                                FROM
                                                    `tabLizenzgutschein`
                                                WHERE
                                                    `purchase_order` = '{po}'
                                                AND
                                                    `status` = 'Gültig'""".format(po=order.get('name')), as_dict=True)
        
        if not len(open_lizenzgutscheine) > 0:
            po_doc = frappe.get_doc("Purchase Order", order.get('name'))
            po_doc.set_status(update=True, status="Closed")
            po_doc.save()
            frappe.db.commit()
            autoclosed_documents.append(order.get('name'))
            
    frappe.log_error(autoclosed_documents, "Closed Purchase Orders")
            
    return
