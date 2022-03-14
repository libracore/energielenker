# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def fetch_payment_schedule_from_so(so, event):
    from energielenker.energielenker.project.project import fetch_payment_schedule
    fetch_payment_schedule(project=so.project, sales_order=so.name, payment_schedule=so.payment_schedule)
    return
