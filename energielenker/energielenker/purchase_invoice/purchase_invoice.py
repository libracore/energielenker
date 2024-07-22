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
    update_stock = 1

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
        new_item = {
                    'item_code': item['item_code'],
                    'item_name': item['item_name'],
                    'description': item['description'],
                    'received_qty': item['qty'],
                    'qty': item['qty'], 
                    'uom': item['uom'], 
                    'stock_uom': item['stock_uom'],
                    'conversion_factor': item['conversion_factor'], 
                    'stock_qty': item['stock_qty'], 
                    'rate': item['rate'], 
                    'amount': item['amount'],
                    'base_rate': item['base_rate'],
                    'base_amount': item['base_amount'],
                    'purchase_order': item['purchase_order'],
                    'purchase_order_item': item['po_detail']
                    }


        if len(po_item) > 0:
            if po_item[0]['received_qty'] == item['qty']:
                received_items.append(item)
            else:
                new_item['received_qty'] = item['qty'] - po_item[0]['received_qty']
                new_item['qty'] = item['qty'] - po_item[0]['received_qty']
                received_items.append(item)
                items_to_book.append(new_item)
        else:
            items_to_book.append(new_item)
    #if the list is empty, proceed normally
    if len(received_items) > 0:
        #if some items are already received, dont update stock
        update_stock = 0
        #create a purchase receipt for the remaining items
        purchase_receipt = frappe.get_doc({
            'doctype': 'Purchase Receipt',
            'supplier': json_doc['supplier'],
            'items': items_to_book
        })
        purchase_receipt.insert()
        purchase_receipt.submit()
        #set status of the purchase receipt to completed
        frappe.db.commit()
        
    return update_stock

@frappe.whitelist()
def set_update_stock(doc, value): #value is 0 or 1
    doc=json.loads(doc)
    doc.update_stock = value
    return