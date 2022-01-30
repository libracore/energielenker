# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def adresse_verknupfen(address, customer):
    address = frappe.get_doc("Address", address)
    row = address.append('links', {})
    row.link_doctype = "Customer"
    row.link_name = customer
    
    address.save()
    return

@frappe.whitelist()
def kontakt_verknupfen(contact, customer):
    contact = frappe.get_doc("Contact", contact)
    row = contact.append('links', {})
    row.link_doctype = "Customer"
    row.link_name = customer
    
    contact.save()
    return

@frappe.whitelist()
def erstelle_supportrechnung(customer, von, bis, adresse):
    sinv = False
    
    tickets = frappe.db.sql("""SELECT `name` FROM `tabIssue` WHERE `customer` = '{customer}' AND `address` = '{adresse}'""".format(customer=customer, adresse=adresse), as_dict=True)
    for ticket in tickets:
        time_logs = frappe.db.sql("""SELECT
                                        `tabTimesheet Detail`.`hours` AS `hours`,
                                        `tabTimesheet Detail`.`from_time` AS `from_time`,
                                        `tabTimesheet Detail`.`remarks` AS `remarks`,
                                        `tabTimesheet`.`employee` AS `employee`,
                                        `tabTimesheet`.`employee_name` AS `employee_name`
                                    FROM `tabTimesheet Detail`
                                    LEFT JOIN `tabTimesheet`
                                    ON `tabTimesheet Detail`.`parent` = `tabTimesheet`.`name`
                                    WHERE `from_time` >= '{von} 00:00:00' AND `from_time` <= '{bis} 23:59:59'""".format(von=von, bis=bis), as_dict=True)
        for time_log in time_logs:
            if not sinv:
                sinv = frappe.new_doc("Sales Invoice")
                sinv.customer = customer
                sinv.customer_address = adresse
            row = sinv.append('items', {})
            row.item_code = get_item(time_log.employee)
            beschreibung = '{employee_name}, {from_time}, {hours}h:<br>{remarks}'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks)
            row.description = beschreibung
            row.qty = float(time_log.hours)
    
    if sinv:
        sinv.flags.ignore_mandatory = True
        sinv.save()
        return sinv.name
    else:
        return 'no sinv'

def get_item(employee):
    employee = frappe.get_doc("Employee", employee)
    support_level = employee.support_level
    if support_level == 1:
        return frappe.db.get_single_value('energielenker Settings', 'support_1')
    elif support_level == 2:
        return frappe.db.get_single_value('energielenker Settings', 'support_2')
    elif support_level == 3:
        return frappe.db.get_single_value('energielenker Settings', 'support_3')
    else:
        return frappe.db.get_single_value('energielenker Settings', 'support_1')
