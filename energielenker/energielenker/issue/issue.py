# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.communication.email import make
from frappe.email import relink
import re

def onload_functions(self, event):
    check_for_assigment(self)

def add_mail_as_description_to_issue(self, event):
    if self.reference_doctype == 'Issue' and self.sent_or_received == 'Received':
        # überprüfung ob E-Mail tatsächlich ein neues Ticket erstellen sollte, oder ob es zu einem existierenden gehört.
        # Die Überprüfung findet anhand der Betreffzeile statt
        betreff_check = parse_subject_line(self)
        if betreff_check.get('correct_linking'):
            if int(frappe.db.get_value("energielenker Settings", "energielenker Settings", "ticket_bestaetigungs_mail")) == 1:
                if int(frappe.db.get_value("Issue", self.reference_name, "mark_for_reply")) == 1:
                    send_issue_creation_notification_to_customer(self.reference_name, self.content, self.sender, self.subject)
                    frappe.db.set_value("Issue", self.reference_name, 'description', self.content, update_modified=False)
                    frappe.db.set_value("Issue", self.reference_name, 'mark_for_reply', 0, update_modified=False)
                    frappe.db.commit()
                else:
                    update_timestamp(self.reference_name)
        else:
            frappe.db.set_value("Issue", self.reference_name, 'description', 'Dieses Ticket wird innert 4 Minuten gelöscht und kann/muss ignoriert werden!', update_modified=False)
            frappe.db.set_value("Issue", self.reference_name, 'subject', 'Löschvormerkung', update_modified=False)
            frappe.db.set_value("Issue", self.reference_name, 'issue_type', 'Reklamation', update_modified=False)
            frappe.db.set_value("Issue", self.reference_name, 'mark_for_deletion', 1, update_modified=False)
            relink(name=self.name, reference_doctype='Issue', reference_name=betreff_check.get('belongs_to'))
            update_timestamp(betreff_check.get('belongs_to'))

def send_issue_creation_notification_to_customer(issue, description, sender, subject):
    subject = subject
    raised_by = sender
    if raised_by:
        make(doctype='Issue', 
        name=issue, 
        content='Vielen Dank für Ihre Nachricht. Ihr Ticket wird bearbeitet.<hr>{0}'.format(description or '-'), 
        subject='{0}: Ihr Ticket ({1}) wird bearbeitet'.format(subject, issue), 
        sender='support@energielenker.de', 
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
    if self.issue_type != 'Reklamation' and self.owner == 'Administrator':
        frappe.db.set_value("Issue", self.name, 'mark_for_reply', 1, update_modified=False)
        frappe.db.commit()

def parse_subject_line(mail):
    regex = r'[ANF]{3}[0-9]{7}'
    results = re.findall(regex, mail.get("subject"))
    if len(results) > 0:
        if results[0] == mail.get("reference_name"):
            return {
                'correct_linking': True
            }
        else:
            return {
                'correct_linking': False,
                'belongs_to': results[0]
            }
    else:
        return {
            'correct_linking': True
        }

def delete_based_on_mark():
    issues = frappe.db.sql("""SELECT `name` FROM `tabIssue` WHERE `mark_for_deletion` = 1""", as_dict=True)
    for issue in issues:
        iss = frappe.get_doc("Issue", issue.name)
        iss.delete()

@frappe.whitelist()
def set_booked_hours(self, event):
    
    affected_issues = []
    
    for time_log in self.time_logs:
        if time_log.issue and time_log.issue not in affected_issues:
            affected_issues.append(time_log.issue)
    
    for issue in affected_issues:
        sql_query = """
            SELECT SUM(`hours`) AS `total_hours`
            FROM `tabTimesheet Detail`
            WHERE `issue` = '{issue}'
            AND `docstatus` = 1;""".format(issue=issue)
    
        total_hours = frappe.db.sql(sql_query, as_dict=True)

        if len(total_hours) > 0:
            booked_hours = total_hours[0].total_hours
        else:
            booked_hours = 0
        
        if not booked_hours:
            booked_hours = 0
        
        frappe.db.set_value("Issue", issue, "booked_hours", booked_hours)
    
    frappe.db.commit()

    return
        
        
def update_timestamp(issue):
    frappe.db.set_value("Issue", issue, 'update_timestamp', frappe.db.get_value("Issue", issue, 'update_timestamp') + 1)
    return

@frappe.whitelist()
def send_invoice_notification(issue):
    recipient = frappe.db.get_value("energielenker Settings", "energielenker Settings", "issue_notification_to")
    
    cc = frappe.db.get_value("energielenker Settings", "energielenker Settings", "issue_notification_cc")

    message = "Guten Tag,<br><br>Anfrage {0} wurde zur Berechnung freigegeben.<br><br>Ich wünsche Ihnen einen schönen Tag.".format(issue)
    
    
    return {
        'recipient': recipient,
        'cc': cc,
        'message': message
        }
