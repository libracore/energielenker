# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import today, now, get_datetime, add_to_date, nowdate, time_diff_in_hours
import json

@frappe.whitelist()
def get_data():
    data = {}
    user = frappe.session.user
    
    # employee
    try:
        data["employee"] = frappe.db.sql("""SELECT `name`, `employee_name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_dict=True)[0]
    except:
        data["employee"] = 0
        
    # current timesheet
    try:
        data["timesheet"] = frappe.db.sql("""SELECT * FROM `tabTimesheet` WHERE `employee` = '{employee}' AND `start_date` = '{nowdate}' AND `docstatus` != '2'""".format(employee=data["employee"]["name"], nowdate=today()), as_dict=True)[0]
        data["timer_status"] = 'stopped'
        zero_hours_qty = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabTimesheet Detail` WHERE `parent` = '{timesheet}' AND `hours` = 0""".format(timesheet=data["timesheet"]["name"]), as_list=True)[0][0]
        if zero_hours_qty > 0:
            data["timer_status"] = 'started'
    except:
        data["timesheet"] = 0
        data["timer_status"] = 'stopped'
    
    return data

@frappe.whitelist()
def quick_start_timer(ts):
    if ts != 'new':
        ts = frappe.get_doc("Timesheet", ts)
        
        row = ts.append('time_logs', {})
        row.activity_type = 'Execution'
        row.from_time = get_datetime()
        row.to_time= get_datetime()
        row.hours = 0
        
        ts.save()
        
        return ts.name
    else:
        user = frappe.session.user
        employee = frappe.db.sql("""SELECT `name`, `employee_name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_dict=True)[0]
        new_ts = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": employee.name,
            "time_logs": [
                {
                    "activity_type": 'Execution',
                    "from_time": get_datetime(),
                    "to_time": get_datetime(),
                    "hours": 0
                }
            ]
        })
        new_ts.insert()
        return new_ts.name
    
@frappe.whitelist()
def start_timer(ts, details):
    if ts != 'new':
        try:
            basestring
        except NameError:
            basestring = str
        if isinstance(details, basestring):
            details = json.loads(details)

        ts = frappe.get_doc("Timesheet", ts)
        
        row = ts.append('time_logs', {})
        row.activity_type = details["activity_type"]
        row.from_time = get_datetime()
        row.to_time= get_datetime()
        row.hours = 0
        
        for key in details:
            if key == 'project':
                row.project = details[key]
            if key == "task":
                row.task = details[key]
            if key == "issue":
                row.issue = details[key]
                
        if int(details["bill"]) == 1:
            rates = get_employee_rate(ts.employee)
            row.billable = 1
            row.billing_hours = 0
            row.billing_rate = rates["external_rate"]
            row.costing_rate = rates["internal_rate"]
                
        ts.save()
        
        return ts.name
    else:
        try:
            basestring
        except NameError:
            basestring = str
        if isinstance(details, basestring):
            details = json.loads(details)
            
        project = ''
        task = ''
        issue = ''
        for key in details:
            if key == 'project':
                project = details[key]
            if key == "task":
                task = details[key]
            #if key == "issue":
            #    issue = details[key]
                
        user = frappe.session.user
        employee = frappe.db.sql("""SELECT `name`, `employee_name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_dict=True)[0]
        
        if int(details["bill"]) == 1:
            rates = get_employee_rate(employee.name)
            billable = 1
            billing_hours = 0
            billing_rate = rates["external_rate"]
            costing_rate = rates["internal_rate"]
        else:
            billable = 0
            billing_hours = 0
            billing_rate = 0
            costing_rate = 0
        
        new_ts = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": employee.name,
            "time_logs": [
                {
                    "activity_type": details["activity_type"],
                    "from_time": get_datetime(),
                    "to_time": get_datetime(),
                    "hours": 0,
                    #"issue": issue,
                    "project": project,
                    "task": task,
                    "billable": billable,
                    "billing_hours": billing_hours,
                    "billing_rate": billing_rate,
                    "costing_rate": costing_rate
                }
            ]
        })
        new_ts.insert()
        return new_ts.name
    
@frappe.whitelist()
def stop_timer(ts):
    if ts != 'new':
        ts = frappe.get_doc("Timesheet", ts)
        
        for time_log in ts.time_logs:
            if time_log.hours == 0:
                time_log.to_time = get_datetime()
                if time_log.billable == 1:
                    time_log.billing_hours = time_diff_in_hours(time_log.to_time.strftime("%Y-%m-%d %H:%M:%S"), time_log.from_time.strftime("%Y-%m-%d %H:%M:%S"))
                    time_log.billing_amount = float(time_log.billing_hours) * float(time_log.billing_rate)
                    time_log.costing_amount = float(time_log.billing_hours) * float(time_log.costing_rate)
                
        ts.save()
        
        return ts.name

@frappe.whitelist()
def add_timeblock(ts, details):
    if ts != 'new':
        try:
            basestring
        except NameError:
            basestring = str
        if isinstance(details, basestring):
            details = json.loads(details)

        next_start_time = get_next_start_time(ts)
        ts = frappe.get_doc("Timesheet", ts)
        
        row = ts.append('time_logs', {})
        row.activity_type = details["activity_type"]
        row.from_time = next_start_time
        row.to_time= add_to_date(date=row.from_time, hours=details["hours"])
        row.hours = details["hours"]
        
        for key in details:
            if key == 'project':
                row.project = details[key]
            if key == "task":
                row.task = details[key]
            if key == "issue":
                row.issue = details[key]
                
        if int(details["bill"]) == 1:
            rates = get_employee_rate(ts.employee)
            row.billable = 1
            row.billing_hours = details["hours"]
            row.billing_rate = rates["external_rate"]
            row.costing_rate = rates["internal_rate"]
            row.billing_amount = float(details["hours"]) * float(rates["external_rate"])
            row.costing_amount = float(details["hours"]) * float(rates["internal_rate"])
                
        ts.save()
    
        return ts.name
    else:
        try:
            basestring
        except NameError:
            basestring = str
        if isinstance(details, basestring):
            details = json.loads(details)
            
        start_time = get_datetime(nowdate() + " 00:00:00")
        project = ''
        task = ''
        issue = ''
        for key in details:
            if key == 'project':
                project = details[key]
            if key == "task":
                task = details[key]
            #if key == "issue":
            #    issue = details[key]
                
        user = frappe.session.user
        employee = frappe.db.sql("""SELECT `name`, `employee_name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_dict=True)[0]
        
        if int(details["bill"]) == 1:
            rates = get_employee_rate(employee.name)
            billable = 1
            billing_hours = details["hours"]
            billing_rate = rates["external_rate"]
            costing_rate = rates["internal_rate"]
            billing_amount = float(details["hours"]) * float(rates["external_rate"])
            costing_amount = float(details["hours"]) * float(rates["internal_rate"])
        else:
            billable = 0
            billing_hours = 0
            billing_rate = 0
            costing_rate = 0
            billing_amount = 0
            costing_amount = 0
        
        new_ts = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": employee.name,
            "time_logs": [
                {
                    "activity_type": details["activity_type"],
                    "from_time": start_time,
                    "to_time": add_to_date(date=start_time, hours=details["hours"]),
                    "hours": details["hours"],
                    #"issue": issue,
                    "project": project,
                    "task": task,
                    "billable": billable,
                    "billing_hours": billing_hours,
                    "billing_rate": billing_rate,
                    "costing_rate": costing_rate,
                    "billing_amount": billing_amount,
                    "costing_amount": costing_amount
                }
            ]
        })
        new_ts.insert()
        return new_ts.name
    
def get_next_start_time(ts):
    ts = frappe.get_doc("Timesheet", ts)
    start_time = get_datetime(nowdate() + " 00:00:00")
    
    for timelog in ts.time_logs:
        if timelog.from_time == start_time:
            start_time = timelog.to_time
            
    return start_time

def get_employee_rate(employee):
    employee = frappe.get_doc("Employee", employee)
    if employee.employee_rate:
        try:
            rates = frappe.db.sql("""SELECT `internal_rate`, `external_rate` FROM `tabenergielenker Employee Rate` WHERE `parent` = '{employee}' AND `date` <= '{today}' ORDER BY `date` DESC LIMIT 1""".format(employee=employee.name, today=today()), as_dict=True)[0]
        except:
            rates = {
                'internal_rate': 0,
                'external_rate': 0
            }
    else:
        rates = {
                'internal_rate': 0,
                'external_rate': 0
            }
    return rates
    
