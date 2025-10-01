# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025, libracore and contributors
# For license information, please see license.txt

import frappe
import json
import requests
from frappe.utils.__init__ import validate_email_address
from frappe.utils import now_datetime
from frappe.utils.data import cint

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
            Im TEST-Modus wird nur das übermittelte JSON geprüft dabei werden KEINE Tickets erstellt oder aktualisiert.


    Fehler die Validiert werden:
    1. Parameter issue vorhanden?
        --> Errorcode 1
    2. Parameter zoho_id in issue vorhanden?
        --> Errorcode 2
    3. create_ticket: Wurden alle zwingenden Felder übermittelt?
        --> Errorcode 3
        --> Zwingende Felder: subject, customer, contact_customer, address, raised_by, status, issue_type, themenfeld, assigned_to
    4. update_ticket: Sind andere parapeter als zoho_id vorhanden?
        --> Errorcode 4
    5. Sind übermittelte Kunde, Addresse, Konakt, Priorität, Tickettyp, Sales Order, Themenfeld, Status und Assigned To existierende Dokumente oder Optionen?
    --> Errorcode 5
    6. Ist die als "raised_by" übermittelte eine valide E-Mail Adresse?
    --> Errorcode 6
    7. Existiert bereits ein Ticket mit der angegebenen ZOHO ID?
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
    
    if not kwargs["issue"].get('zoho_data_id'):
        return [2, 'Missing Parameter zoho_data_id']
    
    if kwargs["cmd"] == "energielenker.zoho_api.create_ticket":
        #Check Mandatory fields and ZOHO ID
        api_mandatory_fields_missing = check_api_mandatory_fields(kwargs)
        if api_mandatory_fields_missing:
            return api_mandatory_fields_missing
        
        #Check if ZOHO ID is already existing
        existing_issue = frappe.db.exists("Issue", {'zoho_data_id': kwargs["issue"]["zoho_data_id"]})
        if existing_issue:
            return [7, 'ZOHO DATA ID {0} already exists'.format(kwargs["issue"]["zoho_data_id"])]
    else:
        if len(kwargs['issue']) < 2:
            return [4, 'Nothing to Update']
        
        #Check if ZOHO ID is already existing
        existing_issue = frappe.db.exists("Issue", {'zoho_id': kwargs["issue"]["zoho_id"]})
        if not existing_issue:
            return [7, 'ZOHO ID {0} does not exist'.format(kwargs["issue"]["zoho_id"])]
        
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
        kwargs["issue"]["status"] = translate_status(kwargs["issue"]["status"])
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

def check_api_mandatory_fields(kwargs):
    api_mandatory_fields = [
        ["subject", 3, 'Subject is Missing'],
        ["customer", 3, 'Customer is Missing'],
        ["contact_customer", 3, 'Customer Contact is Missing'],
        ["address", 3, 'Customer address is Missing'],
        ["raised_by", 3, 'Raised by is Missing'],
        ["status", 3, 'Status is Missing'],
        ["issue_type", 3, 'Issue type is Missing'],
        ["themenfeld", 3, 'Themenfeld is Missing'],
        ["assigned_to", 3, 'Assigned To is Missing']
    ]
    
    for api_mandatory_field in api_mandatory_fields:
        if api_mandatory_field[0] not in kwargs["issue"]:
            return [api_mandatory_field[1], api_mandatory_field[2]]
    
    return False

def send_request(endpoint, json_object, token, is_update=False, zoho_id=None, test=False):
    url = get_request_url(endpoint, is_update, zoho_id)
    
    headers = {"Authorization": "Zoho-oauthtoken {0}".format(token), "Content-Type": "application/json"}
    
    if is_update:
        if endpoint == "address":
            api_connection = requests.patch(url, json = json_object, headers = headers)
        else:
            api_connection = requests.put(url, json = json_object, headers = headers)
    else:
        api_connection = requests.post(url, json = json_object, headers = headers)
    
    if "errorCode" in api_connection:
        frappe.log_error("ZOHO API ERROR", "errorCode: {0}<br>message: {1}<br>endpoint: {2}<br>sent_object: {3}".format(api_connection.get('errorCode'), api_connection.get('message'), json_object))
    else:
        if endpoint == "issue":
            return api_connection
        else:
            return api_connection.json()

