# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from energielenker.energielenker.doctype.depot.depot import get_items_html
from frappe.utils.data import getdate
from frappe.utils import cint

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
def check_for_webshop_account(doc, event="submit"):
    delivery_note_doc = json.loads(doc)
    validation = True
    #get points item
    points_item = frappe.db.get_value("Webshop Settings", "Webshop Settings", "so_item")
    
    for item in delivery_note_doc['items']:
        if item.get('item_code') == points_item:
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
    
    return validation

@frappe.whitelist()
def check_for_webshop_points(doc, event="submit"):
    delivery_note_doc = json.loads(doc)
    points = False
    #get points item
    points_item = frappe.db.get_value("Webshop Settings", "Webshop Settings", "so_item")
    
    #check if there are webshop points in items
    qty = 0
    
    for item in delivery_note_doc['items']:
        if item.get('item_code') == points_item:
            qty += item.get('qty')
            points = True

    #if there are points add/remove points to account
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
    
    return points
    
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
        if item['depot_qty']:
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
        
def set_invoiced_items(self, event):
    if not self.total:
        self.per_billed = 100
        self.status = "Completed"
    return

@frappe.whitelist()
def check_for_overdelivery(doc, check_items=True):
    doc = json.loads(doc)
    items_without_so = []

    if cint(doc['skip_check_against_sales_order']) == 1:
        check_items = False
    else:
        for item in doc['items']:
            if not item.get('against_sales_order'):
                items_without_so.append("""Pos. {0} {1}""".format(item.get('idx'), item.get('item_code')))
    
    if len(items_without_so) > 0:
        msgprint_txt = """
            Nachfolgende Artikel besitzen keinen Kundenauftrag und müssen geprüft werden:<br><br>{0}<br><br>
            Wenn es korrekt ist dass diese Artikel keinen Kundenauftrag besitzen sollen, dann können Sie oben rechts auf "Kundenauftrag Prüfung deaktivieren" klicken und den Lieferschein erneut buchen.
        """.format("<br>".join(items_without_so))
        frappe.msgprint(msgprint_txt)
        return False
    else:
        #get qty of all Delivery Notes and Sales Orders
        for item in doc['items']:
            if item.get('against_sales_order'):
                delivery_note = frappe.db.sql("""
                                        SELECT
                                            SUM(`qty`) AS `dn_qty`,
                                            `item_code`
                                        FROM
                                            `tabDelivery Note Item`
                                        WHERE
                                            (`docstatus` = 1 AND `against_sales_order` = '{so_name}' AND `item_code` = '{item_code}' AND `exclude_from_overdelivery_check` = 0)
                                        OR
                                            (`item_code` = '{item_code}' AND `parent` = '{dn}' AND `exclude_from_overdelivery_check` = 0)
                                        GROUP BY `item_code`""".format(so_name=item.get('against_sales_order'), item_code=item.get('item_code'), dn=doc.get('name')), as_dict=True)
                                            
                sales_order = frappe.db.sql("""
                                        SELECT
                                            SUM(`qty`) AS `so_qty`,
                                            `delivered_position`
                                        FROM
                                            `tabSales Order Item`
                                        WHERE
                                            `parent` = '{so_name}'
                                        AND
                                            `item_code` = '{item_code}'""".format(so_name=item.get('against_sales_order'), item_code=item.get('item_code')), as_dict=True)
                #Validate quantities
                if not sales_order[0].so_qty or len(sales_order) < 1:
                    frappe.msgprint("Artikel {0} nicht in Kundenauftrag {1} vorhanden".format(item.get('item_code'), item.get('against_sales_order')))
                    return False
                else:
                    if len(delivery_note) < 1:
                        frappe.msgprint("Es ist ein Fehler aufgetreten")
                        return False
                    elif delivery_note[0].dn_qty > sales_order[0].so_qty:
                        frappe.msgprint("Artikel {0} kann nicht überliefert werden!".format(item.get('item_code')))
                        return False
                    elif sales_order[0].delivered_position:
                        frappe.msgprint("Artikel {0} wurde bereits über Streckengeschäft geliefert!".format(item.get('item_code')))
                        return False
    return True

@frappe.whitelist()
def toggle_check_against_sales_order(dn, flag):
    frappe.db.set_value("Delivery Note", dn, "skip_check_against_sales_order", flag)
    frappe.db.commit()
    return
    
@frappe.whitelist()
def check_so_quantities(doc):
    doc = json.loads(doc)
    message = '<ul style="padding-left: 32px !important; ">'
    overdelivery = False
    affected_items = []
    
    for item in doc.get('items'):
        if item.get('against_sales_order'):
            undelivered_so_qty = frappe.db.get_value("Sales Order Item", item.get('so_detail'), "qty") - frappe.db.get_value("Sales Order Item", item.get('so_detail'), "delivered_qty")
            if item.get('qty') > undelivered_so_qty:
                message +=  '<li><b>{0} (Zeile {1})</b></li>'.format(item.get('item_code'), item.get('idx'))
                affected_items.append({'item_line_name': item.get('name'), 'undelivered_qty': undelivered_so_qty})
                overdelivery = True
                
    return {'overdelivery': overdelivery, 'affected_items' : affected_items, 'message': message}

def serial_no_by_pos_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    if filters.get('batch_no'):
        batch_condition = """AND `tabSerial No`.`batch_no` = '{batch}'""".format(batch=filters.get('batch_no'))
    else:
        batch_condition = """"""
    serial_nos = frappe.db.sql("""
                                SELECT
                                    `tabSerial No`.`name`
                                FROM
                                    `tabSerial No`
                                LEFT JOIN
                                    `tabStock Entry Detail` ON `tabStock Entry Detail`.`serial_no` LIKE CONCAT('%', `tabSerial No`.`name`, '%')
                                WHERE
                                    `item_so_detail` = '{so_detail}'
                                AND
                                    `tabSerial No`.`warehouse` = '{warehouse}'
                                {batch_condition}
                                AND
                                    `tabStock Entry Detail`.`docstatus` = 1""".format(so_detail=filters.get('so_detail'), warehouse=filters.get('warehouse'), batch_condition=batch_condition), as_dict=as_dict)
    return serial_nos

@frappe.whitelist()
def get_depot_item_warehouse(doc):
    doc = json.loads(doc)
    depot_items = []
    
    for item in doc.get('items'):
        if item.get('source_depot'):
            default_warehouse = frappe.db.get_value("Item", item.get('item_code'), "default_warehouse_readonly")
            depot_items.append({'line_name': item.get('name'), 'warehouse': default_warehouse })
    
    if len(depot_items) > 0:
        return depot_items
    else:
        return None

@frappe.whitelist()
def get_default_warehouses(doc):
    doc = json.loads(doc)
    affected_items = []
    
    for item in doc.get('items'):
        if not item.get('source_depot'):
            default_warehouse = frappe.db.get_value("Item", item.get('item_code'), "default_warehouse_readonly")
            affected_items.append({'line_name': item.get('name'), 'warehouse': default_warehouse })
    
    if len(affected_items) > 0:
        return affected_items
    else:
        return None

@frappe.whitelist()
def get_hidden_serial_nos():
    items = frappe.db.sql("""
                    SELECT
                        `item_code`
                    FROM
                        `tabDelivery Note Hidden Serial Numbers`""", as_dict=True)
                        
    item_list = []
    for item in items:
        item_list.append(item.get('item_code'))
    
    return item_list
