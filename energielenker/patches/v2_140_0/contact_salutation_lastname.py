import frappe

def execute():
    frappe.reload_doc("Selling", "doctype", "Sales Order")
    
    sales_orders = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `contact_person_two`
                                FROM
                                    `tabSales Order`
                                WHERE
                                    `contact_person_two` IS NOT NULL
                                AND
                                    `docstatus` < 2""", as_dict=True)
                                    
    frappe.log_error(sales_orders, "sales_orders")
    for sales_order in sales_orders:
        contact_doc = frappe.get_doc("Contact", sales_order.get('contact_person_two'))
        
        if contact_doc:
            frappe.db.set_value("Sales Order", sales_order.get('name'), "contact_salutation", "{0}".format(contact_doc.get('salutation')))
            frappe.db.set_value("Sales Order", sales_order.get('name'), "contact_last_name", "{0}".format(contact_doc.get('first_name')))
    frappe.db.commit()
    return