def get_request_url(endpoint, is_update, zoho_id=None):
    url = "https://desk.zoho.eu/api/v1/"
    
    try:
        mapper = {
            'contact': 'contacts',
            'address': 'cm_adressen',
            'issue': 'closeTickets',
            'customer': 'accounts'
        }
        url += mapper[endpoint]
    except Exception as err:
        frappe.log_error("ZOHO API ERROR", "Error occured while mapping the Endpoint: {0}".format(err))
    
    if is_update:
        if not zoho_id:
            frappe.log_error("ZOHO API ERROR", "ZOHO ID missing for {0} Update".format(endpoint))
            return
        url += "/{0}".format(zoho_id)
        
    return url

def get_new_token(test=False):
    url = "https://accounts.zoho.eu/oauth/v2/token?"
    client_id = frappe.get_value("energielenker Settings", "energielenker Settings", "zoho_client_id")
    client_secret = frappe.get_value("energielenker Settings", "energielenker Settings", "zoho_client_secret")
    if test:
        refresh_token = frappe.get_value("energielenker Settings", "energielenker Settings", "zoho_sandbox_refresh_token")
    else:
        refresh_token = frappe.get_value("energielenker Settings", "energielenker Settings", "zoho_refresh_token")
    
    data = {
            'grant_type': "refresh_token",
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
            }
    
    token = requests.post(url, data=data)
    if token:
        return(token.json())
    else:
        frappe.log_error("ZOHO API ERROR", "Error in getting new authorization Token: {0}".format(token))

