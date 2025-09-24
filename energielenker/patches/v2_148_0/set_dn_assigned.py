import frappe
from frappe.modules.utils import sync_customizations
from energielenker.zoho_api import send_request, get_new_token

def execute():
    sync_customizations("energielenker")
    
    delivery_notes = frappe.db.sql("""
                                    SELECT
                                        `name`
                                    FROM
                                        `tabDelivery Note`
                                    WHERE
                                        `docstatus` = 1;""", as_dict=True)
    
    for delivery_note in delivery_notes:
        frappe.db.set_value("Delivery Note", delivery_note.get('name'), "delivery_note_assigned", 1)
