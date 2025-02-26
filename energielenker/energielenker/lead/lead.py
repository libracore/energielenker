# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (validate_email_address, cint, has_gravatar, getdate, nowdate)
from datetime import datetime, timedelta
from erpnext.crm.doctype.lead.lead import Lead

@frappe.whitelist()
def update_lead_status(self, method):
    #************************************************************************************
    #overwrite the lead validation where set_status is called
    overwrite_lead_validation()
    #************************************************************************************
    
    # Query to retrieve all quotations that are linked to a lead
    if (self.quotation_to == 'Lead'):
        lead = frappe.get_doc("Lead", self.party_name)
        quotations = frappe.get_all('Quotation', filters={'quotation_to': 'Lead', 'party_name': lead.name, 'docstatus': 1}, fields=['name', 'status', 'valid_till'])

        # if there is an open quotation, set the status to "Quotation", if there is a lost quotation, set the status to "Lost Quotation", if all quotations are expired, set the status to "Verfallenes Angebot"
        if quotations:
            any_open = any(q.status == 'Open' for q in quotations)
            all_expired = all(q.status == 'Expired' for q in quotations)
            any_lost = any(q.status == 'Lost' for q in quotations)
            
            if any_open:
                try:
                    lead.status = 'Quotation'
                except Exception as err:
                    frappe.log_error(err, "lead.status {0}".format(lead.status))
            elif any_lost:
                try:
                    lead.status = 'Lost Quotation'
                    lead.contact_date = ''
                except Exception as err:
                    frappe.log_error(err, "lead.status {0}".format(lead.status))
            elif all_expired:
                try:
                    lead.status = 'Verfallene Angebote'
                    lead.contact_date = ''
                except Exception as err:
                    frappe.log_error(err, "lead.status {0}".format(lead.status))
            else:
                #status remains unchanged
                pass
        else:
            lead.status = 'Lead'
        lead.save(ignore_permissions=True)

def overwrite_lead_validation():
    Lead.validate = lead_validation
    
def lead_validation(self):
    #original lead exkl. self.set_status() and Follow Up dates

    self.set_lead_name()
    self._prev = frappe._dict({
        "contact_date": frappe.db.get_value("Lead", self.name, "contact_date") if \
            (not cint(self.get("__islocal"))) else None,
        "ends_on": frappe.db.get_value("Lead", self.name, "ends_on") if \
            (not cint(self.get("__islocal"))) else None,
        "contact_by": frappe.db.get_value("Lead", self.name, "contact_by") if \
            (not cint(self.get("__islocal"))) else None,
    })

    #self.set_status()

    if self.email_id:
        if not self.flags.ignore_email_validation:
            validate_email_address(self.email_id, True)

        if self.email_id == self.lead_owner:
            frappe.throw(_("Lead Owner cannot be same as the Lead"))

        if self.email_id == self.contact_by:
            frappe.throw(_("Next Contact By cannot be same as the Lead Email Address"))

        if self.is_new() or not self.image:
            self.image = has_gravatar(self.email_id)

    # ~ if self.contact_date and getdate(self.contact_date) < getdate(nowdate()):
        # ~ frappe.throw(_("Next Contact Date cannot be in the past"))

    # ~ if self.ends_on and self.contact_date and\
        # ~ (self.ends_on < self.contact_date):
        # ~ frappe.throw(_("Ends On date cannot be before Next Contact Date."))

    

