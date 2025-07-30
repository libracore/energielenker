import frappe
from frappe.modules.utils import sync_customizations
from energielenker.zoho_api import send_request, get_new_token

def execute():
    sync_customizations("energielenker")
    
    #Get Token
    token = get_new_token()
    # ~ token = "1000.00cdba87ee043f6c302e68c76d197ba2.60afc394dffd08545952fb2e6f329fc4" #to be removed after testing
    
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
        json = {
                    "firstName": contact.get('last_name'),
                    "lastName": contact.get('first_name'),
                    "email": contact.get('email_id'),
                    "cf" : {
                        "cf_nutzertyp" : "Lobas Handelspartner" #To be defined where "cf_nutzertyp" comes from
                    }
                }
        
        try:
            request = send_request("contact", json, token)#.get('access_token')) <- To be changed after Testing
            frappe.db.set_value("Contact", contact.get('name'), "zoho_id", request.get('id'))
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
        
        break #to be removed after testing
    
    
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
                    "name": address.get('address_title'),
                    "cf": {
                        "cf_strasse": address.get('address_line1'),
                        "cf_hausnummer": address.get('hausnummer'),
                        "cf_ort": "{0} {1}".format(address.get('plz'), address.get('city'))
                    }
                }
        
        try:
            request = send_request("address", json, token)#.get('access_token')) <- To be changed after Testing
            frappe.db.set_value("Address", address.get('name'), "zoho_id", request.get('id'))
            frappe.log_error(request, "request")
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
        
        break #to be removed after testing
        
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
            request = send_request("customer", json, token)#.get('access_token')) <- To be changed after Testing
            frappe.db.set_value("Customer", customer.get('name'), "zoho_id", request.get('id'))
            frappe.log_error(request, "request")
        except Error as Err:
            frappe.log_error("ZOHO API PATCH ERROR", "ZOHO API patch Error: {0}".format(Err))
        
        break #to be removed after testing
