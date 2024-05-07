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
    warehouse = frappe.db.get_value("Depot", depot,"to_warehouse")
    sales_order = frappe.db.get_value("Depot", depot,"sales_order")
    data = frappe.db.sql("""SELECT 
                                `transactions`.`item_code`,
                                `transactions`.`item_name`,
                                `transactions`.`uom`,
                                SUM(`transactions`.`qty`) AS `balance_qty`
                            FROM (
                                SELECT 
                                    `item_code`,
                                    `item_name`,
                                    `uom`,
                                    SUM(IF (`tabStock Entry Detail`.`s_warehouse` = "{warehouse}", (-1) * `tabStock Entry Detail`.`qty`, `tabStock Entry Detail`.`qty`)) AS `qty`
                                FROM `tabStock Entry Detail`
                                LEFT JOIN `tabStock Entry` ON `tabStock Entry`.`name` = `tabStock Entry Detail`.`parent`
                                WHERE `tabStock Entry`.`source_depot` = "{depot}"
                                  AND `tabStock Entry`.`docstatus` = 1
                                GROUP BY `tabStock Entry Detail`.`item_code`
                                UNION SELECT
                                    `item_code`,
                                    `item_name`,
                                    `uom`,
                                    SUM((-1) * `qty`)
                                FROM `tabDelivery Note Item`
                                WHERE `tabDelivery Note Item`.`source_depot` = "{depot}"
                                  AND `tabDelivery Note Item`.`docstatus` = 1
                                GROUP BY `tabDelivery Note Item`.`item_code`
                            ) AS `transactions`
                            GROUP BY `transactions`.`item_code`;""".format(depot=depot, warehouse=warehouse), as_dict=True)
                            
    if event == "depot":
        items = {
            'items': data
        }
        
        html = frappe.render_template("energielenker/energielenker/doctype/depot/depot_items.html", items)
        
        return html
    elif event == "delivery_note":
        return data, depot, sales_order
