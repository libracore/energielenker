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
