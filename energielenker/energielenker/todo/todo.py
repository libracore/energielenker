# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.communication.email import make

def check_for_assigment(self, event):
    if self.reference_type == 'Issue' and self.reference_name:
        zuweisungen = frappe.db.sql("""SELECT `creation` FROM `tabToDo` WHERE `status` = 'Open' AND `reference_type` = 'Issue' AND `reference_name` = '{0}' ORDER BY `creation` ASC""".format(self.reference_name), as_dict=True)
        if len(zuweisungen) > 0:
            frappe.db.set_value("Issue", self.reference_name, 'letzte_zuweisung', zuweisungen[0].creation)
            frappe.db.commit()
        else:
            frappe.db.set_value("Issue", self.reference_name, 'letzte_zuweisung', None)
            frappe.db.commit()

def reminder_email():
    #get all open To Dos
    open_todos = frappe.db.sql("""
                                SELECT
                                    `tabToDo`.`owner` AS `owner`,
                                    `tabIssue`.`priority` AS `priority`,
                                    `tabToDo`.`date` AS `date`,
                                    `tabToDo`.`description` AS `description`,
                                    `tabToDo`.`reference_name` AS `reference_name`
                                FROM
                                    `tabToDo`
                                LEFT JOIN
                                    `tabIssue` ON `tabToDo`.`reference_name` = `tabIssue`.`name`
                                WHERE
                                    `tabToDo`.`status` = 'Open'
                                AND
                                    `tabIssue`.`status` = 'Open'
                                AND
                                    `tabToDo`.`reference_type` = 'Issue'
                                ORDER BY
                                    `tabToDo`.`owner` ASC""", as_dict=True)
    
    if len(open_todos) > 0:
        #prepare E-Mail Data
        email_data = []
        last_owner = None
        message = None
        for todo in open_todos:
            if todo.get('owner') != last_owner:
                if message and last_owner:
                    email_data.append({'owner': last_owner, 'message': message})
                message = "Guten Tag,<br><br>Sie haben folgende offene Aufgaben:<br><br><b>Referenz:</b> {0}, <b>Priorität:</b> {1}, <b>Deadline:</b> {2}, <b>Aufgabe:</b> {3}".format(todo.get('reference_name') or "-", todo.get('priority') or "-", todo.get('date') or "-", todo.get('description') or "-")
            else:
                message += "<br><br><b>Referenz:</b> {0}, <b>Priorität:</b> {1}, <b>Deadline:</b> {2}, <b>Aufgabe:</b> {3}".format(todo.get('reference_name') or "-", todo.get('priority') or "-", todo.get('date') or "-", todo.get('description') or "-")
            last_owner = todo.get('owner')
        
        #send E-Mails
        for email in email_data:
            #For testing reason
            if email.get('owner') == "ivan.lochbihler@libracore.com" or email.get('owner') == "anja.friedrich@libracore.com":
                make(
                     recipients = email.get('owner'),
                     sender = "no-reply@energielenker.de",
                     subject = "Offene Aufgaben",
                     content = email.get('message'),
                     send_email = True
                )
            
    return
