# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024, libracore and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils.data import getdate

'''
    Call to action: https://[System-URL]/api/method/energielenker.api.get_license
    Beispiel JSON (LIVE):
        '{
            "requested_licenses": [
                {
                    "item_energielenker": "A-0000001",
                    "item_customer": "wago_item",
                    "qty": 1
                }
            ]
        }'
    Beispiel JSON (TEST):
        '{
            "test": 1,
            "requested_licenses": [
                {
                    "item_energielenker": "A-0000001",
                    "item_customer": "wago_item",
                    "qty": 1
                }
            ]
        }'
    
    Beispiel CURL (LIVE):
        curl --location --request POST 'https://[System-URL]/api/method/energielenker.api.get_license' \
        --header 'Authorization: token [API-KEY]:[API-SECRET]' \
        --header 'Content-Type: application/json' \
        --header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image=' \
        --data-raw '{
            "requested_licenses": [
                {
                    "item_energielenker": "A-0000001",
                    "item_customer": "kunden_item",
                    "qty": 1
                }
            ]
        }'
    
    Beispiel CURL (TEST):
        curl --location --request POST 'https://[System-URL]/api/method/energielenker.api.get_license' \
        --header 'Authorization: token [API-KEY]:[API-SECRET]' \
        --header 'Content-Type: application/json' \
        --header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image=' \
        --data-raw '{
            "test": 1,
            "requested_licenses": [
                {
                    "item_energielenker": "A-0000001",
                    "item_customer": "kunden_item",
                    "qty": 1
                }
            ]
        }'

        --> INFO:
            Im TEST-Modus wird nur das übermittelte JSON geprüft.
            Es werden KEINE Lizenzen angelegt/versendet.


    Fehler die Validiert werden:
    1. Wurden Parameter als JSON übergeben?
        --> Errorcode 1
    2. Parameter requested_licenses vorhanden?
        --> Errorcode 2
    3. Ist requested_licenses eine Liste?
        --> Errorcode 3
    4. Besitzt requested_licenses mind. 1 Eintrag?
        --> Errorcode 4
    5. Besteht jedes Element in requested_licenses aus:
    5.1 item_energielenker
    5.2 item_customer
    5.3 qty
        --> Errorcode 5
    6. Ist qty > 0?
        --> Errorcode 6
    7. Existiert der Artikel gem. item_energielenker?
        --> Errorcode 7
    8. Besitzt item_energielenker einen Kundenartikel gem. item_customer?
        --> Errorcode 8
    
    Mögliche Responses:
    1. Passed (LIVE):
        http_status_code: 200
        message: [
            {
                "evse_count": 1,
                "Aktivierungscode": "a4a8d7c8c6a72e7"
            },
            {
                "evse_count": 10,
                "Aktivierungscode": "sda8hdiec6a42tt"
            }
        ]
    2. Passed (TEST):
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
def get_license(**kwargs):
    request_failure = check_request(kwargs)
    if request_failure:
        return raise_xxx(400, 'BadRequest', request_failure)
    
    try:
        if 'test' not in kwargs:
            json_formatted_str = json.dumps(kwargs, indent=2)
            lizenz_anfrage = frappe.get_doc({
                "doctype": "Lizenz Anfrage",
                "request": json_formatted_str
            }).insert(ignore_permissions=True)
            voucher_dict = make_voucher(kwargs['requested_licenses'])
        return raise_200(voucher_dict)
    except Exception as err:
        return raise_xxx(500, 'Internal Server Error', err, daten=kwargs)

def check_request(kwargs):
    if len(kwargs) < 2:
        return [1, 'Missing Parameter']
    
    if 'requested_licenses' not in kwargs:
        return [2, 'Missing Parameter requested_licenses']
    
    if isinstance(kwargs['requested_licenses'], list):
        if len(kwargs['requested_licenses']) < 1:
            return [4, 'Missing Requested Licenses']
        
        loop = 0
        for requested_license in kwargs['requested_licenses']:
            if 'item_energielenker' not in requested_license:
                return [5, 'Missing item_energielenker (Index: {0})'.format(loop)]
            if 'item_customer' not in requested_license:
                return [5, 'Missing item_customer (Index: {0})'.format(loop)]
            if 'qty' not in requested_license:
                return [5, 'Missing qty (Index: {0})'.format(loop)]
            if requested_license['qty'] < 1:
                return [6, 'qty (Index: {0}) has to be greater than 0'.format(loop)]
            
            item_combo_error = has_item_combo_error(requested_license['item_energielenker'], requested_license['item_customer'], loop)
            if item_combo_error:
                return item_combo_error
            loop += 1
    else:
        return [3, 'Missing List of requested_licenses']
    
    return False

def has_item_combo_error(item_energielenker, item_customer, loop):
    failure = False
    if not frappe.db.exists("Item", item_energielenker):
        return [7, 'item_energielenker ({0}) does not exist (Index: {1})'.format(item_energielenker, loop)]
    
    item_el = frappe.get_doc("Item", item_energielenker)
    found = False
    for customer_item in item_el.customer_items:
        if customer_item.ref_code == item_customer:
            found = True
    if not found:
        return [8, 'item_customer ({0}) does not match with item_energielenker ({1}) / (Index: {2})'.format(item_customer, item_energielenker, loop)]
    
    return failure

# Success Return
def raise_200(message='OK'):
    frappe.local.response.http_status_code = 200
    frappe.local.response.message = message
    return

# Error Return
def raise_xxx(code, title, message, daten=None):
    frappe.log_error("{0}\n{1}\n{2}\n\n{3}\n\n{4}".format(code, title, message, frappe.utils.get_traceback(), daten or ''), 'get_license Error')
    frappe.local.response.http_status_code = code
    if isinstance(message, list):
        frappe.local.response.message = [title, message]
    else:
        frappe.local.response.message = "{0}: {1}".format(title, message)
    return

def make_voucher(requested_licenses):
	sales_order = make_sales_order(requested_licenses)
	voucher_dict = [
            {
                "evse_count": 1,
                "Aktivierungscode": "a4a8d7c8c6a72e7"
            },
            {
                "evse_count": 10,
                "Aktivierungscode": "sda8hdiec6a42tt"
            }
        ]
	return voucher_dict
	
def make_sales_order(requested_licenses):
	today = getdate()
	api_doc_name = get_api_doc_name()
	api_document = frappe.get_doc("Ladepunkt Key API", api_doc_name)
	customer = frappe.get_doc("Customer", api_document.customer)
	frappe.log_error(customer.ansprechpartner, "customer.ansprechpartner")
	new_doc = frappe.get_doc({
		'doctype': 'Sales Order',
		'customer': api_document.customer,
		'navision_konto': api_document.navision_konto,
		'cost_center': api_document.cost_center,
		'po_no': api_document.po_no,
		'vertriebsgruppe': api_document.vertriebsgruppe,
		'k_ansprechperson': api_document.k_ansprechperson,
		'taxes_and_charges': api_document.taxes_and_charges,
		'po_date': today,
		'ansprechpartner': customer.ansprechpartner,
		'tax_id': customer.tax_id
		})
	
	for license_entry in requested_licenses:
		frappe.log_error(license_entry, 'license_entry')
		lot_size = frappe.db.get_value('Item Customer Detail', {'ref_code': license_entry['item_customer']}, 'size')
		print(lot_size)
		entry = {
			'reference_doctype': 'Sales Order Item',
			'item_code': license_entry['item_energielenker'],
			'delivery_date': today,
			'qty': license_entry['qty'],
			'uom': lot_size
		}
		new_doc.append('items', entry)
	
	new_doc = new_doc.insert(ignore_permissions=True)
	new_doc.submit()
	
	sales_order = new_doc.name
	
	return sales_order
	# ~ return
	
def get_api_doc_name():
	#Berechtigungen API Doctype???
	#Sales Taxes and charges template Sales Order???
	api_doc_name = "API-001"
	return api_doc_name
