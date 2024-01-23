# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

# Sales Order -> Project
def so_to_project(sales_order=False, payment_schedule=False, project=False, pb_ignorieren=False, event=False):
    if 'basestring' not in globals():
        basestring = str
    
    if payment_schedule and isinstance(payment_schedule, basestring):
        payment_schedule = json.loads(payment_schedule)
    elif not payment_schedule:
        # cancel if no SO
        if not sales_order:
            return
        payment_schedule = frappe.get_doc("Sales Order", sales_order).payment_schedule
    
    # cancel if no payment schedule
    if not payment_schedule:
        return
    
    # cancel if no project
    if not project:
        if not sales_order:
            return
        if not frappe.get_doc("Sales Order", sales_order).project_clone:
            return
        else:
            project = frappe.get_doc("Sales Order", sales_order).project_clone
        
    project = frappe.get_doc("Project", project)
    if event and event == "so_update":
        project.so_update = 1
    
    # check all over percent
    aop = 0
    for ps in payment_schedule:
        try:
            ps = ps.as_dict()
        except:
            pass
        aop += ps["invoice_portion"]
    if aop < 99.998:
        frappe.throw("In Summe muss der Zahlungsplann 100% ergeben.")
        return
    
    for ps in payment_schedule:
        try:
            ps = ps.as_dict()
        except:
            pass
        if 'name' in ps and frappe.db.exists("Payment Forecast", {"so_ref": ps['name']}):
            # update
            for pps in project.payment_schedule:
                if pps.so_ref == ps['name']:
                    # ~ ps = ps.as_dict()
                    pps.order = sales_order
                    pps.date = ps["due_date"]
                    pps.amount = ps["payment_amount"]
                    pps.percent = ps["invoice_portion"]
                    pps.projektbewertung_ignorieren = pb_ignorieren
        else:
            if not 'to_delete' in ps:
                # create
                try:
                    ps = ps.as_dict()
                except:
                    pass
                new_ps = project.append('payment_schedule', {})
                new_ps.order = sales_order
                new_ps.date = ps["due_date"]
                new_ps.amount = ps["payment_amount"]
                new_ps.percent = ps["invoice_portion"]
                new_ps.so_ref = ps["name"]
                new_ps.projektbewertung_ignorieren = pb_ignorieren
    project.save()

# changes after submit
@frappe.whitelist()
def change_in_so(so, payment_schedule):
    if 'basestring' not in globals():
        basestring = str
    
    if payment_schedule and isinstance(payment_schedule, basestring):
        payment_schedule = json.loads(payment_schedule)
    
    ps_idx = len(frappe.get_doc("Sales Order", so).payment_schedule) + 1
    for ps in payment_schedule:
        if not 'name' in ps:
            so_ps = frappe.get_doc({
                "doctype": "Payment Schedule",
                "due_date": ps["due_date"],
                "payment_amount": ps["payment_amount"],
                "invoice_portion": ps["invoice_portion"],
                "description": ps["description"],
                "parenttype": "Sales Order",
                "parentfield": "payment_schedule",
                "parent": so,
                "idx": ps_idx
            })
            so_ps.insert()
            ps['name'] = so_ps.name
            ps_idx += 1
        else:
            if 'to_delete' in ps:
                if int(ps['to_delete']) == 1:
                    frappe.db.sql("""DELETE FROM `tabPayment Schedule` WHERE `name` = '{0}'""".format(ps['name']), as_list=True)
                    frappe.db.sql("""DELETE FROM `tabPayment Forecast` WHERE `so_ref` = '{0}'""".format(ps['name']), as_list=True)
            else:
                frappe.db.sql("""UPDATE `tabPayment Schedule` SET
                                    `due_date` = '{due_date}',
                                    `payment_amount` = '{payment_amount}',
                                    `invoice_portion` = '{invoice_portion}',
                                    `description` = '{description}'
                                WHERE `name` = '{name}'""".format(due_date=ps['due_date'], \
                                payment_amount=ps['payment_amount'], \
                                invoice_portion=ps['invoice_portion'], \
                                name=ps['name'], \
                                description=ps['description']), as_list=True)
    
    so_to_project(sales_order=so, payment_schedule=payment_schedule, project=False)

#Look over the CB projektbewertung_ignorieren
@frappe.whitelist()
def update_projektbewertung_ignorieren_in_project_or_in_so(self, event, pb_ignorieren=False):  
    if self.doctype == "Project":
        if self.so_update == 1:
            frappe.db.set(self, 'so_update', 0)
        else:
            for ps in self.payment_schedule:
                so = frappe.get_doc("Sales Order", ps.order)
                if so.projektbewertung_ignorieren  != ps.projektbewertung_ignorieren:
                    so.projektbewertung_ignorieren = ps.projektbewertung_ignorieren
                    so.save()
                    return
                
    elif self.doctype == "Sales Order":
        payment_schedule = frappe.db.sql("""SELECT * FROM `tabPayment Schedule` WHERE `parent` = '{0}'""".format(self.name), as_dict=True)
        so_to_project(sales_order=self.name, payment_schedule=payment_schedule, project=self.project_clone, pb_ignorieren=pb_ignorieren, event=event)
