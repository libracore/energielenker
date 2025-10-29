# Copyright (c) 2025, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RevenueType(Document):
	pass

def autoname(self, event):
    self.name = "{0} - {1}".format(self.number, self.description)
