# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Besuchsbericht(Document):
    def set_status(self):
        if self.customer:
            qty = frappe.db.count('Customer', {'name': self.customer})
            if qty > 0:
                return 'Bestandskunde'
            else:
                return 'Neukunde'
        else:
            return 'Interessent'
