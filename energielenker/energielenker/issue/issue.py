# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.communication.email import make

def onload_functions(self, event):
    add_mail_as_description(self)
    check_for_assigment(self)

def add_mail_as_description(self):
    communications = frappe.db.sql("""
        SELECT `content`
        FROM `tabCommunication`
        WHERE `reference_doctype` = 'Issue'
        AND `reference_name` = '{issue}'
        ORDER BY `creation` ASC
    """.format(issue=self.name), as_dict=True)
    if len(communications) > 0 and not self.description:
        self.description = communications[0].content

def send_creation_notification_to_customer(self, event):
    if self.raised_by:
        make(doctype='Issue', 
        name=self.name, 
        content='Vielen Dank für Ihre Nachricht. Ihr Ticket wird bearbeitet.', 
        subject='Ihr Ticket ({0}) wird bearbeitet'.format(self.name), 
        sender='testsupport@energielenker.de', 
        send_email=True, 
        recipients=[self.raised_by])

def check_for_assigment(self):
    zuweisungen = frappe.db.sql("""SELECT `creation` FROM `tabToDo` WHERE `status` = 'Open' AND `reference_type` = 'Issue' AND `reference_name` = '{0}' ORDER BY `creation` ASC""".format(self.name), as_dict=True)
    if len(zuweisungen) > 0:
        frappe.db.set_value("Issue", self.name, 'letzte_zuweisung', zuweisungen[0].creation, update_modified=False)
        frappe.db.commit()
    else:
        frappe.db.set_value("Issue", self.name, 'letzte_zuweisung', None, update_modified=False)
        frappe.db.commit()
