# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def sales_order_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    frappe.log_error(filters.get('sales_order'), "so")
    items = frappe.db.sql("""SELECT
                                `item_code`,
                                `item_name`
                            FROM
                                `tabSales Order Item`
                            WHERE 
                                `with_bom` = 1
                            AND
                                `parent` = '{so}'""".format(so=filters.get('sales_order')), as_dict=as_dict)
    frappe.log_error(items, "items")
    return items
