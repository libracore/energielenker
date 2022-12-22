# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe

def check_for_assigment(self, event):
    if self.reference_type == 'Issue' and self.reference_name:
        zuweisungen = frappe.db.sql("""SELECT `creation` FROM `tabToDo` WHERE `status` = 'Open' AND `reference_type` = 'Issue' AND `reference_name` = '{0}' ORDER BY `creation` ASC""".format(self.reference_name), as_dict=True)
        if len(zuweisungen) > 0:
            frappe.db.set_value("Issue", self.reference_name, 'letzte_zuweisung', zuweisungen[0].creation)
            frappe.db.commit()
        else:
            frappe.db.set_value("Issue", self.reference_name, 'letzte_zuweisung', None)
            frappe.db.commit()
