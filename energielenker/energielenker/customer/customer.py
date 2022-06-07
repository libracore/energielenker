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
def erstelle_supportrechnung(customer, von, bis, adresse, support_kunde):
    sinv = False
    if int(support_kunde) == 1:
        sup_1 = {
            'qty': 0.00,
            'beschreibung': []
        }
        sup_2 = {
            'qty': 0.00,
            'beschreibung': []
        }
        sup_3 = {
            'qty': 0.00,
            'beschreibung': []
        }
    
    tickets = frappe.db.sql("""SELECT `name` FROM `tabIssue` WHERE `address` = '{adresse}'""".format(adresse=adresse), as_dict=True)
    
    for ticket in tickets:
        time_logs = frappe.db.sql("""SELECT
                                        `tabTimesheet Detail`.`hours` AS `hours`,
                                        `tabTimesheet Detail`.`from_time` AS `from_time`,
                                        `tabTimesheet Detail`.`remarks` AS `remarks`,
                                        `tabTimesheet Detail`.`name` AS `time_log_name`,
                                        `tabTimesheet`.`employee` AS `employee`,
                                        `tabTimesheet`.`employee_name` AS `employee_name`
                                    FROM `tabTimesheet Detail`
                                    LEFT JOIN `tabTimesheet`
                                    ON `tabTimesheet Detail`.`parent` = `tabTimesheet`.`name`
                                    WHERE `from_time` >= '{von} 00:00:00' AND `from_time` <= '{bis} 23:59:59'
                                    AND `tabTimesheet Detail`.`issue` = '{ticket}'
                                    AND `tabTimesheet Detail`.`billed_with_support` != 1""".format(von=von, bis=bis, ticket=ticket.name), as_dict=True)
        if int(support_kunde) == 1:
            for time_log in time_logs:
                if float(time_log.hours) > 0:
                    employee = frappe.get_doc("Employee", time_log.employee)
                    support_level = int(employee.support_level)
                    if support_level == 1:
                        sup_1['qty'] = float(sup_1['qty']) + float(time_log.hours)
                        sup_1['beschreibung'].append('{employee_name}, {from_time}, {hours}h:<br>{remarks}<br>'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks or ''))
                    elif support_level == 2:
                        sup_2['qty'] = float(sup_2['qty']) + float(time_log.hours)
                        sup_2['beschreibung'].append('{employee_name}, {from_time}, {hours}h:<br>{remarks}<br>'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks or ''))
                    elif support_level == 3:
                        x = sup_3['qty']
                        sup_3['qty'] = float(sup_3['qty']) + float(time_log.hours)
                        sup_3['beschreibung'].append('{employee_name}, {from_time}, {hours}h:<br>{remarks}<br>'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks or ''))
                    else:
                        sup_1['qty'] = float(sup_1['qty']) + float(time_log.hours)
                        sup_1['beschreibung'].append('{employee_name}, {from_time}, {hours}h:<br>{remarks}<br>'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks or ''))
                    
                    mark_timelog_as_billed = frappe.db.sql("""UPDATE `tabTimesheet Detail` SET `billed_with_support` = 1 WHERE `name` = '{time_log_name}'""".format(time_log_name=time_log.time_log_name), as_list=True)
        else:
            for time_log in time_logs:
                if float(time_log.hours) > 0:
                    if not sinv:
                        sinv = frappe.new_doc("Sales Invoice")
                        sinv.customer = customer
                        sinv.customer_address = adresse
                        sinv.shipping_address_name = adresse
                    row = sinv.append('items', {})
                    row.item_code = get_item(time_log.employee)
                    beschreibung = '{employee_name}, {from_time}, {hours}h:<br>{remarks}'.format(employee_name=time_log.employee_name, from_time=frappe.utils.get_datetime(time_log.from_time).strftime('%d.%m.%Y'), hours=time_log.hours, remarks=time_log.remarks or '')
                    row.description = beschreibung
                    row.qty = float(time_log.hours)
                    mark_timelog_as_billed = frappe.db.sql("""UPDATE `tabTimesheet Detail` SET `billed_with_support` = 1 WHERE `name` = '{time_log_name}'""".format(time_log_name=time_log.time_log_name), as_list=True)
    
    if int(support_kunde) == 1:
        if (sup_1['qty'] + sup_2['qty'] + sup_3['qty']) > 0:
            sinv = frappe.new_doc("Sales Invoice")
            sinv.customer = customer
            sinv.customer_address = adresse
            sinv.shipping_address_name = adresse
        if sup_1['qty'] > 0:
            row = sinv.append('items', {})
            row.item_code = frappe.db.get_single_value('energielenker Settings', 'support_1')
            row.qty = float(sup_1['qty'])
            beschreibung = '<b>1st-Level Support: {qty}h</b><br>'.format(qty=sup_1['qty'])
            beschreibung += '<br>'.join(sup_1['beschreibung'])
            row.description = beschreibung
        if sup_2['qty'] > 0:
            row = sinv.append('items', {})
            row.item_code = frappe.db.get_single_value('energielenker Settings', 'support_2')
            row.qty = float(sup_2['qty'])
            beschreibung = '<b>2nd-Level Support: {qty}h</b><br>'.format(qty=sup_2['qty'])
            beschreibung += '<br>'.join(sup_2['beschreibung'])
            row.description = beschreibung
        if sup_3['qty'] > 0:
            row = sinv.append('items', {})
            row.item_code = frappe.db.get_single_value('energielenker Settings', 'support_3')
            row.qty = float(sup_3['qty'])
            beschreibung = '<b>3rd-Level Support: {qty}h</b><br>'.format(qty=sup_3['qty'])
            beschreibung += '<br>'.join(sup_3['beschreibung'])
            row.description = beschreibung
        
        if sinv:
            sinv.flags.ignore_mandatory = True
            sinv.save()
            return sinv.name
        else:
            return 'no sinv'
    else:
        if sinv:
            sinv.flags.ignore_mandatory = True
            sinv.save()
            return sinv.name
        else:
            return 'no sinv'

def get_item(employee):
    employee = frappe.get_doc("Employee", employee)
    support_level = int(employee.support_level)
    if support_level == 1:
        return frappe.db.get_single_value('energielenker Settings', 'support_1')
    elif support_level == 2:
        return frappe.db.get_single_value('energielenker Settings', 'support_2')
    elif support_level == 3:
        return frappe.db.get_single_value('energielenker Settings', 'support_3')
    else:
        return frappe.db.get_single_value('energielenker Settings', 'support_1')

@frappe.whitelist()
def get_adressen_zum_verrechnen(customer):
    adressen_zum_verrechnen_aus_tickets = frappe.db.sql("""SELECT DISTINCT
                                                                `issue`.`address`
                                                            FROM `tabIssue` AS `issue`
                                                            WHERE
                                                                `issue`.`name` IN (
                                                                    SELECT `ts`.`issue` FROM `tabTimesheet Detail` AS `ts` WHERE `ts`.`billed_with_support` != 1
                                                                )
                                                            AND (
                                                                (
                                                                    `issue`.`customer` = '{customer}'
                                                                    AND `issue`.`address` IS NOT NULL
                                                                )
                                                                OR
                                                                `issue`.`address` IN (
                                                                    SELECT DISTINCT `name` FROM `tabAddress` WHERE `support_wird_verrechnet_ueber` = '{customer}'
                                                                )
                                                            )""".format(customer=customer), as_list=True)
    adress_liste = []
    
    for a in adressen_zum_verrechnen_aus_tickets:
        adress_liste.append(a[0])
    return adress_liste
    
