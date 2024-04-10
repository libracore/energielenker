# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024, libracore and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils.data import getdate
from erpnext.selling.doctype.sales_order.sales_order import make_purchase_order

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
    9. Ist der User erstellt und in einem "Ladepunkt Key API" Dokument hinterlegt?
    
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
    
    api_user = get_api_doc_name()
    if not api_user:
        return [9, 'Missing API User']
    
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
    frappe.clear_messages()
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
    #create Sales Order
    sales_order = create_sales_order(requested_licenses)
    #Create Purchase Order
    purchase_order = create_purchase_order(sales_order)
    #Create Lizenzgutschein and Voucher Dict
    lizenzgutscheine = create_lizenzgutscheine(purchase_order)
    #create voucher dict as response for api
    voucher_dict = create_voucher_dict(purchase_order)
    #create delivery note
    delivery_note =create_delivery_note(sales_order)

    return voucher_dict
    
def create_sales_order(requested_licenses):
    #get today
    today = getdate()
    
    #get API and Customer Dokument
    api_doc_name = get_api_doc_name()
    api_document = frappe.get_doc("Ladepunkt Key API", api_doc_name)
    customer = frappe.get_doc("Customer", api_document.customer)
    
    #create new Sales Order
    new_doc = frappe.get_doc({
        'doctype': 'Sales Order',
        'customer': api_document.customer,
        'navision_konto': api_document.navision_konto,
        'cost_center': api_document.cost_center,
        'po_no': api_document.po_no,
        'auftrags_projektb': api_document.auftrags_projektb,
        'vertriebsgruppe': api_document.vertriebsgruppe,
        'k_ansprechperson': api_document.k_ansprechperson,
        'shipping_address_name': "",
        'shipping_address': "",
        'taxes_and_charges': api_document.taxes_and_charges,
        'po_date': today,
        'ansprechpartner': customer.ansprechpartner,
        'tax_id': customer.tax_id
        })
    
    #Create Sales Order Items
    supplier = frappe.db.get_value('Ladepunkt Key API Purchase Order', 'Ladepunkt Key API Purchase Order', 'supplier')
    for license_entry in requested_licenses:
        #create Sales Order Items
        lot_size = frappe.db.get_value('Item Customer Detail', {'ref_code': license_entry['item_customer']}, 'size')
        entry = {
            'reference_doctype': 'Sales Order Item',
            'item_code': license_entry['item_energielenker'],
            'delivery_date': today,
            'qty': license_entry['qty'],
            'uom': lot_size,
            'supplier': supplier
        }
        new_doc.append('items', entry)
    
    new_doc = new_doc.insert(ignore_permissions=True)
    new_doc.submit()
    
    #get name of new Sales Order and return it
    sales_order = new_doc.name
    
    return sales_order
    
def get_api_doc_name():
    user = frappe.session.user
    api_doc_name = frappe.db.sql("""
                                    SELECT `parent`
                                    FROM `tabLadepunkt Key API User`
                                    WHERE `user` = '{0}'
                                """.format(user), as_dict=True)
    if len(api_doc_name) > 0:
        return api_doc_name[0].parent
    else:
        return False

def create_purchase_order(sales_order_name):
    #get today
    today = getdate()
    
    #get Sales Order and settings
    sales_order_doc = frappe.get_doc('Sales Order', sales_order_name)
    po_settings = frappe.get_doc('Ladepunkt Key API Purchase Order', 'Ladepunkt Key API Purchase Order')
    
    #create new Purchase Order
    new_po_doc = frappe.get_doc({
        'doctype': 'Purchase Order',
        'supplier': po_settings.supplier,
        'schedule_date': today,
        'voraussichtlicher_liefertermin': today,
        'sales_order': sales_order_doc.name,
        'shipping_address_name': "",
        'shipping_address': "",
        'ansprechpartner': po_settings.ansprechpartner,
        'k_ansprechperson': po_settings.k_ansprechperson
        })
    
    for item in sales_order_doc.items:
        entry = {
            'reference_doctype': 'Purchase Order Item',
            'item_code': item.item_code,
            'schedule_date': today,
            'item_name': item.item_name,
            'qty': item.qty,
            'uom': item.uom,
            'sales_order': sales_order_doc.name,
            'cost_center': po_settings.cost_center
        }
        new_po_doc.append('items', entry)
    
    new_po_doc = new_po_doc.insert(ignore_permissions=True)
    new_po_doc.submit()
    
    #get name of new Purchase Order and return it
    purchase_order = new_po_doc.name
    
    return purchase_order

def create_lizenzgutscheine(purchase_order_name):
    #get Purchase Order
    purchase_order_doc = frappe.get_doc('Purchase Order', purchase_order_name)
    
    item_count = 0
    
    for item in purchase_order_doc.items:
        item_count += 1
        position_count = 1
        for voucher in range(int(item.qty)):
            lizenzgutschein = frappe.get_doc({
                'doctype': 'Lizenzgutschein',
                'purchase_order': purchase_order_name,
                'positions_nummer': '{item}.{position}'.format(item=item_count, position=position_count),
                'position_id': item.name,
                'evse_count': frappe.get_value("UOM", item.uom, "evse_count")
                })
        
            lizenzgutschein = lizenzgutschein.insert(ignore_permissions=True)
            position_count += 1
                
            
    return

def create_voucher_dict(purchase_order_name):
    voucher_dict = frappe.db.sql("""
                                SELECT
                                    `evse_count`,
                                    `lizenzgutschein` AS `Aktivierungscode`
                                FROM
                                    `tabLizenzgutschein`
                                WHERE
                                    `purchase_order` = '{po}'
                                ORDER BY
                                    `evse_count`""".format(po=purchase_order_name), as_dict=True)
    return voucher_dict

def create_delivery_note(sales_order_name):
    #get today
    today = getdate()
    
    #get API Doc, Sales Order and Customer
    api_doc_name = get_api_doc_name()
    api_document = frappe.get_doc("Ladepunkt Key API", api_doc_name)
    sales_order_doc = frappe.get_doc('Sales Order', sales_order_name)
    customer = frappe.get_doc("Customer", api_document.customer)

    
    #create new Delivery Note
    new_dn = frappe.get_doc({
        'doctype': 'Delivery Note',
        'customer': api_document.customer,
        'k_ansprechperson': api_document.k_ansprechperson,
        'po_no': api_document.po_no,
        'taxes_and_charges': api_document.taxes_and_charges,
        'ansprechpartner': customer.ansprechpartner
        })
    
    for item in sales_order_doc.items:
        entry = {
            'reference_doctype': 'Delivery Note Item',
            'item_code': item.item_code,
            'qty': item.qty,
            'uom': item.uom,
            'against_sales_order': sales_order_name,
            'so_detail': item.name,
            'vk_wert': item.amount
        }
        new_dn.append('items', entry)
    
    new_dn = new_dn.insert(ignore_permissions=True)
    new_dn.submit()
    
    #get name of new Purchase Order and return it
    delivery_note = new_dn.name
    
    return delivery_note
