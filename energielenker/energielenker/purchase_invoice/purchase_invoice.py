# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import json

def validate_lagerfuehrung_of_items(purchase_invoice, event):
    for item in purchase_invoice.items:
        item.ist_lagergefuehrt = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
    return

@frappe.whitelist()
def check_for_streckengeschaeft(doc_):
    doc=json.loads(doc_)
    #set default to non-streckengeschaeft
    update_stock = 1
    
    #check if one item is streckengeschaeft
    for item in doc['items']:
        if item.get('purchase_order'):
            po_item = frappe.db.sql("""
                                    SELECT
                                        `delivered_by_supplier`
                                    FROM
                                        `tabPurchase Order Item`
                                    WHERE
                                        `name` = '{po_detail}'
                                    AND
                                        `docstatus` = 1""".format(po_detail=item['po_detail']), as_dict=True)
            #if one item is streckengeschaeft, dont update stock - discussed with MR. Ruhkamp by call
            if len(po_item) > 0:
                if po_item[0]['delivered_by_supplier'] == 1:
                    update_stock = 0
                
    return update_stock

@frappe.whitelist()
def check_purchase_order_receipts(doc):
    json_doc=json.loads(doc)
    items = json_doc['items']

    #collect items that are already received
    received_items = []
    items_to_book = []
    for item in items:
        po_item = frappe.db.sql("""
                                SELECT
                                    `received_qty`
                                FROM
                                    `tabPurchase Receipt Item`
                                WHERE
                                    `purchase_order_item` = '{po_detail}'
                                AND
                                    `docstatus` = 1""".format(po_detail=item['po_detail']), as_dict=True)
        if len(po_item) > 0:
            if po_item[0]['received_qty'] == item['qty']:
                received_items.append(item)
            else:
                item['qty'] = item['qty'] - po_item[0]['received_qty']
                items_to_book.append(item)
        else:
            items_to_book.append(item)
    #if the list is empty, proceed normally
    if len(received_items) > 0:
        #remove the update stock checkmark
        json_doc['update_stock'] = 0
    #else remove the update stock checkmark and create a purchase receipt for the rest of the items
    return items_to_book

@frappe.whitelist()
def set_update_stock(doc, value): #value is 0 or 1
    doc=json.loads(doc)
    doc.update_stock = value
    return