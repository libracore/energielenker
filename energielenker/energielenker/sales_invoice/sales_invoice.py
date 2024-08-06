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
    
def charged_at_cost(self, event):
    #get all sales orders which are affected
    affected_sales_orders = []
    for si_item in self.get('items'):
        if si_item.get('artikel_nach_aufwand') and si_item.get('artikel_nach_aufwand') not in affected_sales_orders:
            affected_sales_orders.append(si_item.get('sales_order'))
    
    for sales_order in affected_sales_orders:
        sales_order_doc = frappe.get_doc("Sales Order", sales_order)
        
            
    frappe.db.set_value("Sales Order", "AB0001479", "per_billed", 100)
    frappe.db.set_value("Sales Order", "AB0001479", "status", "To Deliver")
            
    return


