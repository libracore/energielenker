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
	
	update_stock = 1
	
	for item in doc['items']:
		so_items = frappe.db.sql("""
			SELECT `soitem`.`delivered_by_supplier`
			FROM `tabSales Order Item` AS `soitem`
			LEFT JOIN `tabSales Order` AS `so` ON `soitem`.`parent` = `so`.`name`
			LEFT JOIN `tabPurchase Order Item` AS `poitem` ON `poitem`.`sales_order` = `so`.`name`
			LEFT JOIN `tabPurchase Order` AS `po` ON `poitem`.`parent` = `po`.`name`
			WHERE `po`.`name` = '{po}'
			AND `soitem`.`item_code` = '{item}'
			AND `po`.`docstatus` = 1
			AND `so`.`docstatus` = 1
			GROUP BY `soitem`.`delivered_by_supplier`""".format(po=item['purchase_order'], item=item['item_code']), as_dict=True)
			
		for so_item in so_items:
			if so_item['delivered_by_supplier'] == 1:
				update_stock = 0

	return update_stock
