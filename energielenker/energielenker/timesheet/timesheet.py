# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def assign_read_for_all(ts, event):
    frappe.share.add('Timesheet', ts.name, everyone=1, read=1, flags={'ignore_share_permission': True})
