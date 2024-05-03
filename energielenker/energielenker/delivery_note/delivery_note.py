# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

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
def get_depot_items(depot):
    items = frappe.db.sql("""SELECT
                            `tabDepot Item`.`item_code`,
                            `tabDepot Item`.`qty`,
                            `tabDepot`.`to_warehouse` AS `warehouse`
                        FROM `tabDepot Item`
                        LEFT JOIN `tabDepot` ON `tabDepot Item`.`parent` = `tabDepot`.`name`
                        WHERE `tabDepot Item`.`parent` = '{depot}'""".format(depot=depot), as_dict=True)
    return items
