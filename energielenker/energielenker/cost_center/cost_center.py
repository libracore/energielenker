# -*- coding: utf-8 -*-
# Copyright (c) 2026, libracore and contributors
# For license information, please see license.txt
import frappe

def update_kst_code(self, event):
    old_doc = frappe.get_doc("Cost Center", self.get('name'))
    
    #if KST Code has changed, update revenue type with this cost center
    if self.get('kst_code') != old_doc.get('kst_code'):
        update_revenue_types = frappe.db.sql("""
                                        UPDATE
                                            `tabRevenue Type`
                                        SET
                                            `kst_code` = %(kst)s
                                        WHERE
                                            `cost_center` = %(cc)s;""", {'kst': self.get('kst_code'), 'cc': self.get('name')}, as_dict=True)
    
    return
