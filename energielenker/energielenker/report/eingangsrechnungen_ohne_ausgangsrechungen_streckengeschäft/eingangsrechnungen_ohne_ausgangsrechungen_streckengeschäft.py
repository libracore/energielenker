# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data
    

def get_columns():
    columns = [
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("DBS"), "fieldname": "dbs", "fieldtype": "Data", "width": 100}
    ]
    return columns

def get_data():
    data = frappe.db.sql("""SELECT
        `piitem`.`parent` AS `invoice`,
        `piitem`.`amount` AS `amount`,
        `soitem`.`parent` AS `sales_order`,
        `soitem`.`delivered_by_supplier` AS `dbs`
        FROM `tabSales Order Item` AS `soitem`
        LEFT JOIN `tabPurchase Order Item` AS `poitem` ON `poitem`.`sales_order_item` = `soitem`.`name`
        LEFT JOIN `tabPurchase Invoice Item` AS `piitem` ON `piitem`.`po_detail` = `poitem`.`name`
        WHERE `soitem`.`delivered_by_supplier` = 1
        AND `soitem`.`billed_amt` != `soitem`.`amount`
        AND `piitem`.`docstatus` = 1
        AND `soitem`.`docstatus` = 1
        AND `poitem`.`docstatus` = 1
        """, as_dict=True)
        
    return data
