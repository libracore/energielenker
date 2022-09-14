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
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 95},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Salutation"), "fieldname": "salutation", "fieldtype": "Data", "width": 60},
        {"label": _("First Name"), "fieldname": "first_name", "fieldtype": "Data", "width": 95},
        {"label": _("Last Name"), "fieldname": "last_name", "fieldtype": "Data", "width": 95},
        {"label": _("E-Mail"), "fieldname": "email", "fieldtype": "Data", "width": 200},
        {"label": _("Mobile"), "fieldname": "mobile", "fieldtype": "Data", "width": 150},
        {"label": _("Phone"), "fieldname": "phone", "fieldtype": "Data", "width": 150}
    ]

    return columns

def get_data(filters):
    data = []
    projects = frappe.db.sql("""SELECT
                                    `name`,
                                    `customer`,
                                    `contact`
                                FROM `tabProject`
                                WHERE `status` = 'Completed'""", as_dict=True)
    for project in projects:
        _data = {
            'project': project.name,
            'customer': project.customer
        }
        
        if project.contact:
            contact = frappe.get_doc("Contact", project.contact)
            _data['salutation'] = contact.salutation
            _data['first_name'] = contact.last_name
            _data['last_name'] = contact.first_name
            _data['mobile'] = contact.mobile_no
            _data['phone'] = contact.phone
            
            for email in contact.email_ids:
                if int(email.is_primary) == 1:
                    _data['email'] = email.email_id
        
        data.append(_data)
    
    return data
