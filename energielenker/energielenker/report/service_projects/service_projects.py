# Copyright (c) 2022-2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import calendar
import datetime
from frappe.utils import cint
from erpnext.selling.doctype.sales_order import make_sales_invoice

def execute(filters=None):
    columns, data = [], []
            
    columns = get_columns()
    
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {'fieldname': 'customer', 'label': _('Customer'), 'fieldtype': 'Link', 'options': 'Customer', 'width': 75},
        {'fieldname': 'customer_name', 'label': _('Customer name'), 'fieldtype': 'Data', 'width': 150},
        {'fieldname': 'date', 'label': _('Date'), 'fieldtype': 'Date', 'width': 80},
        {'fieldname': 'project', 'label': _('Project'), 'fieldtype': 'Link', 'options': 'Project', 'width': 150},
        {'fieldname': 'item', 'label': _('Item'), 'fieldtype': 'Link', 'options': 'Item', 'width': 200},
        {'fieldname': 'hours', 'label': _('Billing Hours'), 'fieldtype': 'Float', 'width': 100},
        {'fieldname': 'rate', 'label': _('Rate'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'timesheet', 'label': _('Timesheet'), 'fieldtype': 'Link', 'options': 'Timesheet', 'width': 120},
        {'fieldname': 'sales_order', 'label': _('Sales Order'), 'fieldtype': 'Link', 'options': 'Sales Order', 'width': 120},
        {'fieldname': 'task', 'label': _('Task'), 'fieldtype': 'Link', 'options': 'Task', 'width': 120},
        {'fieldname': 'action', 'label': _('Action'), 'fieldtype': 'Data', 'width': 150}
    ]
    
def get_data(filters):
    entries = get_invoiceable_entries(from_date=filters.from_date, to_date=filters.to_date, customer=filters.customer)
    
    # group by project
    # find projects
    projects = []
    for e in entries:
        if e.project not in projects:
            projects.append(e.project)
    
    # create grouped entries
    output = []
    for p in projects:
        details = []
        total_h = 0
        total_amount = 0
        customer_name = None
        customer = None
        for e in entries:
            if e.project == p:
                total_h += e.hours or 0
                total_amount += ((e.qty or 1) * (e.rate or 0))
                customer_name = e.customer_name
                customer = e.customer
                details.append(e)
                
        # insert customer row
        output.append({
            'customer': customer,
            'customer_name': customer_name,
            'project': p,
            'hours': total_h,
            'rate': "",
            'action': _('Create invoice'),
            'indent': 0
        })
        for d in details:
            output.append(d)
    
    return output

def get_invoiceable_entries(from_date=None, to_date=None, customer=None, project=None):
    if not from_date:
        from_date = "2000-01-01"
    if not to_date:
        to_date = "2099-12-31"

    if not customer:
        customer = "%"
        
    if project:
        project_condition = "AND `project` = '{0}'".format(project)
    else:
        project_condition = ""
    
    sql_query = """
        SELECT 
            `tabProject`.`customer` AS `customer`,
            `tabCustomer`.`customer_name` AS `customer_name`,
            DATE(`tabTimesheet Detail`.`from_time`) AS `date`,
            "Timesheet"  AS `timesheet`,
            `tabTimesheet`.`name` AS `timesheet`,
            `tabTimesheet Detail`.`task` AS `task`,
            `tabTimesheet`.`employee_name` AS `employee_name`,
            `tabTimesheet Detail`.`name` AS `ts_detail`,
            `tabProject`.`name` AS `project`,
            `tabTimesheet Detail`.`hours` AS `hours`,
            `tabSales Order Item`.`item_code` AS `item`,
            `tabSales Order Item`.`rate` AS `rate`,
            `tabTimesheet Detail`.`remarks` AS `remarks`,
            `tabSales Order Item`.`parent` AS `sales_order`,
            `tabSales Order Item`.`name` AS `so_detail`,
            1 AS `indent`
        FROM `tabTimesheet Detail`
        LEFT JOIN `tabTimesheet` ON `tabTimesheet`.`name` = `tabTimesheet Detail`.`parent`
        LEFT JOIN `tabProject` ON `tabProject`.name = `tabTimesheet Detail`.`project`
        LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `tabProject`.`customer`
        LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`task` = `tabTimesheet Detail`.`task`
        WHERE 
           `tabTimesheet`.`docstatus` = 1
           AND `tabCustomer`.`name` LIKE "{customer}"
           AND ((DATE(`tabTimesheet Detail`.`from_time`) >= "{from_date}" AND DATE(`tabTimesheet Detail`.`from_time`) <= "{to_date}")
            OR (DATE(`tabTimesheet Detail`.`to_time`) >= "{from_date}" AND DATE(`tabTimesheet Detail`.`to_time`) <= "{to_date}"))
           AND `tabTimesheet Detail`.`no_bill` = 0
           AND `tabTimesheet Detail`.`billed_with_service_project` = 0
           AND `tabProject`.`is_service_project` = 1
           AND (`tabSales Order Item`.`docstatus` != 2
            OR `tabSales Order Item`.`docstatus` IS NULL)
            {project_condition}
        ORDER BY `customer_name` ASC, `date` ASC;
    """.format(
        from_date=from_date, 
        to_date=to_date,
        customer=customer,
        project_condition=project_condition
    )
    entries = frappe.db.sql(sql_query, as_dict=True)
    return entries

@frappe.whitelist()
def create_invoice(from_date, to_date, project):
    # fetch entries
    entries = get_invoiceable_entries(from_date=from_date, to_date=to_date, project=project)
    
    #get needed Sales Orders to create Invoice from and prepare item data
    sales_orders = []
    filtered_entries = []
    details = []
    for entry in entries:
        if entry.get('sales_order'):
            filtered_entries.append({
                                    'so_detail': entry.get('so_detail'),
                                    'remarks': entry.get('remarks'),
                                    'qty': entry.get('hours'),
                                    'employee_name': entry.get('employee_name'),
                                    'task': entry.get('task'),
                                    'ts_date': entry.get('date'),
                                    'sales_order': entry.get('sales_order'),
                                    'item': entry.get('item')
                                    })
            if entry.get('sales_order') not in sales_orders:
                sales_orders.append(entry)
    
    for sales_order in sales_orders:
        #create invoice from sales order
        invoice = make_sales_invoice(sales_order)
        
        #remove all items
        invoice.items = []
        
        #Add Items to Invoice
        
        
        #Insert Invoice
        invoice.insert()
        
        #Update Timesheets
