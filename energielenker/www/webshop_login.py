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
def reset_webshop_password(user, send_email=False):
    from frappe.utils import random_string, get_url
    
    self = frappe.get_doc("User", user)
    
    key = random_string(32)
    self.db_set("reset_password_key", key)

    url = "/reset_password_webshop?key=" + key

    link = get_url(url)
    if send_email:
        webshop_password_reset_mail(self, link)
    frappe.msgprint("Eine Anleitung zum Zurücksetzen des Passworts wurde an ihre E-Mail-Adresse verschickt", indicator='green')
    return link
    
def webshop_password_reset_mail(self, link):
    send_webshop_login_mail(self, "Ladepunktabruf - Passwort zurücksetzten",
        "password_reset", {"link": link}, now=True)
        
def send_webshop_login_mail(self, subject, template, add_args, now=None):
    """send mail with login details"""
    from frappe.utils.user import get_user_fullname
    from frappe.utils import get_url
    
    args = {
        'first_name': self.first_name or self.last_name or "user",
        'user': self.name,
        'title': subject,
        'login_url': get_url(),
        'user_fullname': "Administrator"
    }

    args.update(add_args)

    sender = frappe.get_value("Email Account", {"default_outgoing": 1}, "email_id")
    
    frappe.sendmail(recipients=self.email, sender=sender, subject=subject,
        template=template, args=args, header=[subject, "green"],
        delayed=(not now) if now!=None else self.flags.delay_emails, retry=3)
