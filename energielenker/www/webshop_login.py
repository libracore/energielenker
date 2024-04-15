# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.auth import LoginManager

no_cache = True

def get_context(context):
    # redirect if already logged in
    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/retrieving_charging_points"
        raise frappe.Redirect

    context["title"] = "Login"
    context['login_name_placeholder'] = "Email Address"

    return context
