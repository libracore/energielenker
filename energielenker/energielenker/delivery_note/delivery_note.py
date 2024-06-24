# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from energielenker.energielenker.doctype.depot.depot import get_items_html

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
    
    frappe.log_error(affected_items)
    return
