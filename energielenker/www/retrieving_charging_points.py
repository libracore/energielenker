# Copyright (c) 2024, libracore ag and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate

no_cache = True

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/webshop_login"
        raise frappe.Redirect
    
    context['ladepunkte'] = get_ladepunkte(frappe.session.user)
    return context

def get_ladepunkte(user):
    
    data = frappe.db.sql("""SELECT
                                `tabLicense Key Account`.`avaliable_points`
                            FROM `tabLicense Key Account`
                            LEFT JOIN `tabLicense Key Account User` ON `tabLicense Key Account`.`name` = `tabLicense Key Account User`.`parent`
                            WHERE `tabLicense Key Account User`.`user` = '{user}'
                            AND `tabLicense Key Account`.`disabled` = 0""".format(user=user), as_dict=True)
    
    if len(data) > 0:
        avaliable_points = data[0].get('avaliable_points')
    else:
        avaliable_points = 0
    
    return avaliable_points
    
@frappe.whitelist()
def validate_qty(qty_string):
    qty = int(qty_string)
    uom_check = get_item_uom(qty)
    if not uom_check:
        license_key = "Error"
        return license_key
    avaliable_points = get_ladepunkte(frappe.session.user)
    if avaliable_points >= qty:
        license_key = create_license_key(qty)
        return license_key
    else:
        return False
        
def create_license_key(qty):
    purchase_order = create_purchase_order(qty)
    lizenzgutschein = create_lizenzgutschein(purchase_order, qty)
    license_key = get_license_key(lizenzgutschein)
    log_entry = create_log_entry(license_key, qty)
    return license_key
    

def create_purchase_order(qty):
    #get today
    today = getdate()
    
    #get Sales Order and settings
    po_settings = frappe.get_doc('Ladepunkt Key API Purchase Order', 'Ladepunkt Key API Purchase Order')
    
    #create new Purchase Order
    new_po_doc = frappe.get_doc({
        'doctype': 'Purchase Order',
        'supplier': po_settings.supplier,
        'schedule_date': today,
        'voraussichtlicher_liefertermin': today,
        'shipping_address_name': "",
        'shipping_address': "",
        'ansprechpartner': po_settings.ansprechpartner,
        'k_ansprechperson': po_settings.k_ansprechperson
        })
    
    entry = {
        'reference_doctype': 'Purchase Order Item',
        'item_code': po_settings.item_code,
        'schedule_date': today,
        'item_name': po_settings.item_name,
        'qty': 1,
        'uom': get_item_uom(qty),
        'cost_center': po_settings.cost_center
    }
    new_po_doc.append('items', entry)
    
    new_po_doc = new_po_doc.insert(ignore_permissions=True)
    new_po_doc.submit()
    
    #get name of new Purchase Order and return it
    purchase_order = new_po_doc.name
    
    return purchase_order

def create_lizenzgutschein(purchase_order_name, qty):
    # ~ #get Purchase Order
    purchase_order_doc = frappe.get_doc('Purchase Order', purchase_order_name)
    
    lizenzgutschein = frappe.get_doc({
        'doctype': 'Lizenzgutschein',
        'purchase_order': purchase_order_doc.name,
        'positions_nummer': "1.1",
        'position_id': purchase_order_doc.items[0].name,
        'evse_count': qty
        })

    lizenzgutschein = lizenzgutschein.insert(ignore_permissions=True)
                
    return lizenzgutschein.name
    
def get_license_key(lizenzgutschein):
    data = frappe.db.sql("""SELECT
                            `lizenzgutschein`
                            FROM `tabLizenzgutschein`
                            WHERE `name` = '{lg}'""".format(lg=lizenzgutschein), as_dict=True)
                            
    if len(data) > 0:
        license_key = data[0].get('lizenzgutschein')
    else:
        frappe.log_error("Webshop Lizenzgutschein Error", "Lizenzgutschein Error")
        license_key = "Error"
        
    return license_key

def create_log_entry(license_key, qty):
    today = getdate()
    customer = frappe.db.sql("""SELECT `parent` FROM `tabLicense Key Account User`  WHERE `user` = '{user}'""".format(user=frappe.session.user), as_dict=True)
    customer_doc = frappe.get_doc("License Key Account", customer[0].parent)
    
    entry = {
        'reference_doctype': 'License Key Account Log',
        'date': today,
        'evse_count': qty,
        'license_key': license_key,
        'user': frappe.session.user
    }
    customer_doc.append('past_activities', entry)
    customer_doc.save()
    frappe.db.commit()
    
    return

def get_item_uom(qty):
    data = frappe.db.sql("""SELECT `name` FROM `tabUOM` WHERE `evse_count` = '{qty}'""".format(qty=qty), as_dict=True)
    if len(data) == 1:
        uom = data[0].get('name')
        return uom
    else:
        frappe.log_error("Webshop UOM Error", "UOM Error")
        return False
