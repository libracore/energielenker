# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe

def get_plz_gebiet(self, event):
	if not self.gebiet and self.customer_address:
		self.gebiet = frappe.db.get_value("Address", self.customer_address, "plz")[:2]
	return
		
	
