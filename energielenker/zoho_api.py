# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025, libracore and contributors
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def test():
    frappe.log_error("Maschine", "Maschine")
