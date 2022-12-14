# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def add_mail_as_description(self, event):
    communications = frappe.db.sql("""
        SELECT `content`
        FROM `tabCommunication`
        WHERE `reference_doctype` = 'Issue'
        AND `reference_name` = '{issue}'
        ORDER BY `creation` ASC
    """.format(issue=self.name), as_dict=True)
    if len(communications) > 0 and not self.description:
        self.description = communications[0].content
