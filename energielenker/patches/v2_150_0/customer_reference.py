import frappe
from frappe.modules.utils import sync_customizations
from energielenker.zoho_api import send_request, get_new_token

def execute():
    sync_customizations("energielenker")
    
    sales_orders = frappe.db.sql("""
                                    SELECT
                                        `name`,
                                        `customer`
                                    FROM
                                        `tabSales Order`;""", as_dict=True)
    
    for sales_order in sales_orders:
        reference = frappe.get_value("Customer", sales_order.get('customer'), "referenz")
        frappe.db.set_value("Sales Order", sales_order.get('name'), "customer_reference", reference)
