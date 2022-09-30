# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import add_months, nowdate
from erpnext.selling.doctype.quotation.quotation import Quotation

@frappe.whitelist() 
def change_status_from_old_angebote():
	months = add_months(nowdate(), -6)
	angebots = frappe.db.sql("""SELECT `name` FROM `tabQuotation` WHERE `status` = 'Open' AND `tabQuotation`.`valid_till` <= '{months}' """.format(months=months), as_dict=True)
	
	for angebot in angebots:
		
		angebot_doc = frappe.get_doc("Quotation", angebot['name'])
		lost_reasons_list = [{'lost_reason': 'unbekannt (Ausschreibung)'}]
		
		#set angebot status to lost after being more than 6 months old
		try:
			Quotation.declare_enquiry_lost(angebot_doc, lost_reasons_list)
		except Exception as err:
			frappe.log_error(err, "change angebot status_: mark angebot {0}".format(angebot_doc.name))
	return
