# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore ag

from __future__ import unicode_literals
import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def call_ladepunkte(call, customer):
	#translate javaskript passing to dictionarys
	receive=json.loads(call)
	#transform strings to ints
	for rec in receive:
		if type(rec['set_size']) is str:
			rec['set_size'] = int(rec['set_size'])
		if type(rec['quantity']) is str:
			rec['quantity'] = int(rec['quantity'])
	#get free amount of ladepunkte for customer
	total_free_ladepunkte, free_ladepunkte_per_so = get_not_recieved_ladepunke(customer)
	#calculate total amount of ladepunkte to recieve
	total_ladepunkte = get_total_recieved_ladepunkte(receive)
	
	frappe.log_error(total_free_ladepunkte, "total_ladepunkte")
	frappe.log_error(free_ladepunkte_per_so, "ladepunkte_per_so")
	
	return

def get_not_recieved_ladepunke(customer):
	
	total_data = frappe.db.sql("""
	SELECT SUM(`soitem`.`qty` - `soitem`.`delivered_qty`) AS `total_freie_ladepunkte`
	FROM `tabSales Order Item` AS `soitem`
	LEFT JOIN `tabSales Order` AS `so` ON `soitem`.`parent` = `so`.`name`
	WHERE `soitem`.`item_code` = 'A-0002006'
	AND `so`.`customer` = '{cust}'
	AND `so`.`docstatus` = 1""".format(cust=customer), as_dict=True)
	
	total_amount = 0
	if len(total_data) > 0:
		total_amount = total_data[0].total_freie_ladepunkte
	else:
		total_amount = 0
		
	amount_per_so = frappe.db.sql("""
	SELECT `so`.`name` AS `sales_order`,
		(`soitem`.`qty` - `soitem`.`delivered_qty`) AS `quantity`
	FROM `tabSales Order Item` AS `soitem`
	LEFT JOIN `tabSales Order` AS `so` ON `soitem`.`parent` = `so`.`name`
	WHERE `soitem`.`item_code` = 'A-0002006'
	AND `so`.`customer` = '{cust}'
	AND (`soitem`.`qty` - `soitem`.`delivered_qty`) > 0""".format(cust=customer), as_dict=True)

	return total_amount, amount_per_so
	
def get_total_recieved_ladepunkte(receive):
	total_ladepunkte = 0
	for rec in receive:
		total_ladepunkte += rec['set_size'] * rec['quantity']
	return total_ladepunkte


		
	
	
	
