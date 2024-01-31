# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

import frappe
import re

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

def insert_plz_gebiet(self, event):
    for link in self.links:
        if link.link_doctype == "Lead":
            if not frappe.db.get_value("Lead", link.link_name, "gebiet"):
                _gebiet = self.plz if self.plz and self.is_primary_address == 1 else get_primary_plz(link.link_name, self.plz)
                if _gebiet:
                    gebiet = re.findall(r"[0-9]{2,}", _gebiet)
                    if len(gebiet) > 0:
                        frappe.db.set_value("Lead", link.link_name, "gebiet", gebiet[0][:2])

    return

def get_primary_plz(link_name, fallback):
    gebiet_plz = frappe.db.sql("""
        SELECT `address`.`plz`, `address`.`is_primary_address`
        FROM `tabDynamic Link` AS `addresslink`
        LEFT JOIN `tabAddress` AS `address` ON `addresslink`.`parent` = `address`.`name`
        LEFT JOIN `tabLead` AS `lead` ON `addresslink`.`link_name` = `lead`.`name`
        WHERE `addresslink`.`link_name` = '{name}'
        ORDER BY `address`.`is_primary_address` DESC
        """.format(name=link_name), as_dict=True)
    if not gebiet_plz:
        gebiet_plz = [{
            'plz': fallback
        }]
    return gebiet_plz[0]['plz']
