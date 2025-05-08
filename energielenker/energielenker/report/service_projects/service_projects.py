# Copyright (c) 2022-2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import calendar
import datetime
from frappe.utils import cint

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
        {'fieldname': 'reference', 'label': _('Task'), 'fieldname': 'task', 'fieldtype': 'Link', 'options': 'Task', 'width': 120},
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

def get_invoiceable_entries(from_date=None, to_date=None, customer=None):
    if not from_date:
        from_date = "2000-01-01"
    if not to_date:
        to_date = "2099-12-31"

    if not customer:
        customer = "%"
    
    sql_query = """
        SELECT 
            `tabProject`.`customer` AS `customer`,
            `tabCustomer`.`customer_name` AS `customer_name`,
            DATE(`tabTimesheet Detail`.`from_time`) AS `date`,
            "Timesheet"  AS `timesheet`,
            `tabTimesheet`.`name` AS `timesheet`,
            `tabTimesheet Detail`.`task` AS `task`,
            `tabTimesheet`.`employee_name` AS `employee_name`,
            `tabTimesheet Detail`.`name` AS `detail`,
            `tabProject`.`name` AS `project`,
            `tabTimesheet Detail`.`hours` AS `hours`,
            `tabSales Order Item`.`item_code` AS `item`,
            `tabSales Order Item`.`rate` AS `rate`,
            `tabTimesheet Detail`.`remarks` AS `remarks`,
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
        ORDER BY `customer_name` ASC, `date` ASC;
    """.format(
        from_date=from_date, 
        to_date=to_date,
        customer=customer
    )
    entries = frappe.db.sql(sql_query, as_dict=True)
    return entries

@frappe.whitelist()
def create_invoice(from_date, to_date, customer, company=None, project=None):
    # fetch entries
    entries = get_invoiceable_entries(from_date=from_date, to_date=to_date, customer=customer, company=company)
    
    # create sales invoice
    sinv = frappe.get_doc({
        'doctype': "Sales Invoice",
        'customer': customer,
        'customer_group': frappe.get_value("Customer", customer, "customer_group")
    })
    
    for e in entries:
        if project and e.project != project:
            continue            # skip in case project invoicing is active and this is not from this project
            
        #Format Remarks 
        if e.remarks:
            remarkstring = "{0}: {1}<br>{2}".format(e.date.strftime("%d.%m.%Y"), e.employee_name, e.remarks)
        else:
            remarkstring = "{0}: {1}".format(e.date.strftime("%d.%m.%Y"), e.employee_name)
        
        # project trace
        sinv.project = e.project
        
        item = {
            'item_code': e.item,
            'qty': e.qty,
            'rate': e.rate,
            'description': e.remarks,            # will be overwritten by frappe
            'remarks': remarkstring

        }
        if e.dt == "Delivery Note":
            item['delivery_note'] = e.reference
            item['dn_detail'] = e.detail

        elif e.dt == "Timesheet":
            item['timesheet'] = e.reference
            item['ts_detail'] = e.detail
            item['qty'] = e.hours
     
        if item['qty'] > 0:                     # only append items with qty > 0 (otherwise this will cause an error)
            sinv.append('items', item)
    
    # check currency and debtors account
    customer_doc = frappe.get_doc("Customer", customer)
    if customer_doc.default_currency:
        sinv.currency = customer_doc.default_currency
    
    # assume debtors account from first row (#NOTE TO FUTURE SELF: INCLUDE MULTI-COMPANY)
    if customer_doc.accounts and len(customer_doc.accounts) > 0:
        if company:
            for a in customer_doc.accounts:
                if a.company == company:
                    sinv.debit_to = a.account
        else:
            sinv.debit_to = customer_doc.accounts[0].account
    
    # add default taxes and charges
    taxes = find_tax_template(customer, company)
    if taxes:
        sinv.taxes_and_charges = taxes
        taxes_template = frappe.get_doc("Sales Taxes and Charges Template", taxes)
        for t in taxes_template.taxes:
            sinv.append("taxes", t)
    
    # insert new invoice
    sinv.insert()
    
    frappe.db.commit()
    
    return sinv.name

def find_tax_template(customer, company=None):
    # check if the customer has a specific template
    customer_doc = frappe.get_doc("Customer", customer)
    if customer_doc.get("default_taxes_and_charges"):
        template = customer_doc.get("default_taxes_and_charges")
    else:
        default_template = frappe.get_all("Sales Taxes and Charges Template", 
            filters={
                'is_default': 1,
                'company': company or frappe.defaults.get_global_default("company")
            }, 
            fields=['name'])
        if len(default_template) > 0:
            template = default_template[0]['name']
        else:
            template = None
    return template

        # ~ LEFT JOIN `tabSales Invoice Item` ON (
            # ~ `tabTimesheet Detail`.`name` = `tabSales Invoice Item`.`ts_detail`
            # ~ AND `tabSales Invoice Item`.`docstatus` < 2
        # ~ )
