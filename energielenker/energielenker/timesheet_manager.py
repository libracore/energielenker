# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import today, now, get_datetime, add_to_date, nowdate
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
    
    return data

@frappe.whitelist()
def quick_start_timer(ts):
    ts = frappe.get_doc("Timesheet", ts)
    
    row = ts.append('time_logs', {})
    row.activity_type = 'Execution'
    row.from_time = get_datetime()
    row.to_time= get_datetime()
    row.hours = 0
    
    ts.save()
    
    return
    
@frappe.whitelist()
def start_timer(ts, details):
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
            
    ts.save()
    
    return
    
@frappe.whitelist()
def stop_timer(ts):
    ts = frappe.get_doc("Timesheet", ts)
    
    for time_log in ts.time_logs:
        if time_log.hours == 0:
            time_log.to_time = get_datetime()
            
    ts.save()
    
    return

@frappe.whitelist()
def add_timeblock(ts, details):
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
            
    ts.save()
    
    return
    
def get_next_start_time(ts):
    ts = frappe.get_doc("Timesheet", ts)
    start_time = get_datetime(nowdate() + " 00:00:00")
    
    for timelog in ts.time_logs:
        if timelog.from_time == start_time:
            start_time = timelog.to_time
            
    return start_time
