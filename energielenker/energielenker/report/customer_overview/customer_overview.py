# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    columns = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Street"), "fieldname": "street", "fieldtype": "Data", "width": 100},
        {"label": _("PLZ"), "fieldname": "plz", "fieldtype": "Data", "width": 40},
        {"label": _("Locality"), "fieldname": "locality", "fieldtype": "Data", "width": 100},
        {"label": _("Customer Group"), "fieldname": "customer_group", "fieldtype": "Data", "width": 100},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Data", "width": 100},
        {"label": _("Customer Support"), "fieldname": "customer_support", "fieldtype": "Data", "width": 100},
        {"label": _("Lead Owner"), "fieldname": "lead_owner", "fieldtype": "Data", "width": 100},
        {"label": _("Lead Source"), "fieldname": "lead_source", "fieldtype": "Data", "width": 100},
        {"label": _("Website"), "fieldname": "website", "fieldtype": "Data", "width": 100},
        {"label": _("Contact"), "fieldname": "contact", "fieldtype": "Link", "options": "Contact", "width": 80},
        {"label": _("Contact Name"), "fieldname": "contact_name", "fieldtype": "Data", "width": 100},
        {"label": _("Contact First Name"), "fieldname": "contact_first_name", "fieldtype": "Data", "width": 100},
        {"label": _("Contact E-Mail"), "fieldname": "contact_email", "fieldtype": "Data", "width": 100},
        {"label": _("Contact Phone"), "fieldname": "contact_phone", "fieldtype": "Data", "width": 100},
        {"label": _("Contact Mobile"), "fieldname": "contact_moblie", "fieldtype": "Data", "width": 100},
        {"label": _("Contact Description"), "fieldname": "contact_description", "fieldtype": "Data", "width": 100},
        {"label": _("Contact Department"), "fieldname": "contact_department", "fieldtype": "Data", "width": 100},
        {"label": _("Relevant Contact"), "fieldname": "relevant_contact", "fieldtype": "Check", "width": 100}
    ]
    return columns

def get_data():
    data = frappe.db.sql("""
                            SELECT
                                `cust`.`name` AS `customer`,
                                `cust`.`customer_name` AS `customer_name`,
                                `cust`.`customer_group` AS `customer_group`,
                                `cust`.`territory` AS `territory`,
                                `cust`.`ansprechpartner` AS `customer_support`,
                                `cust`.`website` AS `website`,
                                `link`.`relevant_contact` AS `relevant_contact`,
                                `cont`.`name` AS `contact`,
                                `cont`.`first_name` AS `contact_name`,
                                `cont`.`last_name` AS `contact_first_name`,
                                `cont`.`department_clone` AS `contact_description`,
                                `cont`.`funktion` AS `contact_department`,
                                `email`.`email_id` AS `contact_email`,
                                `phone`.`phone` AS `contact_phone`,
                                `moblie`.`phone` AS `contact_moblie`,
                                CONCAT(`addr`.`address_line1`, ' ', `addr`.`hausnummer`) AS `street`,
                                `addr`.`plz` AS `plz`,
                                `addr`.`city` AS `locality`,
                                `lead`.`lead_owner` AS `lead_owner`,
                                `lead`.`source` AS `lead_source`
                            FROM
                                `tabCustomer` AS `cust`
                            INNER JOIN
                                `tabDynamic Link` AS `link` ON `cust`.`name` = `link`.`link_name`
                            INNER JOIN
                                `tabContact` as `cont` ON `link`.`parent` = `cont`.`name`
                            LEFT JOIN
                                `tabContact Email` AS `email` ON `email`.`parent` = `cont`.`name` AND `email`.`is_primary` = 1
                            LEFT JOIN
                                `tabContact Phone` AS `phone` ON `phone`.`parent` = `cont`.`name` AND `phone`.`is_primary_phone` = 1
                            LEFT JOIN
                                `tabContact Phone` AS `moblie` ON `moblie`.`parent` = `cont`.`name` AND `moblie`.`is_primary_mobile_no` = 1
                            INNER JOIN
                                `tabDynamic Link` AS `add_link` ON `cust`.`name` = `add_link`.`link_name`
                            INNER JOIN
                                `tabAddress` as `addr` ON `add_link`.`parent` = `addr`.`name`
                            LEFT JOIN
                                `tabLead` AS `lead` ON `lead`.`name` = `cust`.`lead_name`
                            WHERE
                                `cust`.`disabled` = 0
                            AND
                                `addr`.`is_primary_address` = 1
                            ORDER BY
                                `cust`.`name`""", as_dict=True)
    frappe.log_error(data, "data")                            
                                
    return data
