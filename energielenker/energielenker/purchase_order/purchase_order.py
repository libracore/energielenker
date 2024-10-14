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
    #close all orders from specific supplier
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
            
    #close order with 100% delivery and no actions sice 3 Months
    open_orders = frappe.db.sql("""
                            SELECT
                                `name`,
                                `status`,
                                `per_received`,
                                `per_billed`,
                                `modified`
                            FROM
                                `tabPurchase Order`
                            WHERE
                                `docstatus` = 1
                            AND
                                `status` IN ("To Receive and Bill", "To Receive", "To Bill")""", as_dict=True)
    closed_by_receiving = []
    closed_by_billed = []
    three_months_ago = add_months(getdate(), -3)
    for open_order in open_orders:
        if open_order.get('modified') < three_months_ago and open_order.get('per_received') > 99:
            po_doc = frappe.get_doc("Purchase Order", open_order.get('name'))
            po_doc.set_status(update=True, status="Closed")
            po_doc.save()
            frappe.db.commit()
            closed_by_receiving.append(open_order.get('name'))
        elif open_order.get('per_billed') > 99.995 and open_order.get('status') == "To Bill":
            frappe.db.set_value("Purchase Order", open_order.get('name'), "status", "Completed")
            frappe.db.set_value("Purchase Order", open_order.get('name'), "per_billed", 100)
            frappe.db.commit()
            closed_by_billed.append(open_order.get('name'))
    frappe.log_error(autoclosed_documents, "Closed Purchase Orders")
    frappe.log_error(closed_by_receiving, "Closed Purchase Orders")
    frappe.log_error(closed_by_billed, "Closed Purchase Orders")
    return
    
def test_something():
    # ~ frappe.db.set_value("Purchase Order", "BE0002232", "status", "To Bill")
    # ~ frappe.db.set_value("Purchase Order", "BE0002232", "per_billed", 99)
    po_doc = frappe.get_doc("Purchase Order", "BE0002232")
    po_doc.set_status(update=True, status="Closed")
    frappe.db.commit()
    return
