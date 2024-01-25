# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
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

def insert_plz_gebiet(self, event):
	for link in self.links:
		if link.link_doctype == "Lead":
			if not frappe.db.get_value("Lead", link.link_name, "gebiet"):
				gebiet = self.plz if self.is_primary_address == 1 else get_primary_plz(link.link_name)
				frappe.db.set_value("Lead", link.link_name, "gebiet", gebiet[:2])
			
			

	frappe.log_error(gebiet_plz, "gebiet_plz")
	
	return

def get_primary_plz(link_name):
	gebiet_plz = frappe.db.sql("""
		SELECT `address`.`plz`
		FROM `tabDynamic Link` AS `addresslink`
		LEFT JOIN `tabAddress` AS `address` ON `addresslink`.`link_name` = `address`.`name`
		WHERE `addresslink`.`link_name` = '{name}'
		SORT BY `address`.`is_primary_address` DESC
		LIMIT 1
		""".format(name=link_name), as_dict=True)
	return gebiet_plz
