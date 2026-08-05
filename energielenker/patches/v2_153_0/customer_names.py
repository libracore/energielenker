import frappe
from frappe.modules.utils import sync_customizations

def execute():
    sync_customizations("energielenker")
    
    customers = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `customer_name`
                                FROM
                                    `tabCustomer`
                                WHERE
                                    `name` != `customer_name`;""", as_dict=True)
    
    if len(customers) > 0:
        for customer in customers:
            try:
                frappe.rename_doc("Customer", customer.get('name'), customer.get('customer_name'), force=True)
            except Exception as Err:
                frappe.log_error("Name: {0}<br>Customer Name: {1}<br>Err: {2}".format(customer.get('name'), customer.get('customer_name'), Err), "Rename Error")
