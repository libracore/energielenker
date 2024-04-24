# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

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

@frappe.whitelist()
def check_if_billed(sales_order_item, sales_order_quantity, artikel_nach_aufwand):
    billed = "Not billed"
    if sales_order_item:
        item = frappe.db.sql("""SELECT * FROM `tabSales Invoice Item` 
                               LEFT JOIN `tabSales Invoice`
                               ON `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
                               WHERE `tabSales Invoice`.`status` != 'Cancelled'
                               AND `tabSales Invoice`.`status` != 'Draft'
                               AND `tabSales Invoice Item`.`so_detail` = '{item_code}'""".format(item_code=sales_order_item), as_dict=True)
        if item:
            total_qty=sum(item_obj.qty for item_obj in item)
            if total_qty >= int(sales_order_quantity):
                billed = "billed"
    return billed
