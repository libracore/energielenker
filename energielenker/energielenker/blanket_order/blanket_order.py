# Copyright (c) 2025, libracore AG and contributors
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def update_to_date(blanket_order, new_date):
    frappe.db.set_value("Blanket Order", blanket_order, "to_date", new_date)
    frappe.db.commit()
    return True

@frappe.whitelist()
def get_blanket_order_discount(doc):
    doc = json.loads(doc)
    discounts = []
    
    
    
    for item in doc["items"]:
        #Check for existing Blanket Order Discount with Customer and Item
        blanket_orders = frappe.db.sql("""
                                        SELECT
                                            `tabBlanket Order`.`name` AS `name`
                                        FROM
                                            `tabBlanket Order`
                                        LEFT JOIN
                                            `tabBlanket Order Discount` ON `tabBlanket Order Discount`.`parent` = `tabBlanket Order`.`name`
                                        WHERE
                                            `tabBlanket Order`.`customer` = %(customer)s
                                        AND
                                            `tabBlanket Order Discount`.`item_code` = %(item)s
                                        AND
                                            `tabBlanket Order`.`from_date` <= CURDATE()
                                        AND
                                            `tabBlanket Order`.`to_date` >= CURDATE()
                                        AND
                                            `tabBlanket Order`.`docstatus` = 1;""", {'customer': doc.get('customer'), 'item': item.get('item_code')}, as_dict=True)
        
        #If one or more Blanket Orders are Avalaible, get highes Discount with reached min. qty
        actual_discount = 0
        if len(blanket_orders) > 0:
            for bo in blanket_orders:
                blanket_order_doc = frappe.get_doc("Blanket Order", bo.get('name'))
                for discount in blanket_order_doc.get('additional_discount'):
                    if discount.get('item_code') == item.get('item_code') and actual_discount < discount.get('discount') and item.get('qty') >= discount.get('qty'):
                        if item.get('item_code') != "A-0001701":
                            actual_discount = discount.get('discount')
                        else:
                            if item.get('uom') == discount.get('uom'):
                                actual_discount = discount.get('discount')
            if actual_discount > 0:
                discounts.append({'name': item.get('name'), 'discount': actual_discount, 'blanket_order': bo.get('name')})
    
    #Return all found discounts
    if len(discounts) > 0:
        return discounts
    
    return None
