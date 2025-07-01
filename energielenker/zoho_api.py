# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025, libracore and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils.__init__ import validate_email_address

'''
    Create Ticket, Call to action: https://[System-URL]/api/method/energielenker.zoho_api.create_ticket
    Update Ticket, Call to action: https://[System-URL]/api/method/energielenker.zoho_api.update_ticket
    Beispiel JSON (LIVE):
        '{
            "issue":
                {
                    "zoho_id": [ZOHO ID],
                    "subject": [SUBJECT],
                    "customer": [CUSTOMER],
                    "contact_customer": [CONTACT],
                    "address": [ADDRESS]",
                    "raised_by": [RAISED BY E-MAIL],
                    "priority": [PRIORITY],
                    "issue_type": [ISSUE TYPE],
                    "themenfeld": [THEMENFELD],
                    "sales_order": [SALES ORDER]
                }
        }'
    Beispiel JSON (TEST):
        '{
            "test": 1,
            "issue":
                {
                    "zoho_id": [ZOHO ID],
                    "subject": [SUBJECT],
                    "customer": [CUSTOMER],
                    "contact_customer": [CONTACT],
                    "address": [ADDRESS]",
                    "raised_by": [RAISED BY E-MAIL],
                    "priority": [PRIORITY],
                    "issue_type": [ISSUE TYPE],
                    "themenfeld": [THEMENFELD],
                    "sales_order": [SALES ORDER]
                }
        }'
    
    Beispiel CURL (LIVE):
        curl --location --request POST 'http://[System-URL]/api/method/energielenker.zoho_api.create_ticket'
        --header 'Authorization: token d7e94428c2e66f9:3c0262a2d008047'
        --header 'Content-Type: application/json'
        --header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image='
        --data-raw '{
            "issue":
                {
                    "zoho_id": [ZOHO ID],
                    "subject": [SUBJECT],
                    "customer": [CUSTOMER],
                    "contact_customer": [CONTACT],
                    "address": [ADDRESS]",
                    "raised_by": [RAISED BY E-MAIL],
                    "priority": [PRIORITY],
                    "issue_type": [ISSUE TYPE],
                    "themenfeld": [THEMENFELD],
                    "sales_order": [SALES ORDER]
                }
        }'
    
    Beispiel CURL (TEST):
        curl --location --request POST 'http://[System-URL]/api/method/energielenker.zoho_api.create_or_update_ticket'
        --header 'Authorization: token d7e94428c2e66f9:3c0262a2d008047'
        --header 'Content-Type: application/json'
        --header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image='
        --data-raw '{
            "test": 1,
            "issue":
                {
                    "zoho_id": [ZOHO ID],
                    "subject": [SUBJECT],
                    "customer": [CUSTOMER],
                    "contact_customer": [CONTACT],
                    "address": [ADDRESS]",
                    "raised_by": [RAISED BY E-MAIL],
                    "priority": [PRIORITY],
                    "issue_type": [ISSUE TYPE],
                    "themenfeld": [THEMENFELD],
                    "sales_order": [SALES ORDER]
                }
        }'

        --> INFO:
            Überflüssige Parameter werden ignoriert
            Im TEST-Modus wird nur das übermittelte JSON geprüft.
            Es werden KEINE Tickets erstellt oder aktualisiert.


    Fehler die Validiert werden:
    1. Parameter issue vorhanden?
        --> Errorcode 1
    2. Parameter zoho_id in issue vorhanden?
        --> Errorcode 2
    3. create_ticket: Wurden alle zwingenden Felder übermittelt?
        --> Errorcode 3
        --> Zwingende Felder: subject, customer, contact_customer, address, raised_by, status, issue_type, themenfeld, sales_order, assigned_to
    4. update_ticket: Sind andere parapeter als zoho_id vorhanden?
        --> Errorcode 4
    5. Sind übermittelte Kunde, Addresse, Konakt, Priorität, Tickettyp, Sales Order, Themenfeld, Status und Assigned To existierende Dokumente oder Optionen?
    --> Errorcode 5
    6. Ist die als "raised_by" übermittelte eine valide E-Mail Adresse?
    --> Errorcode 6
    7. create_ticket: Existiert bereits ein Ticket mit der angegebenen ZOHO ID?
    --> Errorcode 7

    
    Mögliche Responses:
    1. Passed:
        http_status_code: 200
        message: "OK"
    
    2. Failed:
    2.1 Validierungsfehler:
        http_status_code: 400
        message: ["BadRequest", [Errorcode, Detailinformationen]]
    2.2 Sonstige Fehler:
        http_status_code: 500
        message: "Internal Server Error: Detailinformationen"
'''

@frappe.whitelist()
def create_ticket(**kwargs):
    request_failure = check_request(kwargs)
    
    if request_failure:
        return raise_xxx(400, 'BadRequest', request_failure)
    
    try:
        if 'test' not in kwargs:
            new_issue = create_issue(kwargs)
            return raise_200("OK")
        else:
            return raise_200()
    except Exception as err:
        return raise_xxx(500, 'Internal Server Error', err, daten=kwargs)
    
    
@frappe.whitelist()
def update_ticket(**kwargs):
    request_failure = check_request(kwargs)
    
    if request_failure:
        return raise_xxx(400, 'BadRequest', request_failure)
    
    try:
        if 'test' not in kwargs:
            issue = update_issue(kwargs)
            return raise_200("OK")
        else:
            return raise_200()
    except Exception as err:
        return raise_xxx(500, 'Internal Server Error', err, daten=kwargs)
    
