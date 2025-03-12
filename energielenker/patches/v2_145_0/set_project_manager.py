import frappe

def execute():
    frappe.reload_doc("Selling", "doctype", "Sales Order")
    frappe.reload_doc("Accounts", "doctype", "Sales Invoice")
    frappe.reload_doc("Stock", "doctype", "Delivery Note")
    
    documents_to_update = frappe.db.sql("""
                                        SELECT
                                            `name`,
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
                                            'Delivery Note' AS `doctype`
                                        FROM
                                            `tabDelivery Note`
                                        WHERE
                                            `project` IS NOT NULL
                                        AND
                                            `docstatus` != 2""".format(pm=self.get('project_manager_name'), project=self.get('name')), as_dict=True)
                                            
    for doc in documents_to_update:
        frappe.set_value(doc.get('doctype'), doc.get('name'), "project_manager_name", self.get('project_manager_name'))
