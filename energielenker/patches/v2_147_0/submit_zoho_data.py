import frappe
from frappe.modules.utils import sync_customizations
from energielenker.zoho_api import send_request, get_new_token

#POINTS TO BE AMENDED: LINK CONTACTS WITH CUSTOMERS, CONTACTS AND ADDRESS ONLY TO BE SUBMITTED IF THEY BELONG TO A CUSTOMER
def execute():
    sync_customizations("energielenker")
    
    #Get Token
    token = get_new_token()
    
    #Submit Contacts
    contacts = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `last_name`,
                                    `first_name`,
                                    `email_id`
                                FROM
                                    `tabContact`;""", as_dict=True)
    
    for contact in contacts:
        contact_doc = frappe.get_doc("Contact", contact.get('name'))
        
        mobile = None
        phone= None
        if len(contact_doc.phone_nos) > 0:
            for phone_no in contact_doc.phone_nos:
                if phone_no.is_primary_phone:
                    phone = phone_no.phone
                elif phone_no.is_primary_mobile_no:
                    mobile = phone_no.phone
        
        json = {
                    "firstName": contact.get('last_name'),
                    "lastName": contact.get('first_name'),
                    "email": contact.get('email_id'),
                    "phone": phone,
                    "mobile": mobile,
                    "cf" : {
                        "cf_nutzertyp" : "Lobas Handelspartner",
                        "cf_erp_next_kontakt_id": contact_doc.get('name')
                    }
                }
        
        try:
            request = send_request("contact", json, token.get('access_token'))
            frappe.db.set_value("Contact", contact.get('name'), "zoho_id", request.get('id'))
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
    
    #Submit Addresses
    addresses = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `address_title`,
                                    `address_line1`,
                                    `hausnummer`,
                                    `plz`,
                                    `city`
                                FROM
                                    `tabAddress`;""", as_dict=True)
    
    for address in addresses:
        json = {
                    "name": address.get('name'),
                    "cf": {
                        "cf_strasse": address.get('address_line1'),
                        "cf_hausnummer": address.get('hausnummer'),
                        "cf_ort": "{0} {1}".format(address.get('plz'), address.get('city'))
                    }
                }
        
        try:
            request = send_request("address", json, token.get('access_token'))
            frappe.db.set_value("Address", address.get('name'), "zoho_id", request.get('id'))
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
    
    #Submit Customers
    customers = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `customer_name`,
                                    `navision_nr`
                                FROM
                                    `tabCustomer`;""", as_dict=True)
    
    for customer in customers:
        json = {
                    "accountName": customer.get('customer_name'),
                    "cf": {
                        "cf_kundennummer": customer.get('navision_nr')
                    }
                }
        
        try:
            request = send_request("customer", json, token.get('access_token'))
            frappe.db.set_value("Customer", customer.get('name'), "zoho_id", request.get('id'))
            frappe.log_error(request, "request")
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
    
    timestamp = frappe.set_value("energielenker Settings", "energielenker Settings", "zoho_timestamp", now_datetime())
