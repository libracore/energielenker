# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import add_months, nowdate, flt
from erpnext.selling.doctype.quotation.quotation import Quotation
from erpnext.selling.doctype.quotation.quotation import _make_customer
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist() 
def update_quotation_status():
    #************************************************************************************
    #overwrite validate to also set "Expired" as a status
    overwrite_quotation_validate()
    #************************************************************************************

    # Query to retrieve quotations that are still open 
    quotations_list = frappe.get_all("Quotation", filters={"status": ["in", ["Open"]]}, fields=["name", "status"])
    
    for quotation in quotations_list:
        quotation = frappe.get_doc("Quotation", quotation['name'])
        if str(quotation.valid_till) and str(quotation.valid_till) < nowdate():
            try:
                frappe.db.set(quotation, 'status', 'Expired')
                quotation.save(ignore_permissions=True)
                print("quotation {0} ".format(quotation.name))
            except Exception as err:
                frappe.log_error(err, "Quotation {0}".format(quotation.name))

def overwrite_quotation_validate():
    Quotation.validate = quotation_validation

def quotation_validation(self):
    #original Quotation exkl. self.set_status()
    def validate(self):
        super(Quotation, self).validate()
        # ~ self.set_status()
        self.update_opportunity()
        self.validate_order_type()
        self.validate_uom_is_integer("stock_uom", "qty")
        self.validate_valid_till()
        self.set_customer_name()
        if self.items:
            self.with_items = 1
            
@frappe.whitelist() 
def change_status_from_old_angebote():
    months = add_months(nowdate(), -6)
    angebots = frappe.db.sql("""SELECT `name` FROM `tabQuotation` WHERE (`status` = 'Open' OR `status` = 'Expired') AND `tabQuotation`.`valid_till` <= '{months}' """.format(months=months), as_dict=True)
    
    for angebot in angebots:
        
        angebot_doc = frappe.get_doc("Quotation", angebot['name'])
        lost_reasons_list = [{'lost_reason': 'verfallen vor mehr als 6 Monaten'}]
        
        #set angebot status to lost after being more than 6 months old
        try:
            Quotation.declare_enquiry_lost(angebot_doc, lost_reasons_list)
        except Exception as err:
            frappe.log_error(err, "change angebot status_: mark angebot {0}".format(angebot_doc.name))
    return

@frappe.whitelist() 
def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
    customer = _make_customer(source_name, ignore_permissions)

    def set_missing_values(source, target):
        if customer:
            target.customer = customer.name
            target.customer_name = customer.customer_name
        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    def update_item(obj, target, source_parent):
        target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

    doclist = get_mapped_doc("Quotation", source_name, {
            "Quotation": {
                "doctype": "Sales Order",
                "validation": {
                    "docstatus": ["=", 1]
                }
            },
            "Quotation Item": {
                "doctype": "Sales Order Item",
                "field_map": {
                    "parent": "prevdoc_docname"
                },
                "postprocess": update_item
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "add_if_empty": True
            },
            "Sales Team": {
                "doctype": "Sales Team",
                "add_if_empty": True
            }
        }, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

    # postprocess: fetch shipping address, set missing values

    return doclist

@frappe.whitelist()
def get_payment_terms_template(customer):
    template = None
    if customer:
        template = frappe.db.get_value("Customer", customer, "payment_terms")
    if not template:
        template = frappe.db.get_value("Company", "energielenker solutions GmbH", "payment_terms")
    return template

@frappe.whitelist()
def get_price_list_rate(item_code, uom, customer):
    #Check if customer has specific price
    price_list_rate = frappe.get_value("Item Price", {'item_code': item_code, 'uom': uom, 'customer': customer, 'selling': 1}, "price_list_rate")
    frappe.log_error(price_list_rate, "price_list_rate")
    if price_list_rate:
        return price_list_rate
    else:
        price_list_rate = frappe.get_value("Item Price", {'item_code': item_code, 'uom': uom, 'customer': None, 'selling': 1}, "price_list_rate")
        frappe.log_error(price_list_rate, "price_list_rate")
        return price_list_rate