#Nightly ZOHO Update
@frappe.whitelist()
def update_zoho():
    try:
        #get ne API Token
        token = get_new_token()
        
        #get Last Sync Time
        timestamp = frappe.get_value("energielenker Settings", "energielenker Settings", "zoho_timestamp")
        
        #Get updated or created Customers
        customer_data = frappe.db.sql("""
                                        SELECT
                                            `name`,
                                            `zoho_id`
                                        FROM
                                            `tabCustomer`
                                        WHERE
                                            `modified` > '{ts}'
                                        AND
                                            `disabled` = 0
                                        AND
                                            `blocked_customer` = 0;""".format(ts=timestamp), as_dict=True)
        
        if len(customer_data) > 0:
            for customer in customer_data:
                #prepare JSON
                customer_doc = frappe.get_doc("Customer", customer.get('name'))
                
                json = {
                            "accountName": customer_doc.get('customer_name'),
                            "cf": {
                                "cf_kundennummer": customer_doc.get('navision_nr')
                            }
                        }
                #Send request
                if customer.get('zoho_id'):
                    request = send_request("customer", json, token.get('access_token'), is_update=True, zoho_id=customer.get('zoho_id'))
                else:
                    request = send_request("customer", json, token.get('access_token'))
                    #Update Customer
                    frappe.db.set_value("Customer", customer.get('name'), "zoho_id", request.get('id'))
        
        #Get updated or created Contacts
        contact_data = frappe.db.sql("""
                        SELECT
                            `name`,
                            `zoho_id`
                        FROM
                            `tabContact`
                        WHERE
                            `modified` > '{ts}';""".format(ts=timestamp), as_dict=True)
        
        if len(contact_data) > 0:
            for contact in contact_data:
                #prepare JSON
                contact_doc = frappe.get_doc("Contact", contact.get('name'))
                #Check if Contact belongs to Customer
                customer_name = None
                if len(contact_doc.links) > 0:
                    for link in contact_doc.links:
                        if link.get('link_name') and link.get('link_doctype') == "Customer":
                            customer_name = link.get('link_name')
                            break
                if customer_name:
                    customer_zoho_id = frappe.get_value("Customer", customer_name, "zoho_id")
                    mobile = None
                    phone= None
                    if len(contact_doc.phone_nos) > 0:
                        for phone_no in contact_doc.phone_nos:
                            if phone_no.is_primary_phone:
                                phone = phone_no.phone
                            elif phone_no.is_primary_mobile_no:
                                mobile = phone_no.phone
                    
                    json = {
                                "firstName": contact_doc.get('last_name'),
                                "lastName": contact_doc.get('first_name'),
                                "email": contact_doc.get('email_id'),
                                "phone": phone,
                                "mobile": mobile,
                                "accountId": customer_zoho_id,
                                "cf" : {
                                    "cf_nutzertyp" : "Lobas Handelspartner",
                                    "cf_erp_next_kontakt_id": contact_doc.get('name')
                                }
                            }
                    #Send request
                    if contact.get('zoho_id'):
                        request = send_request("contact", json, token.get('access_token'), is_update=True, zoho_id=contact.get('zoho_id'))
                    else:
                        request = send_request("contact", json, token.get('access_token'))
                        #Update Contact
                        frappe.db.set_value("Contact", contact.get('name'), "zoho_id", request.get('id'))
        
        #Get updated or created Addresses
        address_data = frappe.db.sql("""
                                        SELECT
                                            `name`,
                                            `zoho_id`
                                        FROM
                                            `tabAddress`
                                        WHERE
                                            `modified` > '{ts}'
                                        AND
                                            `disabled` = 0;""".format(ts=timestamp), as_dict=True)
        
        if len(address_data) > 0:
            for address in address_data:
                #prepare JSON
                address_doc = frappe.get_doc("Address", address.get('name'))
                
                #Check if Contact belongs to Customer
                customer_name = None
                if len(address_doc.links) > 0:
                    for link in address_doc.links:
                        if link.get('link_name') and link.get('link_doctype') == "Customer":
                            customer_name = link.get('link_name')
                            break
                if customer_name:
                    json = {
                                "name": address_doc.get('name'),
                                "cf": {
                                    "cf_strasse": address_doc.get('address_line1'),
                                    "cf_hausnummer": address_doc.get('hausnummer'),
                                    "cf_ort": "{0} {1}".format(address_doc.get('plz'), address_doc.get('city'))
                                }
                            }
                    #Send request
                    if address.get('zoho_id'):
                        request = send_request("address", json, token.get('access_token'), is_update=True, zoho_id=address.get('zoho_id'))
                    else:
                        request = send_request("address", json, token.get('access_token'))
                        #Update Address
                        frappe.db.set_value("Address", address.get('name'), "zoho_id", request.get('id'))
        
        #Get closed Tickets
        issue_data = frappe.db.sql("""
                                        SELECT
                                            `name`,
                                            `zoho_id`,
                                            `zoho_data_id`
                                        FROM
                                            `tabIssue`
                                        WHERE
                                            `modified` >= '{ts}'
                                        AND
                                            `status` = 'Closed';""".format(ts=timestamp), as_dict=True)
        
        if len(issue_data) > 0:
            #prepare JSON
            closed_issues = []
            for issue in issue_data:
                if issue.get('zoho_data_id'):
                    closed_issues.append(issue.get('zoho_data_id'))
            frappe
            json = {
                        "ids": closed_issues,
                    }
            #Send request
            request = send_request("issue", json, token.get('access_token'))
        
        #Update Timestamp
        timestamp = frappe.set_value("energielenker Settings", "energielenker Settings", "zoho_timestamp", now_datetime())
        frappe.db.commit()
        
        return
    except Exception as Err:
        frappe.log_error(str(Err), "ZOHO API ERROR")

def translate_status(status):
    try:
        mapper = {
            'Offen': "Open",
            'Anhalten': "Hold",
            'Eskaliert': "Escalated",
            'Geschlossen': "Closed",
            'In Bearbeitung': "In Bearbeitung",
            'Warten auf Rückmeldung': "Warte auf Rückantwort",
            'Jira Ticket Anhalten': "Hold"
        }
        return mapper[status]
    except Exception as err:
        frappe.log_error("Status nicht gefunden", str(err))
