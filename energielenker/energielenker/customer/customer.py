# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def adresse_verknupfen(address, customer):
    address = frappe.get_doc("Address", address)
    row = address.append('links', {})
    row.link_doctype = "Customer"
    row.link_name = customer
    
    address.save()
    return

@frappe.whitelist()
def kontakt_verknupfen(contact, customer):
    contact = frappe.get_doc("Contact", contact)
    row = contact.append('links', {})
    row.link_doctype = "Customer"
    row.link_name = customer
    
    contact.save()
    return
