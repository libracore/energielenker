# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import json

def assign_read_for_all(ts, event):
    frappe.share.add('Timesheet', ts.name, everyone=1, read=1, flags={'ignore_share_permission': True})

def validate_manual_invoice(self, event):
    for time_log in self.time_logs:
        if time_log.billed_manually and not time_log.billed_manually_with_sinv:
            frappe.throw("Bitte Rechnung für Zeile {0} angeben".format(time_log.idx))
        elif time_log.billed_manually:
            mark_timelog_as_billed = frappe.db.sql("""UPDATE `tabTimesheet Detail` SET `billed_with_support` = 1 WHERE `name` = '{time_log_name}'""".format(time_log_name=time_log.name), as_list=True)
        elif time_log.billed_with_support and not time_log.billed_manually:
            mark_timelog_as_billed = frappe.db.sql("""UPDATE `tabTimesheet Detail` SET `billed_with_support` = 0 WHERE `name` = '{time_log_name}'""".format(time_log_name=time_log.name), as_list=True)
    return

@frappe.whitelist()
def check_service_projects(doc):
    doc = json.loads(doc)
    
    for time_log in doc.get('time_logs'):
        if time_log.get('project'):
            is_service_project = frappe.get_value("Project", time_log.get('project'), "is_service_project")
            if is_service_project == 1:
                if time_log.get('typisierung') == "time_log.get('project')":
                    return "Projekt {0} ist ein Dienstleistungsprojekt und darf nicht die Typisierung 
