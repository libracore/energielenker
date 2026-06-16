import frappe
from frappe.modules.utils import sync_customizations
from energielenker.zoho_api import send_request, get_new_token

def execute():
    sync_customizations("energielenker")
    
    revenue_types = frappe.db.sql("""
                                    SELECT
                                        `name`,
                                        `cost_center`
                                    FROM
                                        `tabRevenue Type`;""", as_dict=True)
    
    for revenue_type in revenue_types:
        kst_code = frappe.get_value("Cost Center", revenue_type.get('cost_center'), "kst_code")
        update = frappe.db.set_value("Revenue Type", revenue_type.get('name'), "kst_code", kst_code)
    
    frappe.db.commit()
    
    sales_invoices = frappe.db.sql("""
                                    SELECT
                                        `name`
                                    FROM
                                        `tabSales Invoice`;""", as_dict=True)
    
    for sales_invoice in sales_invoices:
        invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice.get('name'))
        for item in invoice_doc.get('items'):
            kst_code = frappe.get_value("Revenue Type", item.get('revenue_type'), "kst_code")
            update = frappe.db.set_value("Sales Invoice Item", item.get('name'), "revenue_kst_code", kst_code)
