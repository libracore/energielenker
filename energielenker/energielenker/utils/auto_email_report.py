# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today
from frappe.email.doctype.auto_email_report.auto_email_report import send_now

def send_monthly_reports():

    # Fetch records where "send_report_on_x_day" is checked
    sql_query = """
        SELECT 
            `name`,
            `x_day_setup`
        FROM
            `tabAuto Email Report`
        WHERE `frequency` = "am X Tag" 
        AND `enabled` = 1
    """
    reports_to_send = frappe.db.sql(sql_query, as_dict=True)

    # Get the current day of the month
    current_day_of_month = frappe.utils.now_datetime().day

    for report in reports_to_send:
        # Check if today is the day specified in x_day_setup
        if current_day_of_month == int(report.x_day_setup):
            '''Send Auto Email report now'''
            try:
                send_now(report['name'])
            except Exception as err:
                frappe.log_error("{0}\n\n{1}".format(err, report_to_be_send.name))
