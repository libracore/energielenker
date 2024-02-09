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
            
            manuell_gestellte_rechnungen = frappe.db.sql("""SELECT
                                                            `tabSales Invoice Item`.`sales_order` AS `sales_order`,
                                                            `tabSales Invoice`.`rounded_total` AS `total_amount`
                                                        FROM `tabSales Invoice`
                                                        JOIN `tabSales Invoice Item` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
                                                        WHERE `tabSales Invoice Item`.`sales_order` = '{0}'
                                                        AND `tabSales Invoice`.`docstatus` = 1
                                                        AND `tabSales Invoice`.`billing_type` = 'Rechnung'
                                                        GROUP BY `tabSales Invoice`.`name`""".format(order.sales_order), as_dict=True)
            if len(manuell_gestellte_rechnungen) > 0:
                if manuell_gestellte_rechnungen[0].sales_order == "AB0000032":
                    frappe.log_error(manuell_gestellte_rechnungen, "Hoi")
                                                        
            if len(manuell_gestellte_rechnungen) > 0:
                if manuell_gestellte_rechnungen[0].total_amount and gestellte_rechnungen[0].amount:
                    gestellte_rechnungen[0].amount += manuell_gestellte_rechnungen[0].total_amount
                elif not gestellte_rechnungen[0].amount:
                    gestellte_rechnungen[0].amount = manuell_gestellte_rechnungen[0].total_amount
            
            project = frappe.db.get_value('Sales Order', order.sales_order, 'project') or None
            project_name = frappe.db.get_value('Project', project, 'project_name') or None if project else None
            project_manager = frappe.db.get_value('Project', project, 'project_manager_name') or None
            outstanding_amount = 0
            affected_project = True
            if project:
                p = frappe.get_doc("Project", project)
                if p.status != 'Open':
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
            
            if not project:
                gestellte_rechnungen_ohne_project = frappe.db.sql("""SELECT
                                                            `tabSales Invoice Item`.`sales_order` AS `sales_order`,
                                                            `tabSales Invoice`.`rounded_total` AS `total_outstanding_amount`
                                                        FROM `tabSales Invoice`
                                                        JOIN `tabSales Invoice Item` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
                                                        WHERE `tabSales Invoice Item`.`sales_order` = '{0}'
                                                        AND `tabSales Invoice`.`docstatus` = 1
                                                        GROUP BY `tabSales Invoice`.`name`""".format(order.sales_order), as_dict=True)

                if len(gestellte_rechnungen_ohne_project) > 0:
                    gestellte_rechnungen_amount_ohne_project = 0

                    for invoice_data in gestellte_rechnungen_ohne_project:
                        gestellte_rechnungen_amount_ohne_project += float(invoice_data.get('total_outstanding_amount', 0))
                        
                    order_payment_amount = order.payment_amount if order.payment_amount > 0 else 0
                    outstanding_amount = order_payment_amount - gestellte_rechnungen_amount_ohne_project
  
            _data = {
                'sales_order': order.sales_order,
                'project': project,
                'project_name': project_name,
                'project_manager': project_manager,
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
        cost_centers_dict = {}
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
                                GROUP BY `sales_order`.`name`""".format(date=filters.date), as_dict=True)
        
        for cost_center in cost_centers:
            gestellte_rechnungen = frappe.db.sql("""SELECT
                                                        SUM(`amount`) AS `amount`
                                                    FROM `tabSales Order Anzahlung`
                                                    WHERE `parent` = '{0}'""".format(cost_center.sales_order), as_dict=True)
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
                
                outstanding_amount = outstanding_amount if outstanding_amount > 0 else 0
                over_amount = 0 if outstanding_amount > 0 else (outstanding_amount * -1)
                
                if cost_center.cost_center in cost_centers_dict:
                    
                    cost_centers_dict[cost_center.cost_center]['outstanding_amount'] += outstanding_amount
                    cost_centers_dict[cost_center.cost_center]['over_amount'] += over_amount
                else:
                    cost_centers_dict[cost_center.cost_center] = {
                        'name': cost_center.cost_center,
                        'outstanding_amount': outstanding_amount,
                        'over_amount': over_amount
                    }
                
        for cost_center in cost_centers_dict:
            _data = {
                'cost_center': cost_centers_dict[cost_center]['name'],
                'outstanding_amount': cost_centers_dict[cost_center]['outstanding_amount'] if cost_centers_dict[cost_center]['outstanding_amount'] > 0 else 0,
                'over_amount': 0 if cost_centers_dict[cost_center]['outstanding_amount'] > 0 else (cost_centers_dict[cost_center]['outstanding_amount'] * -1)
            }
            if cost_centers_dict[cost_center]['outstanding_amount'] > 0 or cost_centers_dict[cost_center]['outstanding_amount'] < 0:
                data.append(_data)
            elif not filters.not_null:
                data.append(_data)
    return data
