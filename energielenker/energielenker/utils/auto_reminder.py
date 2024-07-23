# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import today, add_to_date

def check_for_reminder():
    customer_reminder = frappe.db.sql("""SELECT
                                            `name`
                                        FROM `tabCustomer`
                                        WHERE `wiederkehrende_benachrichtigung_aktiviert` = 1
                                        AND `naechste_ausfuehrung` = '{today}'""".format(today=today()), as_dict=True)
    for cr in customer_reminder:
        customer = frappe.get_doc("Customer", cr.name)
        frappe.sendmail(recipients=get_recipients(customer.empfaenger), message=customer.informationstext, sender='vertrieb@energielenker.de', subject='Reminder: {0}'.format(customer.name))
        new_execution_date = get_new_execution_date(customer)
        customer.naechste_ausfuehrung = new_execution_date
        customer.save()
    
    issue_reminder = frappe.db.sql("""SELECT
                                            `name`
                                        FROM `tabIssue`
                                        WHERE `wiederkehrende_benachrichtigung_aktiviert` = 1
                                        AND `naechste_ausfuehrung` = '{today}'""".format(today=today()), as_dict=True)
    for ir in issue_reminder:
        issue = frappe.get_doc("Issue", ir.name)
        frappe.sendmail(recipients=get_recipients(issue.empfaenger), message=issue.informationstext, sender='vertrieb@energielenker.de', subject='Reminder: {0}'.format(issue.name))
        new_execution_date = get_new_execution_date(issue)
        issue.naechste_ausfuehrung = new_execution_date
        issue.save()
        
    project_reminder = frappe.db.sql("""SELECT
                                            `name`
                                        FROM `tabProject`
                                        WHERE `wiederkehrende_benachrichtigung_aktiviert` = 1
                                        AND `naechste_ausfuehrung` = '{today}'""".format(today=today()), as_dict=True)
    for pr in project_reminder:
        project = frappe.get_doc("Project", pr.name)
        frappe.sendmail(recipients=get_recipients(project.empfaenger), message=project.informationstext, sender='vertrieb@energielenker.de', subject='Reminder: {0}'.format(project.name))
        new_execution_date = get_new_execution_date(project)
        project.naechste_ausfuehrung = new_execution_date
        project.save()
    
    return

def get_recipients(empfaenger=None):
    recipients = []
    for _recipient in empfaenger.split("\n"):
        recipients.append(_recipient)
    return recipients

def get_new_execution_date(record):
    intervall = record.intervall
    intervall_typ = record.intervall_typ
    weeks = 0
    months = 0
    years = 0
    if intervall_typ == 'Wöchentlich':
        weeks = 1
    elif intervall_typ == 'Monatlich':
        months = 1
    elif intervall_typ == 'Quartalsweise':
        months = 3
    elif intervall_typ == 'Halbjährlich':
        months = 6
    elif intervall_typ == 'Jährlich':
        years = 1
    weeks = weeks * intervall
    months = months * intervall
    years = years * intervall
    new_execution_date = add_to_date(date=record.naechste_ausfuehrung, years=years, months=months, weeks=weeks)
    return new_execution_date
