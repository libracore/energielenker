# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
from erpnext.manufacturing.doctype.bom.bom import BOM
import json
from frappe.utils import cint

def autoname(self, event):
    names = frappe.db.sql_list("""select name from `tabBOM` where item=%s""", self.item)

    if names:
        # name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1

        # split by item
        names = [name.split(self.item)[-1][1:] for name in names]

        # split by (-) if cancelled
        names = [cint(name.split('-')[-1]) for name in names]

        idx = max(names) + 1
    else:
        idx = 1

    self.name = 'BOM-' + self.item + ('-%.4i' % idx)


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
                                        `tabSales Order Part List Item`.`item_code`,
                                        SUM(`tabSales Order Part List Item`.`qty`) AS `qty`,
                                        `tabSales Order Part List Item`.`uom`,
                                        `tabSales Order Part List Item`.`belongs_to`,
                                        `tabSales Order Item`.`name` AS `so_detail`
                                    FROM
                                        `tabSales Order Part List Item`
                                    LEFT JOIN
                                        `tabSales Order Item` ON `tabSales Order Item`.`idx` = `tabSales Order Part List Item`.`belongs_to`
                                    WHERE
                                        `tabSales Order Part List Item`.`parent` = '{so}'
                                    AND
                                        `tabSales Order Item`.`item_code` = '{bom_item}'
                                    AND
                                        `tabSales Order Item`.`parent` = '{so}'
                                    GROUP BY
                                        `tabSales Order Part List Item`.`item_code`,
                                        `tabSales Order Part List Item`.`uom`,
                                        `tabSales Order Part List Item`.`belongs_to`""".format(so=sales_order, bom_item=bom_item), as_dict=True)
    
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
