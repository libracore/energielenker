# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from energielenker.energielenker.utils.c_fos_schnittstelle import get_license

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
                                            WHERE `lizenzgutschein` = '{lizenzgutschein}'""".format(lizenzgutschein=data['lizenzgutschein']), as_dict=True)
        
        if len(lizenzgutschein) > 0:
            if lizenzgutschein[0].status == 'Gültig':
                # Gültiger Lizenzgutschein
                # bezeiehe Lizenz
                try:
                    lg_1 = frappe.get_doc("Lizenzgutschein", lizenzgutschein[0].name)
                    if len(lg_1.lizenzen) < 1:
                        get_license(order=lg_1.purchase_order, position=lg_1.positions_nummer, test=0, activation=lg_1.aktivierung, evse_count=lg_1.evse_count, voucher=lg_1.name, position_id=lg_1.position_id, geraete_id=data['geraete_id'])
                except:
                    # Lizenzbezug fehlgeschlagen
                    frappe.local.response.http_status_code = 503
                    frappe.local.response.message = "Service Unavailable"
                    return ['503 Service Unavailable', {
                        "error": {
                            "code": 503,
                            "message": "Service Unavailable"
                        }
                    }]
                lg = frappe.get_doc("Lizenzgutschein", lizenzgutschein[0].name)
                lg.status = 'Bezogen'
                lg.geraete_id = data['geraete_id']
                lg.save(ignore_permissions=True)
                frappe.local.response.http_status_code = 200
                frappe.local.response.message = "Success"
                lizenzen = []
                for lizenz in lg.lizenzen:
                    lizenzen.append(json.loads(lizenz.lizenz))
                return ['200 Success', lizenzen]
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

def get_delivery_note_lizenzgutschein(item_ref, uom=None):
    total = 0
    codes_counter = 0
    column_counter = 0
    lizenzgutschein = frappe.db.sql("""SELECT
                            `lizenzgutschein`
                        FROM `tabLizenzgutschein`
                        WHERE `position_id` IN (
                            SELECT
                                `name`
                            FROM `tabPurchase Order Item`
                            WHERE `sales_order_item` = '{item_ref}'
                        )""".format(item_ref=item_ref), as_dict=True)
    if len(lizenzgutschein) > 0:
        uom_evse_count = get_evse_count_qty()
        if uom:
            return_string = """Anzahl der enthaltenen Ladepunkte je Ladepunkt-Key: <span style="margin: 0px !important; padding-left: 2px !important; font-weight: bold !important;">{0}</span><br>Mit dem/den nachfolgend genannten Ladepunkt-Key/s kann/können unter <u>https://license.energielenker.de</u> die Ladepunkt-Keyfile/s aktiviert und heruntergeladen werden.<br>""".format(uom_evse_count[uom])
            return_string += """Ladepunkt-Keys: <table style="width: 100%; margin-top: 10px !important; "> <tr> <td style="padding: 1px !important; ">"""
        else:
            return_string = """Ladepunkt-Keys: <table table style="width: 100%; margin-top: 10px !important;"> <tr> <td style="padding: 1px !important; ">"""
        for l in lizenzgutschein:
            total += 1
            # ~ frappe.msgprint("lizenzgutschein {0}".format(len(lizenzgutschein)))
            if total == len(lizenzgutschein):
                return_string += """{0}<br></td></tr></table>""".format(l.lizenzgutschein)
            elif codes_counter == 20 and column_counter == 4:
                return_string += """</td></tr></table><table table style="width: 100%; margin-top: 10px !important; margin-bottom: 10px !important; "> <tr> <td style="padding: 1px !important; "><td style="padding: 1px !important; ">{0}<br>""".format(l.lizenzgutschein)
                codes_counter = 0
                column_counter = 0
            elif codes_counter == 20:
                return_string += """ </td>"""
                return_string += """<td style="padding: 1px !important; ">{0}<br>""".format(l.lizenzgutschein)
                codes_counter = 0
                column_counter += 1
            else:
                return_string += """{0}<br>""".format(l.lizenzgutschein)
            
            codes_counter += 1
        
        return return_string
    else:
        return ''

@frappe.whitelist()
def get_evse_count_qty():
    uoms = frappe.db.sql("""SELECT * FROM `tabUOM`""", as_dict=True)
    uom_evse_count = {}
    for uom in uoms:
        if int(uom.manuelle_evse_count_definition) == 1:
            uom_evse_count[uom.name] = int(uom.evse_count)
        else:
            uom_evse_count[uom.name] = 1
    return uom_evse_count

def get_lizenz_qty_so(uom):
    uom_evse_count = get_evse_count_qty()
    return """Anzahl der enthaltenen Ladepunkte: <span style="margin: 0px !important; padding-left: 2px !important; font-weight: bold !important;">{0}</span>""".format(uom_evse_count[uom])
