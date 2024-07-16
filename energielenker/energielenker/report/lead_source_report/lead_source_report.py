# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
    
def get_columns():
    columns = [
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Lead Source"), "fieldname": "lead_source", "fieldtype": "Data", "width": 100},
        {"label": _("Sales Order Date"), "fieldname": "sales_order_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("PLZ"), "fieldname": "plz", "fieldtype": "Data", "width": 60},
        {"label": _("Net Amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Customer Advisor (Sales Order)"), "fieldname": "customer_advisor", "fieldtype": "Data", "width": 150},
        {"label": _("Customer Care (Customer)"), "fieldname": "customer_care", "fieldtype": "Data", "width": 150}
    ]
    return columns

def get_data(filters):
    data = frappe.db.sql("""
        SELECT DISTINCT
            `so`.`name` AS `sales_order`,
            `so`.`transaction_date` AS `sales_order_date`,
            `so`.`customer` AS `customer_name`,
            `so`.`total` AS `net_amount`,
            `so`.`ansprechpartner` AS `customer_advisor`,
            `cust`.`ansprechpartner` AS `customer_care`,
            `lead`.`source` AS `lead_source`,
            `addr`.`plz` AS `plz`
        FROM
            `tabSales Order` AS `so`
        LEFT JOIN
            `tabCustomer` AS `cust` ON `cust`.`name` = `so`.`customer`
        INNER JOIN
            `tabLead` AS `lead` ON `lead`.`name` = `cust`.`lead_name`
        LEFT JOIN
            `tabDynamic Link` AS `link`
                ON `link`.`link_name` = `so`.`customer`
        INNER JOIN
            (SELECT
                `name`, `plz`, `is_primary_address`
            FROM
                `tabAddress`
            WHERE
                `is_primary_address` = 1) AS `addr` ON `link`.`parent` = `addr`.`name`
        WHERE
            `so`.`docstatus` = 1
        AND
            `lead`.`source` IS NOT NULL
        ORDER BY
            `lead`.`source`""", as_dict=True)
   
    return data
