# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

#get all bom items where stock is not maintained for stock entry print format
def get_bom_items(bom_name):
    items = frappe.db.sql("""
                        SELECT
                            `bom_item`.`item_code`,
                            `bom_item`.`item_name`,
                            `bom_item`.`qty`,
                            `bom_item`.`uom`
                        FROM
                            `tabBOM Item` AS `bom_item`
                        LEFT JOIN
                            `tabItem` AS `item` ON `item`.`name` = `bom_item`.`item_code`
                        WHERE
                            `bom_item`.`parent` = '{bom}'
                        AND
                            `item`.`is_stock_item` = 0""".format(bom=bom_name), as_dict=True)
    
    return items

def serial_no_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    # ~ if filters.get('batch_no'):
        # ~ batch_condition = """AND `tabSerial No`.`batch_no` = '{batch}'""".format(batch=filters.get('batch_no'))
    # ~ else:
        # ~ batch_condition = """"""
    serial_nos = frappe.db.sql("""
                                SELECT
                                    `tabSerial No`.`name`
                                FROM
                                    `tabSerial No`
                                WHERE
                                    `item_code` = '{item_code}'
                                AND
                                    `warehouse` IS NULL
                                AND
                                    `delivery_document_type` IS NULL""".format(item_code=filters.get('item_code')), as_dict=as_dict)
    return serial_nos
