# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from energielenker.energielenker.doctype.depot.depot import get_items_html
from frappe.utils.data import getdate

@frappe.whitelist()
def fetch_kontakt_aus_lieferadresse(lieferadresse):
    kontakte = frappe.db.sql("""SELECT * FROM `tabContact` WHERE `address` = '{lieferadresse}' LIMIT 1""".format(lieferadresse=lieferadresse), as_dict=True)
    if len(kontakte) > 0:
        kontakt = kontakte[0]
        anrede = kontakt.salutation or None
        vorname = kontakt.last_name or None
        nachname = kontakt.first_name or None
        name = ''
        if anrede:
            name += anrede + " "
        if vorname:
            name += vorname + " "
        if nachname:
            name += nachname + " "
        return {
            'link': kontakt.name,
            'name':  name
        }
    else:
        return 'keiner'

def validate_valuation_rate(delivery_note, event):
    for item in delivery_note.items:
        item.valuation_rate = frappe.db.get_value('Item', item.item_code, 'valuation_rate') or 0
    return
    
@frappe.whitelist()
def validate_depot(items_string):
    items = json.loads(items_string)
    #check with items are open in a releated depot
    affected_items = []
    for item in items:
        depots = frappe.db.get_list("Depot", {'sales_order': item.get('sales_order')})
        for depot in depots:
            depot_items = get_items_html(depot.get('name'), "validate_depot")
            for depot_item in depot_items:
                if depot_item.get('item_code') == item.get('item') and depot_item.get('balance_qty'):
                    affected_items.append({'item': item.get('item'), 'depot': depot.get('name')})
    #create html for pop up
    if len(affected_items) > 0:
        html = "<p>Folgende Artikel befinden sich in einer offenen Kommissionierung:</p>"
        
        for affected_item in affected_items:
            html += "<br>{item} ({depot})".format(item=affected_item.get('item'), depot=affected_item.get('depot'))
        frappe.msgprint(html, title='Vorsicht', indicator='orange')
    
    return

@frappe.whitelist()
def check_for_webshop_points(doc, event="submit"):
    delivery_note_doc = json.loads(doc)
    validation = True
    #get points item
    points_item = frappe.db.get_value("Webshop Settings", "Webshop Settings", "so_item")
    
    #check if there are webshop points in items
    qty = 0
    
    for item in delivery_note_doc['items']:
        if item.get('item_code') == points_item:
            qty += item.get('qty')
            validation = False
            
    
    #return nothing, if there are no points in sales order
    if validation:
        return validation
    
    #check if customer has account
    try:
        account_doc = frappe.get_doc("Charging Point Key Account", delivery_note_doc.get('customer'))
        validation = True
    except:
        if event == "cancel":
            frappe.throw("Konto für diesen Kunden fehlt!")
        return validation

    #if there are points and an account, add/remove points to account
    account_doc.avaliable_points += qty if event == "submit" else qty * -1
    #create log entry
    log_entry = {
        'date': getdate(),
        'activity': delivery_note_doc['name'],
        'amount': qty if event == "submit" else qty * -1,
        'user': delivery_note_doc['owner']
    }
    account_doc.append('past_activities', log_entry)
    #save document
    account_doc.save()
    frappe.db.commit()
    
    return validation
    
@frappe.whitelist
def check_depot_delivery(delivery_note_doc):
    #get all affected sales order
    affected_sales_orders = []
    for item in delivery_note_doc.items:
        if item.get('against_sales_order') not in affected_sales_orders:
            affected_sales_orders.append(item.get('against_sales_order'))
    
    #check of there is an open depot for any affected sales order -> if not, return True
    open_affected_depots = frappe.db.sql("""
                                            SELECT
                                                `name`
                                            FROM
                                                `tabDepot`
                                            WHERE
                                                `sales_order` in '{0}'
                                            AND
                                                `status` = 'Open'""".format(affected_sales_orders), as_dict=True)
    if len(open_affected_depots) < 1:
        return True
    
    #Compare affected Depots with releated sales order and delivery notes and validate false if there are too many items in delivery note without link to depot
    
    #
    for sales_order in affected_sales_orders:
        open_depots = frappe.db.sql("""
                                    SELECT
                                        `name`
                                    FROM
                                        `tabDepot`
                                    WHERE
                                        `name` = '{so}'
                                    AND
                                        `status` = 'Open'""".format(so=sales_order), as_dict=True)
        if len(open_depots) == 1:
            depot_items = get_items_html(open_depots[0].get('name'), "check_depot_delivery")
        elif len(open_depots) > 1:
            depot_items = []
            for open_depot in open_depots:
                depot_items_ = get_items_html(open_depot, "check_depot_delivery")
                for depot_item_ in depot_items_:
                    existing_item = False
                    for depot_item in depot_items:
                        if depot_item.get('item_code') == depot_item_.get('item_code'):
                            depot_item.get('balance_qty') += depot_item.get('balance_qty')
                            existing_item = True
                    if not existing_item:
                    depot_items.append(depot_item_)
                    
        deliverable_items = []
        sales_order_items = frappe.db.sql("""
                                            SELECT
                                                `item_code`,
                                                `qty`
                                            FROM
                                                `tabSales Order Item`
                                            WHERE
                                                `parent`.`name` = '{so}'
                                            AND
                                                `docstatus` = 1""".format(so=sales_order), as_dict=True
        
