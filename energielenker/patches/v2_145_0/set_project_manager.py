import frappe

def execute():
    frappe.reload_doc("Selling", "doctype", "Sales Order")
    frappe.reload_doc("Accounts", "doctype", "Sales Invoice")
    frappe.reload_doc("Stock", "doctype", "Delivery Note")
    
    documents_to_update = frappe.db.sql("""
                                        SELECT
                                            `name`,
                                            `project_clone` AS `project`,
                                            'Sales Order' AS `doctype`
                                        FROM
                                            `tabSales Order`
                                        WHERE
                                            `project_clone` IS NOT NULL
                                        AND
                                            `docstatus` != 2
                                            
                                        UNION ALL
                                        
                                        SELECT
                                            `name`,
                                            `project`,
                                            'Sales Invoice' AS `doctype`
                                        FROM
                                            `tabSales Invoice`
                                        WHERE
                                            `project` IS NOT NULL
                                        AND
                                            `docstatus` != 2
                                            
                                        UNION ALL
                                        
                                        SELECT
                                            `name`,
                                            `project`,
                                            'Delivery Note' AS `doctype`
                                        FROM
                                            `tabDelivery Note`
                                        WHERE
                                            `project` IS NOT NULL
                                        AND
                                            `docstatus` != 2""", as_dict=True)
                                            
    for doc in documents_to_update:
        project_manager = frappe.get_value("Project", doc.get('project'), "project_manager_name")
        frappe.db.set_value(doc.get('doctype'), doc.get('name'), "project_manager_name", project_manager)
        
    return
