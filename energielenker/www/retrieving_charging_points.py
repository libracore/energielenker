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
    
    avaliable_points = get_ladepunkte(frappe.session.user)
    context['ladepunkte_s'] = avaliable_points.get('avaliable_points_s')
    context['ladepunkte_m'] = avaliable_points.get('avaliable_points_m')
    return context

def get_ladepunkte(user):
    data = frappe.db.sql("""SELECT
                                `tabCharging Point Key Account`.`avaliable_points_s`,
                                `tabCharging Point Key Account`.`avaliable_points_m`
                            FROM
                                `tabCharging Point Key Account`
                            LEFT JOIN
                                `tabCharging Point Key Account User` ON `tabCharging Point Key Account`.`name` = `tabCharging Point Key Account User`.`parent`
                            WHERE
                                `tabCharging Point Key Account User`.`user` = %(user)s
                            AND 
                                `tabCharging Point Key Account`.`disabled` = 0;""", {'user': user}, as_dict=True)
    
    if len(data) > 0:
        avaliable_points_s = data[0].get('avaliable_points_s')
        avaliable_points_m = data[0].get('avaliable_points_m')
    else:
        avaliable_points_s = 0
        avaliable_points_m = 0
    
    return {'avaliable_points_s': avaliable_points_s, 'avaliable_points_m': avaliable_points_m}
    
@frappe.whitelist()
def validate_qty(qty_string, points_type):
    qty = int(qty_string)
    uom_check = get_item_uom(qty)
    if not uom_check:
        license_key = "Error"
        return license_key
    all_avaliable_points = get_ladepunkte(frappe.session.user)
    avaliable_points = all_avaliable_points.get('avaliable_points_{0}'.format(points_type.lower()))
    if avaliable_points >= qty:
        license_key = create_license_key(qty, points_type)
        return license_key
    else:
        return False
        
def create_license_key(qty, points_type):
    purchase_order = create_purchase_order(qty, points_type)
    lizenzgutschein = create_lizenzgutschein(purchase_order, qty, points_type)
    license_key = get_license_key(lizenzgutschein)
    log_entry = update_account(license_key, qty, points_type)
    return license_key
    

def create_purchase_order(qty, points_type):
    #get today
    today = getdate()
    
    #get Settings
    po_settings = frappe.get_doc('Webshop Settings', 'Webshop Settings')
    
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
        'item_code': po_settings.get('po_item_{0}'.format(points_type.lower())),
        'schedule_date': today,
        'item_name': po_settings.get('po_item_{0}_name'.format(points_type.lower())),
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

def create_lizenzgutschein(purchase_order_name, qty, points_type):
    #get Purchase Order
    purchase_order_doc = frappe.get_doc('Purchase Order', purchase_order_name)
    
    #Map Points Type
    voucher_type = map_points_type(points_type)
    
    lizenzgutschein = frappe.get_doc({
        'doctype': 'Lizenzgutschein',
        'purchase_order': purchase_order_doc.name,
        'positions_nummer': "1.1",
        'position_id': purchase_order_doc.items[0].name,
        'evse_count': qty,
        'type': voucher_type
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

def update_account(license_key, qty, points_type):
    today = getdate()
    customer = frappe.db.sql("""SELECT `parent` FROM `tabCharging Point Key Account User`  WHERE `user` = '{user}'""".format(user=frappe.session.user), as_dict=True)
    customer_doc = frappe.get_doc("Charging Point Key Account", customer[0].parent)
    
    fieldname = "avaliable_points_{0}".format(points_type.lower())
    new_qty = customer_doc.get(fieldname) - qty
    customer_doc.set(fieldname, new_qty)
    
    entry = {
        'reference_doctype': 'Charging Point Key Account Log',
        'date': today,
        'type': points_type,
        'activity': "Webshop",
        'evse_count': qty * -1,
        'license_key': license_key,
        'user': frappe.session.user
    }
    customer_doc.append('past_activities', entry)
    customer_doc.save(ignore_permissions=True)
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

@frappe.whitelist()
def logout_from_webshop():
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return

def map_points_type(points_type):
    mapper = {
                'S': "EvseAc",
                'M': "EvseDc"
            }
    
    return mapper[points_type]
