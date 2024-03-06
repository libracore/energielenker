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
			so_item = frappe.db.sql("""
				SELECT `soitem`.`delivered_by_supplier`
				FROM `tabSales Order Item` AS `soitem`
				LEFT JOIN `tabPurchase Order Item` AS `poitem` ON `poitem`.`sales_order_item` = `soitem`.`name`
				WHERE `poitem`.`name` = '{po_detail}'
				AND `poitem`.`docstatus` = 1
				AND `soitem`.`docstatus` = 1""".format(po_detail=item['po_detail']), as_dict=True)
			#if one item is streckengeschaeft, dont update stock - discussed with MR. Ruhkamp by call
			if so_item[0]['delivered_by_supplier'] == 1:
				update_stock = 0
				
	return update_stock
