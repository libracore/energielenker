import frappe
from frappe.modules.utils import sync_customizations

def execute():
    sync_customizations("energielenker")
    
    #Submit Contacts
    contacts = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `last_name`,
                                    `first_name`,
                                    `email_id`,
                                    
                                    
                                FROM
                                    `tabContact`""", as_dict=True



