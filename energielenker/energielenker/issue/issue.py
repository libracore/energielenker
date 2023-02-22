# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.communication.email import make
# ~ import time

def onload_functions(self, event):
    check_for_assigment(self)

def add_mail_as_description_to_issue(self, event):
    if self.reference_doctype == 'Issue':
    issues = frappe.db.sql("""SELECT `name` FROM `tabIssue` WHERE `mark_for_reply` = 1 AND `name` = '{0}'""".format(self.reference_name), as_dict=True)
    for issue in issues:
        frappe.db.set_value("Issue", issue.name, 'description', self.content, update_modified=False)
        frappe.db.set_value("Issue", issue, 'mark_for_reply', 0, update_modified=False)
        frappe.db.commit()
        send_issue_creation_notification_to_customer(issue.name, self.content, self.sender, self.subject)
        frappe.log_error("Issue: {0}\nCommunication: {1}".format(self.reference_name, self.name), "add_mail_as_description_to_issue")
    

def send_issue_creation_notification_to_customer(issue, description, sender, subject):
    subject = subject
    raised_by = sender
    if raised_by:
        make(doctype='Issue', 
        name=issue, 
        content='Vielen Dank für Ihre Nachricht. Ihr Ticket wird bearbeitet.<hr>{0}'.format(description or '-'), 
        subject='{0}: Ihr Ticket ({1}) wird bearbeitet'.format(subject, issue), 
        sender='testsupport@energielenker.de', 
        send_email=True, 
        recipients=[raised_by])
    
    frappe.db.commit()

def check_for_assigment(self):
    zuweisungen = frappe.db.sql("""SELECT `creation` FROM `tabToDo` WHERE `status` = 'Open' AND `reference_type` = 'Issue' AND `reference_name` = '{0}' ORDER BY `creation` ASC""".format(self.name), as_dict=True)
    if len(zuweisungen) > 0:
        frappe.db.set_value("Issue", self.name, 'letzte_zuweisung', zuweisungen[0].creation, update_modified=False)
        frappe.db.commit()
    else:
        frappe.db.set_value("Issue", self.name, 'letzte_zuweisung', None, update_modified=False)
        frappe.db.commit()

def mark_for_reply(self, event):
    if self.issue_type != 'Reklamation':
        frappe.db.set_value("Issue", self.name, 'mark_for_reply', 1, update_modified=False)
        frappe.db.commit()
