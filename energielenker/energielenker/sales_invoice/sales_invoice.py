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
def contains_abrechnen_nach_aufwand(sales_orders):
    sales_orders = json.loads(sales_orders)
    contains_abrechnen_nach_aufwand = []
    for sales_order in sales_orders:
        so = frappe.get_doc("Sales Order", sales_order)
        if so.items:
            for item in so.items:
                if item.artikel_nach_aufwand:
                    contains_abrechnen_nach_aufwand.append(sales_order)
                    break
    if contains_abrechnen_nach_aufwand:
        return check_status(contains_abrechnen_nach_aufwand)
    else:
        return []
    
def check_status(sales_orders):
    completely_billed_sales_orders = []
    incomplete_sales_orders = []
    # check if sales order is completely billed
    for so in sales_orders:
        completely_billed = ready_to_close(so)
        if completely_billed:
            completely_billed_sales_orders.append(so)

    # check if sales order status is 'to deliver and bill'
    for so in completely_billed_sales_orders:
        sales_order_doc = frappe.get_doc("Sales Order", so)
        if sales_order_doc.status == "To Deliver and Bill":
            incomplete_sales_orders.append(so)
    return incomplete_sales_orders

def ready_to_close(sales_order):
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    sales_order_items = sales_order_doc.items
    all_billed = True
    # for each sales order item check if it is in any sales invoice
    for sales_order_item in sales_order_items:
        billed = check_if_billed(sales_order_item.name, sales_order_item.qty, sales_order_item.artikel_nach_aufwand)
        if billed != "billed":
            all_billed = False
    return all_billed

def check_if_billed(sales_order_item, sales_order_quantity, artikel_nach_aufwand):
    billed = "Not billed"
    if sales_order_item:
        item = frappe.db.sql("""SELECT sum(`qty`) FROM `tabSales Invoice Item` 
                               WHERE `tabSales Invoice Item`.`docstatus` <2
                               AND `tabSales Invoice Item`.`so_detail` = '{item_code}'""".format(item_code=sales_order_item), as_dict=True)
        #join useneh, doctype statt status, sum qty statt *, nicht item_code sondern referenz
        if item:
            total_qty=sum(item_obj.qty for item_obj in item)
            if total_qty >= int(sales_order_quantity):
                billed = "billed"
    return billed

#liste von sales orders
#item.so_detail
@frappe.whitelist()
def get_billed_items(sales_order):
    #frappe.msgprint("remove_billed_items")
    #cry
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    sales_order_items = sales_order_doc.items
    remove_so_items = []
    for item in sales_order_items:
        billed = check_if_billed(item.name, item.qty, item.artikel_nach_aufwand)
        if billed == "billed":
            remove_so_items.append(item.name)
    return remove_so_items

