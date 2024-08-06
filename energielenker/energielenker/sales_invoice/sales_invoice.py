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
    so_doc = None
    for si_item in self.get('items'):
        if item.get('artikel_nach_aufwand'):
            if not so_doc:
                so_doc = frappe.db.get_doc("Sales Order", si_item.get('sales_order'))
            for so_item in so_doc.get('items')
                if so_item.get('name') == si_item.get('so_detail'):
                    diff_amt = 0
                    if so_item.get('rate') > si_item.get('rate'):
                        # ~ diff_amt = so_item.get('rate')
                    so_item.billed_amt += diff_amt
            
    return


