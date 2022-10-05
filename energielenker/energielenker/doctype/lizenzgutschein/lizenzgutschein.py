# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Lizenzgutschein(Document):
    def after_insert(self):
        if not self.lizenzgutschein:
            self.create_lizenzgutschein()
    
    def create_lizenzgutschein(self):
        self.lizenzgutschein = frappe.generate_hash(txt=self.name, length=15)
        self.save()

@frappe.whitelist()
def validity_check(**data):
    if 'lizenzgutschein' in data and 'geraete_id' in data:
        lizenzgutschein = frappe.db.sql("""SELECT
                                                *
                                            FROM `tabLizenzgutschein`
                                            WHERE `lizenzgutschein` = '{lizenzgutschein}'
                                            AND `geraete_id` = '{geraete_id}'""".format(lizenzgutschein=data['lizenzgutschein'], geraete_id=data['geraete_id']), as_dict=True)
        
        if len(lizenzgutschein) > 0:
            if lizenzgutschein[0].status == 'Gültig':
                # Gültige Lizenz
                lg = frappe.get_doc("Lizenzgutschein", lizenzgutschein[0].name)
                lg.status = 'Bezogen'
                lg.save(ignore_permissions=True)
                frappe.local.response.http_status_code = 200
                frappe.local.response.message = "Success"
                return ['200 Success', 'Success']
            elif lizenzgutschein[0].status == 'Bezogen':
                # Gültige, aber bereits bezogene Lizenz
                frappe.local.response.http_status_code = 202
                frappe.local.response.message = "Accepted"
                return ['202 Accepted', 'Accepted']
            elif lizenzgutschein[0].status == 'Ungültig':
                # Ungültige/Nicht vorhandene Lizenz
                frappe.local.response.http_status_code = 403
                frappe.local.response.message = "Forbidden"
                return ['403 Forbidden', {
                    "error": {
                        "code": 403,
                        "message": "Forbidden"
                    }
                }]
            
        else:
            # Nicht vorhandene Lizenz
            frappe.local.response.http_status_code = 404
            frappe.local.response.message = "Not Found"
            return ['404 Not Found', {
                "error": {
                    "code": 404,
                    "message": "Not Found"
                }
            }]
    else:
        # Fehlende Keys
        frappe.local.response.http_status_code = 400
        frappe.local.response.message = "Bad Request"
        return ['400 Bad Request', {
            "error": {
                "code": 400,
                "message": "Bad Request"
            }
        }]
