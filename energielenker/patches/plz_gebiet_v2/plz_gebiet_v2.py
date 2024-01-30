import frappe
from frappe import _
from energielenker.energielenker.utils.lead import insert_plz_gebiet
from energielenker.energielenker.utils.utils import get_plz_gebiet

def execute():
    frappe.reload_doc("energielenker", "doctype", "Lead")
    frappe.reload_doc("energielenker", "doctype", "Quotation")
    frappe.reload_doc("energielenker", "doctype", "Sales Order")
    print("Verarbeite Addresse in PLZ...")
    loop = 1
    lead_success = True
    lead_error = []
    sql_query = """
        SELECT `addresslink`.`parent`
        FROM `tabDynamic Link` AS `addresslink`
        WHERE `addresslink`.`link_doctype` = 'Lead'
        AND `addresslink`.`parenttype` = 'Address'"""
    addresses = frappe.db.sql(sql_query, as_dict=True)
    total = len(addresses)
    for address in addresses:
        print("{0} von {1}".format(loop, total))
        try:
            adr = frappe.get_doc("Address", address.parent)
            insert_plz_gebiet(adr, "event")
        except Exception as Err:
            lead_success = False
            lead_error.append([address.parent, str(Err)])
            pass
        loop += 1
    
    print("Verarbeite Angebot in PLZ...")
    loop = 1
    quotation_success = True
    quotation_error = []
    sql_query = """
        SELECT `name`
        FROM `tabQuotation`"""
    quotations = frappe.db.sql(sql_query, as_dict=True)
    total = len(quotations)
    for quotation in quotations:
        print("{0} von {1}".format(loop, total))
        try:
            qtn = frappe.get_doc("Quotation", quotation.name)
            get_plz_gebiet(qtn, "event")
        except Exception as Err:
            quotation_success = False
            quotation_error.append([quotation.name, str(Err)])
            pass
        loop += 1
        
    print("Verarbeite AB in PLZ...")
    loop = 1
    sales_order_success = True
    so_error = []
    sql_query = """
        SELECT `name`
        FROM `tabSales Order`"""
    sales_orders = frappe.db.sql(sql_query, as_dict=True)
    total = len(sales_orders)
    for sales_order in sales_orders:
        print("{0} von {1}".format(loop, total))
        try:
            so = frappe.get_doc("Sales Order", sales_order.name)
            get_plz_gebiet(so, "event")
        except Exception as Err:
            sales_order_success = False
            so_error.append([sales_order.name, str(Err)])
            pass
        loop += 1
    
    print("lead_success = {0}".format(lead_success))
    if not lead_success:
        print(lead_error)
    print("quotation_success = {0}".format(quotation_success))
    if not quotation_success:
        print(quotation_error)
    print("sales_order_success = {0}".format(sales_order_success))
    if not sales_order_success:
        print(so_error)
    return
