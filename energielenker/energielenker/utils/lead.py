# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def delete_events(self, event):
    linked_events = frappe.db.sql("""SELECT
                                        `name`
                                    FROM `tabCommunication`
                                    WHERE `name` IN (
                                        SELECT
                                            `parent`
                                        FROM `tabCommunication Link`
                                        WHERE `link_doctype` = 'Lead'
                                        AND `link_name` = '{0}'
                                    )""".format(self.name), as_dict=True)
    for linked_event in linked_events:
        le = frappe.get_doc("Communication", linked_event.name)
        le.delete()
