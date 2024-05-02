# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Depot(Document):
	pass

def route_to_page(self, event):
    # ~ raise frappe.redirect("/desk?depot='{depot}'#depot-verarbeitung".format(depot=self.name))
    return
