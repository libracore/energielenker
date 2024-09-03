# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
from erpnext.manufacturing.doctype.bom.bom import BOM
import json

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
def get_bom_items(bom_item, sales_order, doc):
    doc = json.loads(doc)
    
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
    
    item_lines = []
    my_bom = frappe.get_doc({'doctype': "BOM", 'items': part_list_items})
    for d in part_list_items:
        if not d.get('belongs_to') in item_lines:
            item_lines.append(d.get('belongs_to'))
        d.update(my_bom.get_bom_material_detail({
                                            'item_code': d.get('item_code'),
                                            'bom_no': doc.get('bom_no') or '',
                                            # ~ "scrap_items": None,
                                            'qty': d.get('qty'),
                                            "stock_qty": d.get('qty'),
                                            "include_item_in_manufacturing": 1,
                                            "uom": d.get('uom'),
                                            "stock_uom": d.get('uom'),
                                            "conversion_factor": 1
                                        }))
                                
                                
    return {'items': item_lines, 'part_list_items': part_list_items}
