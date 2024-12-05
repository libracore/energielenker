# -*- coding: utf-8 -*-
# Copyright (c) 2025, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def transfer_stock(from_warehouse, to_warehouse, update_items, remarks=None):
    stock_movement = False
    #get all items from source warehouse
    warehouse_items = frappe.db.sql("""
                                    SELECT
                                        `item_code`,
                                        `stock_uom`,
                                        `actual_qty`
                                    FROM
                                        `tabBin`
                                    WHERE
                                        `warehouse` = '{warehouse}'
                                    AND
                                        `actual_qty` > 0
                                    AND
                                        `item_code` IN (SELECT `item_code` FROM `tabItem` WHERE `disabled` = 0)""".format(warehouse=from_warehouse), as_dict=True)
    #create control log message
    log_message = "Folgende Artikel wurden von {0} nach {1} umgelagert:\n".format(from_warehouse, to_warehouse)
    
    #create stock entry
    if len(warehouse_items) > 0:
        stock_entry_items = []
        for warehouse_item in warehouse_items:
            log_message += "\n{0} {1} {2}".format(warehouse_item.get('actual_qty'), warehouse_item.get('stock_uom'), warehouse_item.get('item_code'))
            stock_entry_items.append({
                'item_code': warehouse_item.get('item_code'),
                'qty': warehouse_item.get('actual_qty'),
                'uom': warehouse_item.get('stock_uom'),
                's_warehouse': from_warehouse,
                't_warehouse': to_warehouse
            })
        
        stock_entry = frappe.get_doc({
            'doctype': "Stock Entry",
            'stock_entry_type': 'Material Transfer',
            'from_warehouse': from_warehouse,
            'to_warehouse': to_warehouse,
            'items': stock_entry_items,
            'remarks': remarks
        }).insert()
        stock_entry.submit()
        
        stock_movement = True
    else:
        log_message += "\nKeine Artikel mit Lager {0} gefunden".format(from_warehouse)
    
    #set new default warehouse if checkox is set
    if int(update_items):
        #get items to update
        items_to_update = frappe.db.sql("""
                                        SELECT
                                            `parent`
                                        FROM
                                            `tabItem Default`
                                        WHERE
                                            `default_warehouse` = '{warehouse}'""".format(warehouse=from_warehouse), as_dict=True)
        
        #items to update
        frappe.db.sql("""UPDATE `tabItem Default` SET `default_warehouse` = '{to_warehouse}' WHERE `default_warehouse` = '{from_warehouse}'""".format(to_warehouse=to_warehouse, from_warehouse=from_warehouse))
        frappe.db.sql("""UPDATE `tabItem` SET `default_warehouse_readonly` = '{to_warehouse}' WHERE `default_warehouse_readonly` = '{from_warehouse}'""".format(to_warehouse=to_warehouse, from_warehouse=from_warehouse))
        
        #update log message
        log_message += "\n\n\nBei folgenden Artikel wurde das Standardlager von {0} auf {1} angepasst:\n".format(from_warehouse, to_warehouse)
        
                                            
        if len(items_to_update) > 0:
            for item_to_update in items_to_update:
                log_message += "\n{0}".format(item_to_update.get('parent'))
        else:
            log_message += "\nKeine Artikel mit Standardlager {0} gefunden.".format(from_warehouse)
        
    if stock_movement:
        frappe.log_error(log_message, "Umbuchung {0}".format(stock_entry.name))
        return stock_entry.name
    else:
        frappe.log_error(log_message, "Umbuchung ohne Artikel")
        return None
