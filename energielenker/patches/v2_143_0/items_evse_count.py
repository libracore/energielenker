import frappe

def execute():
    frappe.reload_doc("Selling", "doctype", "Quotation Item")
    frappe.reload_doc("Selling", "doctype", "Sales Order Item")
    frappe.reload_doc("Accounts", "doctype", "Sales Invoice Item")
    frappe.reload_doc("Stock", "doctype", "Delivery Note Item")

    quotation_items = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `uom`
                                FROM
                                    `tabQuotation Item`
                                WHERE
                                    `item_code` = "A-0001701"
                                AND
                                    `docstatus` != 2""", as_dict=True)
                                    
    for item in quotation_items:
        evse_count = frappe.get_value("UOM", item.get('uom'), "evse_count")
        if evse_count:
            frappe.db.set_value("Quotation Item", item.get('name'), "evse_count", evse_count)
            
    sales_order_items = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `uom`
                                FROM
                                    `tabSales Order Item`
                                WHERE
                                    `item_code` = "A-0001701"
                                AND
                                    `docstatus` != 2""", as_dict=True)
                                    
    for so_item in sales_order_items:
        evse_count = frappe.get_value("UOM", so_item.get('uom'), "evse_count")
        if evse_count:
            frappe.db.set_value("Sales Order Item", so_item.get('name'), "evse_count", evse_count)
            
    delivery_note_items = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `uom`
                                FROM
                                    `tabDelivery Note Item`
                                WHERE
                                    `item_code` = "A-0001701"
                                AND
                                    `docstatus` != 2""", as_dict=True)
                                    
    for dn_item in delivery_note_items:
        evse_count = frappe.get_value("UOM", dn_item.get('uom'), "evse_count")
        if evse_count:
            frappe.db.set_value("Delivery Note Item", dn_item.get('name'), "evse_count", evse_count)
            
    sales_invoice_items = frappe.db.sql("""
                                SELECT
                                    `name`,
                                    `uom`
                                FROM
                                    `tabSales Invoice Item`
                                WHERE
                                    `item_code` = "A-0001701"
                                AND
                                    `docstatus` != 2""", as_dict=True)
                                    
    for si_item in sales_invoice_items:
        evse_count = frappe.get_value("UOM", si_item.get('uom'), "evse_count")
        if evse_count:
            frappe.db.set_value("Sales Invoice Item", si_item.get('name'), "evse_count", evse_count)

    frappe.db.commit()
    return
