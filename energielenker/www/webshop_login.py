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

    return context
    
@frappe.whitelist(allow_guest=True)
def reset_password_figgdi(user, send_email=False, password_expired=False):
    from frappe.utils import random_string, get_url
    from frappe.core.doctype.user.user import send_login_mail
    
    self = frappe.get_doc("User", user)
    
    key = random_string(32)
    self.db_set("reset_password_key", key)

    url = "/update-password?key=" + key
    if password_expired:
        url = "/update-password?key=" + key + '&password_expired=true'

    link = get_url(url)
    if send_email:
        self.send_login_mail(_("Password Reset"),
            "password_reset", {"link": link}, now=True)

    return link
