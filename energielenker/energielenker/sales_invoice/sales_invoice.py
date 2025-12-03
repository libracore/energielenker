# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.contacts.doctype.address.address import get_address_display
from frappe.contacts.doctype.contact.contact import get_contact_details

def validate_navision_of_items(sales_invoice, event):
    navision_deviation = ''
    for item in sales_invoice.items:
        try:
            item_navision = frappe.db.sql("""SELECT `navision_kontonummer` FROM `tabItem Default` WHERE `parent` = '{item}' AND `company` = '{company}'""".format(item=item.item_code, company=sales_invoice.company), as_dict=True)[0].navision_kontonummer
        except:
            item_navision = ''
        item.navision_kontonummer = item_navision
        if item_navision and item_navision != sales_invoice.navision_kontonummer:
            navision_deviation += str(item.idx) + "<br>"
    sales_invoice.navision_deviation = navision_deviation
    return

@frappe.whitelist()
def get_vat_template(customer):
    template = None
    territory = frappe.db.get_value("Customer", customer, "territory")
    parent_territory = frappe.db.get_value("Territory", territory, "parent_territory")

    if territory == "Deutschland" or parent_territory == "Deutschland":
        template = frappe.db.get_value("Sales Taxes and Charges Template", {"is_default": 1}, "name")
    else:
        data = frappe.db.sql("""
                                    SELECT
                                        `tabSales Taxes and Charges Template`.`name`
                                    FROM
                                        `tabSales Taxes and Charges Template`
                                    LEFT JOIN
                                        `tabSales Taxes and Charges` ON `tabSales Taxes and Charges`.`parent` = `tabSales Taxes and Charges Template`.`name`
                                    WHERE
                                        `tabSales Taxes and Charges`.`rate` = '0'
                                    AND
                                        `tabSales Taxes and Charges Template`.`disabled` = 0""", as_dict=True)
                                    
        if len(data) > 0:
            template = data[0].get('name')
            
    return template
    
def charged_at_cost(self, event):
    #get all sales orders which are affected
    affected_sales_orders = []
    for si_item in self.get('items'):
        if si_item.get('enthaelt_artikel_nach_aufwand') and si_item.get('sales_order') not in affected_sales_orders:
            affected_sales_orders.append(si_item.get('sales_order'))
    
    for sales_order in affected_sales_orders:
        sales_order_doc = frappe.get_doc("Sales Order", sales_order)
        
        invoices = frappe.db.sql("""
                                    SELECT
                                        SUM(`qty`) as `qty`
                                    FROM
                                        `tabSales Invoice Item`
                                    WHERE
                                        `sales_order` = '{so}'
                                    AND
                                        `docstatus` = 1""".format(so=sales_order), as_dict=True)
        
        if invoices[0].qty:
            per_billed = invoices[0].qty / sales_order_doc.get('total_qty') * 100
        else:
            per_billed = 0
        
        frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "per_billed", per_billed)
        frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "set_with_quantity", 1)
        
        if sales_order_doc.status == "To Deliver and Bill" and per_billed == 100:
            frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "status", "To Deliver")
        elif sales_order_doc.status == "To Bill" and per_billed == 100:
            frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "status", "Completed")
        elif sales_order_doc.status == "To Deliver" and per_billed < 100:
            frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "status", "To Deliver and Bill")
        elif sales_order_doc.status == "Completed" and per_billed < 100:
            frappe.db.set_value("Sales Order", sales_order_doc.get('name'), "status", "To Bill")
            
    return

def set_navision_export_check(self, event):
    if not self.is_return:
        self.rechnung_nach_navision_exportiert = 0
        self.rechnung_nach_d365_exportiert = 0
    else:
        self.rechnung_nach_navision_exportiert = 1
        self.rechnung_nach_d365_exportiert = 1
    return

def set_billing_information(self, event):
    if not self.billing_address_name:
        #check for standrad address
        check = frappe.db.get_value("Customer", self.customer, "set_manual_billing_address")
        if check:
            billing_information = frappe.db.sql("""
                                                SELECT
                                                    `manual_billing_address`,
                                                    `billing_contact`
                                                FROM
                                                    `tabCustomer`
                                                WHERE
                                                    `name` = '{cust}'""".format(cust=self.customer), as_dict=True)
            
            if len(billing_information) > 0:
                self.billing_address_name = billing_information[0].get('manual_billing_address')
                self.billing_contact = billing_information[0].get('billing_contact')
                self.billing_address = get_address_display(self.billing_address_name)
                billing_contact_display_dict = get_contact_details(self.billing_contact)
                self.billing_contact_display = billing_contact_display_dict.get('contact_display')
                self.save()
                frappe.db.commit()
