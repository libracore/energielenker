# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def sales_order_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    if filters.get('sales_order'):
        items = frappe.db.sql("""SELECT
                                    `item_code`,
                                    `item_name`
                                FROM
                                    `tabSales Order Item`
                                WHERE 
                                    `with_bom` = 1
                                AND
                                    `parent` = '{so}'""".format(so=filters.get('sales_order')), as_dict=as_dict)
    else:
        items = frappe.db.sql("""SELECT
                            `item_code`,
                            `item_name`
                        FROM
                            `tabItem`""", as_dict=as_dict)
    return items
    
@frappe.whitelist()
def get_bom_items(bom_item, sales_order):
    items = frappe.db.sql("""
                            SELECT
                                `idx`,
                                `item_code`,
                                `with_bom`
                            FROM
                                `tabSales Order Item`
                            WHERE
                                `parent` = '{so}'
                            AND
                                `item_code` = '{item}'""".format(so=sales_order, item=bom_item), as_dict=True)
    
    part_list_items = frappe.db.sql("""
                            SELECT
                                `item_code`,
                                SUM(`qty`) AS `qty`,
                                `uom`,
                                `belongs_to`
                            FROM
                                `tabSales Order Part List Item`
                            WHERE
                                `parent` = '{so}'
                            GROUP BY
                                `item_code`,
                                `uom`,
                                `belongs_to`""".format(so=sales_order), as_dict=True)
                                
    return {'items': items, 'part_list_items': part_list_items}
