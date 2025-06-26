# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025, libracore and contributors
# For license information, please see license.txt

import frappe
import json

'''
    Call to action: https://[System-URL]/api/method/energielenker.api.get_license
    Beispiel JSON (LIVE):
        '{
            "issue":
                {
                    "zoho_id": "ANF0002627",
                    "subject": [Ticket Subject],
                    "customer": [Customer]
                }
        }'
    Beispiel JSON (TEST):
        '{
            "test": 1,
            "issue":
                {
                    "zoho_id": "ANF0002627",
                    "subject": [Ticket Subject],
                    "customer": [Customer]
                }
        }'
    
    Beispiel CURL (LIVE):
        curl --location --request POST 'http://[System-URL]/api/method/energielenker.zoho_api.create_or_update_ticket'
        --header 'Authorization: token d7e94428c2e66f9:3c0262a2d008047'
        --header 'Content-Type: application/json'
        --header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image='
        --data-raw '{
            "issue":
                {
                    "zoho_id": "ANF0002627",
                    "subject": [Ticket Subject],
                    "customer": [Customer]
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
                    "zoho_id": "ANF0002627",
                    "subject": [Ticket Subject],
                    "customer": [Customer]
                }
        }'

        --> INFO:
            Im TEST-Modus wird nur das übermittelte JSON geprüft.
            Es werden KEINE Tickets erstellt oder aktualisiert.


    Fehler die Validiert werden:
    1. Parameter issue vorhanden?
        --> Errorcode 1
    2. Parameter zoho_id vorhanden?
        --> Errorcode 2
    3. Sind andere parapeter als zoho_id vorhanden?
        --> Errorcode 3
    # ~ 4. Besitzt requested_licenses mind. 1 Eintrag?
        # ~ --> Errorcode 4
    # ~ 5. Besteht jedes Element in requested_licenses aus:
    # ~ 5.1 item_energielenker
    # ~ 5.2 item_customer
    # ~ 5.3 qty
    # ~ 5.4 reference
        # ~ --> Errorcode 5
    # ~ 6. Ist qty > 0?
        # ~ --> Errorcode 6
    # ~ 7. Existiert der Artikel gem. item_energielenker?
        # ~ --> Errorcode 7
    # ~ 8. Besitzt item_energielenker einen Kundenartikel gem. item_customer?
        # ~ --> Errorcode 8
    # ~ 9. Ist der User erstellt und in einem "Ladepunkt Key API" Dokument hinterlegt?
    
    # ~ Mögliche Responses:
    # ~ 1. Passed (LIVE):
        # ~ http_status_code: 200
        # ~ message: [
            # ~ {
                # ~ "evse_count": 1,
                # ~ "Aktivierungscode": "a4a8d7c8c6a72e7"
            # ~ },
            # ~ {
                # ~ "evse_count": 10,
                # ~ "Aktivierungscode": "sda8hdiec6a42tt"
            # ~ }
        # ~ ]
    # ~ 2. Passed (TEST):
        # ~ http_status_code: 200
        # ~ message: "OK"
    
    # ~ 2. Failed:
    # ~ 2.1 Validierungsfehler:
        # ~ http_status_code: 400
        # ~ message: ["BadRequest", [Errorcode, Detailinformationen]]
    # ~ 2.2 Sonstige Fehler:
        # ~ http_status_code: 500
        # ~ message: "Internal Server Error: Detailinformationen"
'''

@frappe.whitelist()
def create_or_update_ticket(**kwargs):
    request_failure = check_request(kwargs)
    
    if request_failure:
            return raise_xxx(400, 'BadRequest', request_failure)
    
    frappe.log_error(kwargs, "kwargs")
    
    
def check_request(kwargs):
    if not kwargs.get('issue'):
        return [1, 'Missing Parameter Issue']
    
    if not kwargs["issue"].get('zoho_id'):
        return [2, 'Missing Parameter ZOHO ID']
        
    if len(kwargs["issue"]) < 2:
        return [3, 'Missing updated Parameter']
        
    #Gibt es den angegebenen Kunden?
    #Gibt es den angegebenen Kontakt?
    #Gibt es die angegebene Adresse?
    #Gibt es die angegebene Sales Order?
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
