import frappe

def execute():
    frappe.reload_doc("Contacts", "doctype", "Contact")
    
    contacts = frappe.db.sql("""
                                SELECT
                                    `name`
                                FROM
                                    `tabContact`
                                WHERE
                                    `email_id` IS NULL""", as_dict=True)
                                    
    for contact in contacts:
        contact_doc = frappe.get_doc("Contact", contact.get('name'))
        
        if contact_doc:
            if contact_doc.email_ids:
                if not contact_doc.salutation:
                    contact_doc.salutation = "-"
                for e_mail in contact_doc.email_ids:
                    e_mail.is_primary = 1
                    break
            contact_doc.save()
    frappe.db.commit()
    
    frappe.reload_doc("Selling", "doctype", "Sales Order")
    
    sales_orders = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `contact_person_two`
                                FROM
                                    `tabSales Order`
                                WHERE
                                    `contact_person_two` IS NOT NULL""", as_dict=True)
    
    for sales_order in sales_orders:
        contact_email = frappe.get_value("Contact", sales_order.get('contact_person_two'), "email_id")
        if contact_email:
            update_email = frappe.db.sql("""
                                            UPDATE
                                                `tabSales Order`
                                            SET
                                                `contact_email_two` = '{email}'
                                            WHERE
                                                `name` = '{so}'""".format(email=contact_email, so=sales_order.get('name')))
                                                
    frappe.db.commit()
        
    return
