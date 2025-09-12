# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime

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
    cost_centers = {}
    #get total amount from Payment Schedule until filter date
    from_date_condition = """"""
    if filters.from_date:
        from_date_condition = """AND `ps`.`due_date` >= '{0}'""".format(filters.from_date)
    
    orders = frappe.db.sql("""SELECT 
                                `so`.`name` AS `sales_order`,
                                `so`.`project` AS `project`,
                                `so`.`cost_center` AS `cost_center`,
                                MAX(`ps`.`due_date`) AS `due_date`,
                                SUM(`ps`.`payment_amount`) AS `payment_amount`
                            FROM `tabPayment Schedule` AS `ps`
                            LEFT JOIN `tabSales Order` AS `so` ON `so`.`name` = `ps`.`parent`
                            WHERE `ps`.`due_date` <= '{date}'
                            {from_date_condition}
                            AND `so`.`docstatus` = 1
                            AND `so`.`status` NOT IN ('Closed', 'Completed')                
                            GROUP BY `sales_order`""".format(date=filters.date, from_date_condition=from_date_condition), as_dict=True)
    
    #loop through all orders
    for order in orders:
        gestellte_rechnungen = frappe.db.sql("""
                                        SELECT SUM(`si`.`rounded_total`) AS `amount`
                                        FROM `tabSales Invoice` AS `si`
                                        WHERE `si`.`name` IN (
                                            SELECT `siitem`.`parent`
                                            FROM `tabSales Invoice Item` AS `siitem`
                                            WHERE `siitem`.`sales_order` = '{so}')
                                        AND `si`.`docstatus` = 1""".format(so=order.sales_order), as_dict=True)
    
        #set outstanding amount
        order_payment_amount = order.payment_amount if order.payment_amount > 0 else 0
        if len(gestellte_rechnungen) > 0:
            if gestellte_rechnungen[0].amount:
                if filters.from_date:
                    #if start date is filtered, calculate outstanding amount
                    outstanding_amount = get_filtered_payment_amount(order.get('sales_order'), gestellte_rechnungen[0].amount, datetime.strptime(filters.from_date, "%Y-%m-%d").date(), datetime.strptime(filters.date, "%Y-%m-%d").date())
                else:
                    outstanding_amount = order_payment_amount - gestellte_rechnungen[0].amount
            else:
                outstanding_amount = order_payment_amount
        else:
            outstanding_amount = order_payment_amount                
        
        #If Filter is "Auftrag" and outstanding_amount is not 0, create line for Order
        if filters.ausfuehrung == 'Auftrag':
            if outstanding_amount != 0:
                _data = {
                    'sales_order': order.get('sales_order'),
                    'project': order.get('project'),
                    'project_name': frappe.db.get_value('Project', order.get('project'), 'project_name') or None if order.get('project') else None,
                    'project_manager': frappe.db.get_value('Project', order.get('project'), 'project_manager_name') or None if order.get('project') else None,
                    'cost_center': order.get('cost_center'),
                    'due_date': order.get('due_date'),
                    'outstanding_amount': outstanding_amount if outstanding_amount > 0 else 0,
                    'over_amount': 0 if outstanding_amount > 0 else (outstanding_amount * -1)
                }
                data.append(_data)
        #If Filter is "Kostenstelle" create cost center or add amount to existing cost center
        else:
            cost_center = order.get('cost_center')
            if cost_center and cost_center in cost_centers and outstanding_amount != 0:
                if outstanding_amount > 0:
                    cost_centers[cost_center]['outstanding_amount'] += outstanding_amount
                else:
                    cost_centers[cost_center]['over_amount'] += (outstanding_amount * -1)
            elif cost_center and cost_center not in cost_centers and outstanding_amount != 0:
                if outstanding_amount > 0:
                    new_entry = {'outstanding_amount': outstanding_amount, 'over_amount': 0}
                    cost_centers[cost_center] = new_entry
                else:
                    new_entry = {'outstanding_amount': 0, 'over_amount': (outstanding_amount * -1)}
                    cost_centers[cost_center] = new_entry
                    
    #If Filter is "Kostenstelle", prepare data for report
    for cost_center, amount in cost_centers.items():
        _data = {
            'cost_center': cost_center,
            'outstanding_amount': amount.get('outstanding_amount') if amount.get('outstanding_amount') else 0,
            'over_amount': amount.get('over_amount') if amount.get('over_amount') else 0
        }
        data.append(_data)

    return data

def get_filtered_payment_amount(so_name, gestellte_rechnungen, filter_date, end_date):
    #get all all scheduled payments before filter date and during filter date
    previous_payment_amount = 0
    period_amount = 0
    order = frappe.get_doc("Sales Order", so_name)
    
    for scheduled_payment in order.get('payment_schedule'):
        if scheduled_payment.get('due_date') < filter_date:
            previous_payment_amount += scheduled_payment.get('payment_amount')
        elif scheduled_payment.get('due_date') >= filter_date and scheduled_payment.get('due_date') <= end_date:
            period_amount += scheduled_payment.get('payment_amount')
    
    #get filtered payment amount
    filtered_payment_amount = 0
    if gestellte_rechnungen - previous_payment_amount > 0:
        filtered_payment_amount = period_amount - (gestellte_rechnungen - previous_payment_amount)
    else:
        filtered_payment_amount = period_amount
    
    return filtered_payment_amount