def check_request(kwargs):
    #Check if Parameter Issue is given
    if not kwargs.get('issue'):
        return [1, 'Missing Parameter Issue']
    
    #Check if ZOHO ID is given
    if not kwargs["issue"].get('zoho_id'):
        return [2, 'Missing Parameter zoho_id']
        
    if kwargs["cmd"] == "energielenker.zoho_api.create_ticket":
        #Check Mandators fields
        if "subject" not in kwargs["issue"]:
            return [3, 'Subject is Missing']
            
        if "customer" not in kwargs["issue"]:
            return [3, 'Customer is Missing']
            
        if "contact_customer" not in kwargs["issue"]:
            return [3, 'Customer Contact is Missing']
        
        if "address" not in kwargs["issue"]:
            return [3, 'Customer address is Missing']
        
        if "raised_by" not in kwargs["issue"]:
            return [3, 'Raised by is Missing']
        
        if "status" not in kwargs["issue"]:
            return [3, 'Status is Missing']
        
        if "issue_type" not in kwargs["issue"]:
            return [3, 'Issue type is Missing']
        
        if "themenfeld" not in kwargs["issue"]:
            return [3, 'Themenfeld is Missing']
        
        if "sales_order" not in kwargs["issue"]:
            return [3, 'Sales Order is Missing']
        
        if "assigned_to" not in kwargs["issue"]:
            return [3, 'Assigned To is Missing'] 
        
        #Check if ZOHO ID is already existing
        existing_issue = frappe.db.exists("Issue", {'zoho_id': kwargs["issue"]["zoho_id"]})
        if existing_issue:
            return [7, 'ZOHO ID {0} already exists'.format(kwargs["issue"]["zoho_id"])]
    else:
        if len(kwargs['issue']) < 2:
            return [4, 'Nothing to Update']
        
    if "customer" in kwargs["issue"]:
        customer = frappe.db.exists("Customer", kwargs["issue"]["customer"])
        if not customer:
            return [5, 'Customer not existing']
        
    if "contact_customer" in kwargs["issue"]:
        contact = frappe.db.exists("Contact", kwargs["issue"]["contact_customer"])
        if not contact:
            return [5, 'Contact not existing']
    
    if "address" in kwargs["issue"]:
        address = frappe.db.exists("Address", kwargs["issue"]["address"])
        if not address:
            return [5, 'Adress not existing']
        
    if "priority" in kwargs["issue"]:
        priority = frappe.db.exists("Issue Priority", kwargs["issue"]["priority"])
        if not priority:
            return [5, 'Priority not existing']
    
    if "issue_type" in kwargs["issue"]:
        issue_type = frappe.db.exists("Issue Type", kwargs["issue"]["issue_type"])
        if not issue_type:
            return [5, 'Issue Type not existing']
    
    if "sales_order" in kwargs["issue"]:
        sales_order = frappe.db.exists("Sales Order", kwargs["issue"]["sales_order"])
        if not sales_order:
            return [5, 'Sales Order not existing']
    
    if "raised_by" in kwargs["issue"]:
        raised_by = validate_email_address(kwargs["issue"]["raised_by"])
        if not raised_by:
            return [6, 'Raised by is not a valid E-Mail address']
    
    if "themenfeld" in kwargs["issue"]:
        themenfeld = validate_options("themenfeld", kwargs["issue"]["themenfeld"])
        if not themenfeld:
            return [6, 'Themenfeld not existing']
    
    if "status" in kwargs["issue"]:
        status = validate_options("status", kwargs["issue"]["status"])
        if not status:
            return [6, 'Status not existing']
    
    if "assigned_to" in kwargs["issue"]:
        assigned_to = frappe.db.exists("User", {'email': kwargs["issue"]["assigned_to"]})
        if not assigned_to:
            return [6, 'Assigned to User not existing']
    
    return False

# Success Return
def raise_200(message='OK'):
    frappe.clear_messages()
    frappe.local.response.http_status_code = 200
    frappe.local.response.message = message
    return

# Error Return
def raise_xxx(code, title, message, daten=None):
    frappe.log_error("{0}\n{1}\n{2}\n\n{3}\n\n{4}".format(code, title, message, frappe.utils.get_traceback(), daten or ''), 'zoho_api Error')
    frappe.local.response.http_status_code = code
    if isinstance(message, list):
        frappe.local.response.message = [title, message]
    else:
        frappe.local.response.message = "{0}: {1}".format(title, message)
    return

def create_issue(kwargs):
    new_issue = frappe.get_doc({'doctype': "Issue"})
    new_issue.update(kwargs["issue"])
    new_issue.insert()
    
    #Add assigned to
    if kwargs["issue"]["assigned_to"]:
        create_todo({'owner': kwargs["issue"]["assigned_to"], 'reference_type': "Issue", 'reference_name': new_issue.name, 'description': kwargs["issue"]["subject"]})
    
    return new_issue.name

def update_issue(kwargs):
    issue = frappe.get_doc("Issue", {'zoho_id': kwargs['issue'].get('zoho_id')})
    issue.update(kwargs["issue"])
    issue.save()
    return issue.name

def validate_options(target_field, value):
    meta = frappe.get_meta("Issue")
    field = meta.get_field(target_field)
    options = field.options.split("\n") if field and field.options else []
    
    if value in options:
        return value
    else:    
        return None

def create_todo(update_dict):
    new_todo = frappe.get_doc({'doctype': "ToDo"})
    new_todo.update(update_dict)
    new_todo.insert(ignore_permissions=True)
    return
