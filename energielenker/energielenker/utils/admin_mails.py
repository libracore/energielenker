# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def stop(self, event):
    found = False
    if len(self.recipients) > 0:
        for rec in self.recipients:
            if rec.recipient == 'Administrator <admin@example.com>':
                found = True
    if found:
        remove_admin(self.name)

def remove_admin(queue):
    q = frappe.get_doc("Email Queue", queue)
    old_recipients = q.recipients
    q.recipients = []
    for old_recipient in old_recipients:
        if old_recipient.recipient != 'Administrator <admin@example.com>':
            q.recipients.append(old_recipient)
    q.save()
