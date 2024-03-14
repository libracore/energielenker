# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    if filters.ausfuehrung == 'Auftrag':
        columns = [
            {"label": _("Kundenauftrag"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
            {"label": _("Projektnummer"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
            {"label": _("Projektname"), "fieldname": "project_name", "fieldtype": "Data", "width": 100},
            {"label": _("Projektleiter"), "fieldname": "project_manager", "fieldtype": "Data", "width": 100},
            {"label": _("Kostenstelle"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 100},
            {"label": _("Zahlungsdatum bis einschl."), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
            {"label": _("Saldo offene Zahlungsbeträge"), "fieldname": "outstanding_amount", "fieldtype": "Currency"},
            {"label": _("Saldo Zahlungsbeträge > Forecast"), "fieldname": "over_amount", "fieldtype": "Currency"}
        ]
    else:
        columns = [
            {"label": _("Kostenstelle"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 100},
            {"label": _("Saldo offene Zahlungsbeträge"), "fieldname": "outstanding_amount", "fieldtype": "Currency"},
            {"label": _("Saldo Zahlungsbeträge > Forecast"), "fieldname": "over_amount", "fieldtype": "Currency"}
        ]
    return columns

def get_data(filters):
    data = []
    #get total amount from Payment Schedule until filter date
    orders = frappe.db.sql("""SELECT 
                                `so`.`name` AS `sales_order`,
                                `so`.`project` AS `project`,
                                `so`.`cost_center` AS `cost_center`,
                                MAX(`ps`.`due_date`) AS `due_date`,
                                SUM(`ps`.`payment_amount`) AS `payment_amount`
                            FROM `tabPayment Schedule` AS `ps`
                            LEFT JOIN `tabSales Order` AS `so` ON `so`.`name` = `ps`.`parent`
                            WHERE `ps`.`due_date` <= '{date}'
                            AND `so`.`docstatus` = 1
                            AND `so`.`status` NOT IN ('Closed', 'Completed')                
                            GROUP BY `sales_order`""".format(date=filters.date), as_dict=True)
    for order in orders:
        gestellte_rechnungen = frappe.db.sql("""
												SELECT SUM(`amount`)
												FROM `tabSales Invoice Item`
												WHERE `sales_order` = '{so}'
												AND `parent`.`docstatus` = 1""".format(so=order.sales_order), as_dict=True)
    
    data = orders

    return data
