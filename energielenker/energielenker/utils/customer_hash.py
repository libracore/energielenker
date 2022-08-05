# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import hashlib

@frappe.whitelist()
def get_customer_hash(value=None):
    if value:
        hashed_string = hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    if not value:
        hashed_string = ''
    return hashed_string
