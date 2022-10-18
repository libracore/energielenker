# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Kundenauftrag"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Projektnummer"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
        {"label": _("Projektname"), "fieldname": "project_name", "fieldtype": "Data", "width": 100},
        {"label": _("Kostenstelle"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 100},
        {"label": _("Zahlungsdatum bis einschl."), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": _("Saldo offene Zahlungsbeträge"), "fieldname": "outstanding_amount", "fieldtype": "Currency"}
    ]
    return columns

def get_data(filters):
    data = []
    orders = frappe.db.sql("""SELECT 
                                SUM(`payment_amount`) AS `payment_amount`,
                                `parent` AS `sales_order`,
                                MAX(`due_date`) AS `due_date`
                            FROM `tabPayment Schedule`
                            WHERE `parenttype` = 'Sales Order'
                            AND `due_date` <= '{date}'
                            AND `parent` IN (
                                SELECT `name` FROM `tabSales Order`
                                WHERE `docstatus` = 1
                            )
                            GROUP BY `parent`""".format(date=filters.date), as_dict=True)
    
    for order in orders:
        project_payment_forecast = frappe.db.sql("""SELECT
                                                        SUM(`pf`.`amount`) AS `outstanding_amount`,
                                                        `pf`.`parent` AS `project`,
                                                        `pf`.`order` AS `sales_order`,
                                                        `p`.`project_name` AS `project_name`
                                                    FROM `tabPayment Forecast` AS `pf`
                                                    LEFT JOIN `tabProject` AS `p` ON `pf`.`parent` = `p`.`name`
                                                    WHERE `pf`.`order` = '{sales_order}'
                                                    AND `pf`.`invoice_created` != 1
                                                    GROUP BY `pf`.`order`""".format(sales_order=order.sales_order), as_dict=True)
        if len(project_payment_forecast) > 0:
            project_payment_forecast = project_payment_forecast[0]
            outstanding_amount = project_payment_forecast.outstanding_amount
        else:
            project = frappe.db.get_value('Sales Order', order.sales_order, 'project') or None
            project_name = frappe.db.get_value('Project', project, 'project_name') or None if project else None
            project_payment_forecast = False
            outstanding_amount = (frappe.db.get_value('Sales Order', order.sales_order, 'grand_total') / 100) * (100 - frappe.db.get_value('Sales Order', order.sales_order, 'per_billed') or 0)
        
        _data = {
            'sales_order': order.sales_order,
            'project': project_payment_forecast.project if project_payment_forecast else project,
            'project_name': project_payment_forecast.project_name if project_payment_forecast else project_name,
            'cost_center': frappe.db.get_value('Sales Order', order.sales_order, 'cost_center') or None,
            'due_date': order.due_date,
            'outstanding_amount': outstanding_amount
        }
        if outstanding_amount > 0:
            data.append(_data)
        elif not filters.not_null:
            data.append(_data)
    return data
