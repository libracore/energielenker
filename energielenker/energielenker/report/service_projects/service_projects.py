# Copyright (c) 2022-2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import calendar
import datetime
from frappe.utils import cint
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from frappe.utils import formatdate
import datetime

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
            `tabSales Order Item`.`docstatus` AS `so_docstatus`,
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
        ORDER BY `sales_order` ASC, `so_detail` ASC, `date` ASC;
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
    frappe.log_error(entries, "entries")
    #get needed Sales Orders to create Invoice from and prepare item data
    sales_orders = []
    filtered_entries = []
    details = []
    for entry in entries:
        #Check if all Sales Orders are booked
        if entry.get('sales_order') and entry.get('so_docstatus') != 1:
            frappe.throw("Kundenauftrag {0} muss zuerst gebucht werden.".format(entry.get('sales_order')))
        if entry.get('sales_order'):
            filtered_entries.append({
                                    'so_detail': entry.get('so_detail'),
                                    'remarks': entry.get('remarks'),
                                    'qty': entry.get('hours'),
                                    'employee_name': entry.get('employee_name'),
                                    'task': entry.get('task'),
                                    'ts_date': entry.get('date'),
                                    'ts_detail': entry.get('ts_detail'),
                                    'sales_order': entry.get('sales_order'),
                                    'item': entry.get('item'),
                                    'rate': entry.get('rate')
                                    })
            if entry.get('sales_order') not in sales_orders:
                sales_orders.append(entry.get('sales_order'))
    
    created_invoices = []
    
    for sales_order in sales_orders:
        #create invoice from sales order
        invoice = make_sales_invoice(sales_order)
        
        #remove all items
        invoice.items = []
        
        #Prepare List to mark Timesheets as paid
        invoiced_ts_entries = []
        
        #Add Items to Invoice
        so_detail = None
        for filtered_entry in filtered_entries:
            frappe.log_error(filtered_entry.get('ts_date'), "date")
            frappe.log_error(type(filtered_entry.get('ts_date')), "type")
            #Check if actual Entry belongs to actual Invoice
            if filtered_entry.get('sales_order') == sales_order:
                if filtered_entry.get('so_detail') != so_detail:
                    #Add item to Invoice
                    if so_detail != None:
                        invoice.append('items', new_item)
                    #Create new Item
                    new_item = {
                                'item_code': filtered_entry.get('item'),
                                'qty': filtered_entry.get('qty'),
                                'uom': "Std",
                                'rate': filtered_entry.get('rate'),
                                'description': "{0}, {1}, {2}h:<br>{3}".format(filtered_entry.get('employee_name'), formatdate(filtered_entry.get('ts_date'), "dd.mm.yyyy"), filtered_entry.get('qty'), filtered_entry.get('remarks')),
                                'sales_order': filtered_entry.get('sales_order'),
                                'so_detail': filtered_entry.get('so_detail')
                                }
                else:
                    #Update Item
                    new_item['qty'] += filtered_entry.get('qty')
                    new_item['description'] += "<br><br>{0}, {1}, {2}h:<br>{3}".format(filtered_entry.get('employee_name'), formatdate(filtered_entry.get('ts_date'), "dd.mm.yyyy"), filtered_entry.get('qty'), filtered_entry.get('remarks'))
                    
                #Add Entry Invoiced TS Entry
                invoiced_ts_entries.append(filtered_entry.get('ts_detail'))
                
                #Set new so_detail
                so_detail = filtered_entry.get('so_detail')
                
        #Add Last item to Invoice
        invoice.append('items', new_item)
        
        #Insert Invoice
        invoice.insert()
        
        #Update Timesheets
        for ts_entry in invoiced_ts_entries:
            frappe.db.set_value("Timesheet Detail", ts_entry, "billed_with_service_project", 1)
            frappe.db.set_value("Timesheet Detail", ts_entry, "billed_with_service_sinv", invoice.get('name'))
        
        #Add new Invoice to Invoices List
        created_invoices.append(invoice.get('name'))
        
    frappe.db.commit()
    return created_invoices

def reset_testproject():
    update = frappe.db.sql("""
                            UPDATE
                                `tabTimesheet Detail`
                            SET
                                `billed_with_service_project` = 0,
                                `billed_with_service_sinv` = NULL
                            WHERE
                                `project` = 'P0000838';""")
