# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Depot(Document):
    pass

@frappe.whitelist()
def get_items_html(depot, event):
    items = frappe.db.sql("""SELECT 
                                `transactions`.`item_code`,
                                SUM(`transactions`.`qty`) AS `balance_qty`
                            FROM (
                                SELECT 
                                    `item_code`, 
                                    IF (`tabStock Entry Detail`.`source_warehouse` = "{warehouse}", (-1) * `tabStock Entry Detail`.`qty`, `tabStock Entry Detail`.`qty`) AS `qty`
                                FROM `tabStock Entry Detail`
                                LEFT JOIN `tabStock Entry` ON `tabStock Entry`.`name` = `tabStock Entry Detail`.`parent`
                                WHERE `tabStock Entry`.`source_depot` = "{depot}"
                                  AND `tabStock Entry`.`docstatus` = 1
                                UNION SELECT
                                    `item_code`,
                                    (-1) * `qty`
                                FROM `tabDelivery Note Item`
                                WHERE `tabDelivery Note Item`.`source_depot` = "{depot}"
                                  AND `tabDelivery Note Item`.`docstatus` = 1
                            ) AS `transactions`
                            GROUP BY `transactions`.`item_code`;""".format(depot=depot, warehouse=warehouse), as_dict=True)
                            
    frappe.log_error(items, "items")

    
    html = frappe.render_template("energielenker/energielenker/doctype/depot/depot_items.html", items)
    
    return html
