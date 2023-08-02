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
    if filters.ausfuehrung == 'Auftrag':
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
                                    AND `status` NOT IN ('Closed', 'Completed')
                                )
                                GROUP BY `parent`""".format(date=filters.date), as_dict=True)
        
        for order in orders:
            gestellte_rechnungen = frappe.db.sql("""SELECT
                                                        SUM(`amount`) AS `amount`
                                                    FROM `tabSales Order Anzahlung`
                                                    WHERE `parent` = '{0}'""".format(order.sales_order), as_dict=True)
            
            project = frappe.db.get_value('Sales Order', order.sales_order, 'project') or None
            project_name = frappe.db.get_value('Project', project, 'project_name') or None if project else None
            affected_project = True
            if project:
                p = frappe.get_doc("Project", project)
                if p.status != 'Open':
                    affected_project = False
                if p.contract_type == 'Dienstleistungsvertrag':
                    affected_project = False
            
            if affected_project:
                if len(gestellte_rechnungen) > 0:
                    if gestellte_rechnungen[0].amount:
                        gestellte_rechnungen_amount = float(gestellte_rechnungen[0].amount)
                    else:
                        gestellte_rechnungen_amount = 0
                else:
                    gestellte_rechnungen_amount = 0
                
                order_payment_amount = order.payment_amount if order.payment_amount > 0 else 0
                outstanding_amount = order_payment_amount - gestellte_rechnungen_amount
                
                _data = {
                    'sales_order': order.sales_order,
                    'project': project,
                    'project_name': project_name,
                    'cost_center': frappe.db.get_value('Sales Order', order.sales_order, 'cost_center') or None,
                    'due_date': order.due_date,
                    'outstanding_amount': outstanding_amount if outstanding_amount > 0 else 0,
                    'over_amount': 0 if outstanding_amount > 0 else (outstanding_amount * -1)
                }
                if outstanding_amount > 0 or outstanding_amount < 0:
                    data.append(_data)
                elif not filters.not_null:
                    data.append(_data)
    else:
        cost_centers = frappe.db.sql("""SELECT 
                                    SUM(`ps`.`payment_amount`) AS `payment_amount`,
                                    `sales_order`.`cost_center` AS `cost_center`,
                                    `sales_order`.`name` AS `sales_order`
                                FROM `tabPayment Schedule` AS `ps`
                                INNER JOIN `tabSales Order` AS `sales_order` ON `ps`.`parent` = `sales_order`.`name`
                                WHERE `ps`.`parenttype` = 'Sales Order'
                                AND `ps`.`due_date` <= '{date}'
                                AND `ps`.`parent` IN (
                                    SELECT `name` FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `status` NOT IN ('Closed', 'Completed')
                                )
                                GROUP BY `sales_order`.`cost_center`""".format(date=filters.date), as_dict=True)
        
        for cost_center in cost_centers:
            gestellte_rechnungen = frappe.db.sql("""SELECT
                                                        SUM(`amount`) AS `amount`
                                                    FROM `tabSales Order Anzahlung`
                                                    WHERE `parent` IN (
                                                        SELECT `name` FROM `tabSales Order`
                                                        WHERE `docstatus` = 1
                                                        AND `status` NOT IN ('Closed', 'Completed')
                                                        AND `cost_center` = '{0}'
                                                    )""".format(cost_center.cost_center), as_dict=True)
            project = frappe.db.get_value('Sales Order', cost_center.sales_order, 'project') or None
            project_name = frappe.db.get_value('Project', project, 'project_name') or None if project else None
            affected_project = True
            if project:
                p = frappe.get_doc("Project", project)
                if p.status != 'Open':
                    affected_project = False
                if p.contract_type == 'Dienstleistungsvertrag':
                    affected_project = False
            
            if affected_project:
                if len(gestellte_rechnungen) > 0:
                    if gestellte_rechnungen[0].amount:
                        gestellte_rechnungen_amount = float(gestellte_rechnungen[0].amount)
                    else:
                        gestellte_rechnungen_amount = 0
                else:
                    gestellte_rechnungen_amount = 0
                
                cost_center_payment_amount = cost_center.payment_amount if cost_center.payment_amount > 0 else 0
                outstanding_amount = cost_center_payment_amount - gestellte_rechnungen_amount
                
                _data = {
                    'cost_center': cost_center.cost_center,
                    'outstanding_amount': outstanding_amount if outstanding_amount > 0 else 0,
                    'over_amount': 0 if outstanding_amount > 0 else (outstanding_amount * -1)
                }
                if outstanding_amount > 0 or outstanding_amount < 0:
                    data.append(_data)
                elif not filters.not_null:
                    data.append(_data)
    return data
