# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe

no_cache = True

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/webshop_login"
        raise frappe.Redirect
    
    context['ladepunkte'] = get_ladepunkte(frappe.session.user)
    return context

def get_ladepunkte(user):
    return 250
