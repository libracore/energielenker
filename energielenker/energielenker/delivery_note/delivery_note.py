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
    
@frappe.whitelist()
def check_depot_delivery(self, event):
    items = frappe.db.sql("""
                            SELECT 
                                *,
                                (SELECT SUM(`qty` - `delivered_qty`) 
                                 FROM `tabSales Order Item`
                                 WHERE `parent` = `dn`.`against_sales_order`
                                   AND `item_code` = `dn`.`item_code`
                                ) AS `so_qty`
                            FROM (
                                SELECT 
                                    `parent`,
                                    `against_sales_order`,
                                    `item_code`,
                                    SUM(`qty`) AS `dn_qty`
                                FROM `tabDelivery Note Item`
                                WHERE `parent` = "{dn}"
                                  AND `source_depot` IS NULL
                                GROUP BY CONCAT(`against_sales_order`, ":", `item_code`)
                            ) AS `dn`""".format(dn=self.name), as_dict=True)
                            
    for item in items:
        item['depot_qty'] = get_depot_qty(item.get('item_code'), item.get('against_sales_order'))
        avaliable_qty = item.get('so_qty') - item.get('depot_qty')
        if item.get('dn_qty') > avaliable_qty:
            frappe.throw("Es können nicht mehr als {0} von Artikel {1} ausgeliefert werden!".format(avaliable_qty, item.get('item_code')))
    
    return
    
def get_depot_qty(item_code, sales_order):
    depot_qty = frappe.db.sql("""
            SELECT 
                IFNULL(SUM(`transactions`.`qty`), 0) AS `balance_qty`
            FROM (
                SELECT 
                    SUM(IF (`tabStock Entry Detail`.`s_warehouse` IN (SELECT `to_warehouse` FROM `tabDepot` WHERE `sales_order` = "{sales_order}"), (-1) * `tabStock Entry Detail`.`qty`, `tabStock Entry Detail`.`qty`)) AS `qty`
                FROM `tabStock Entry Detail`
                LEFT JOIN `tabStock Entry` ON `tabStock Entry`.`name` = `tabStock Entry Detail`.`parent`
                WHERE `tabStock Entry`.`source_depot` IN (SELECT `name` FROM `tabDepot` WHERE `sales_order` = "{sales_order}")
                  AND `tabStock Entry`.`docstatus` = 1
                  AND `tabStock Entry Detail`.`item_code` = "{item}"
                UNION SELECT
                    (-1) * `qty`
                FROM `tabDelivery Note Item`
                WHERE `tabDelivery Note Item`.`source_depot` IN (SELECT `name` FROM `tabDepot` WHERE `sales_order` = "{sales_order}")
                  AND `tabDelivery Note Item`.`item_code` = "{item}"
                  AND `tabDelivery Note Item`.`docstatus` = 1
            ) AS `transactions`;""".format(sales_order=sales_order, item=item_code), as_dict=True)
            
    if len(depot_qty) > 0:
        return depot_qty[0]['balance_qty']
    else:
        return 0
