# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
import sys
sys.path.append('/home/frappe/.local/lib/python3.9/site-packages')
from sshtunnel import SSHTunnelForwarder
import requests
from frappe.utils import get_site_name
import json
from frappe.utils.password import get_decrypted_password

@frappe.whitelist()
def get_license(order=None, position=None, test=0, activation=1, evse_count=1, voucher=False, position_id=None, geraete_id=None):
    '''
        Beschreibung
        ----------------
        Dieser API Endpunkt erlaubt das Bestellen und Downloaden einer Lizenz für den cFos Charging Manager.
        Die Lizenz wird für die übergebenen Daten ausgestellt. Die Abrechnung erfolgt getrennt von dem Bestellprozess.
        
        Beschreibung der Felder des JSON-Requests:
        ---------------------------------------------
        - Das Feld test kann zum testen die Werte von 1–4 annehmen, Details siehe unten. Für die Bestellung einer funktionierenden Lizenz muss es 0 enthalten.
        - Das Feld keyphrase muss das Passwort zum Laden des Schlüssels zum Signieren der Lizenz beinhalten.
        - Das Feld entity muss für Energielenker auf 1 stehen.
        - Das Feld order_id muss eine beliebige, aber über alle Bestellungen eindeutige Zeichenfolge enthalten, z.B. Bestellnummer.Position.
        - Das Feld activation kann true oder false enthalten und entscheidet darüber, ob die Lizenz vor der Benutzung auf dem Kundenrechner aktiviert werden muss.
        - Das Feld evse_count gibt die Anzahl der Ladepunkte (resp. OCPP-Gateways) an, welche vom Charging Manager unterstützt werden können.
          Werte zwischen 1–100 können angegeben werden. Die obere Grenze ist nur zur Sicherheit gegen Fehler eingebaut und kann auf Rückfrage erhöht werden.
        - Die anderen Felder können beliebige Werte beinhalten, die so in die Lizenz übernommen werden. Die Felder town und email müssen ausgefüllt werden, ebenso mindestens eines der name... Felder.
        
        Fehler
        -------
        Im Falle von Fehlern werden folgende HTTP Statuswerte zurückgegeben:
        - 400, Bad request
        - 401, Unauthorized
        - 403, Forbidden
        - 409, Conflict
        
        Tests
        ------
        Der Wert test kann die Werte 0–4 annehmen.
        Bei Angabe der Werte 1–4 wird nur ein Teil des Ablaufs der Bestellung durchgeführt.
        Diese Werte können zum Testen des Prozesses verwendet werden, ohne dabei eine kostenpflichtige Lizenz abzurufen.
        
        1: Der Benutzer wird authentisiert und der JSON-String der Anfrage wird gelesen.
        2: Wie 1, zusätzlich werden alle Felder des Requests überprüft und in die Lizenz übernommen.
        3: Wie 2, zusätzlich wird der Schlüssel zum Signieren mittels des Passworts in keyphrase gelesen.
        4: Wie 3, zusätzlich wird die Bestellung gespeichert, aber nicht signiert. Diesen Aufruf bitte selten ausführen, da jeweils eine Seriennummer verbraucht wird.
        0: Der Prozess wird vollständig durchlaufen. Die Bestellung wird gespeichert und es wird eine signierte Lizenz zurückgegeben.
'''

    if not order or not position or not frappe.db.exists("Purchase Order", order):
        frappe.throw("Ein Lieferantenauftrag ist zwingend erforderlich.")
    
    #Get Credentials
    url = frappe.db.get_single_value('energielenker Settings', 'cfos_new_url')
    user = frappe.db.get_single_value('energielenker Settings', 'cfos_new_user')
    password = get_decrypted_password('energielenker Settings', 'energielenker Settings', 'cfos_new_password', False)
    
    #Get Sales Order
    sales_order = None
    if voucher:
        sales_order = frappe.get_value("Lizenzgutschein", voucher, "kundenauftrag")
    
    # define API request data
    data = { 
        "order_id": "{order}:{position}:{position_id}".format(order=order, position=position or 'no_pos', position_id=position_id or 'no_id'),
        "evse_count": int(evse_count),
        "hardware_id": geraete_id or None,
        "contract_order_id": sales_order
    }

    # post API request
    r = requests.post(url, json=data, auth=(user, password))
    
    # check request
    if r.status_code == 200:
        # get license as JSON
        try:
            license_file_data = json.dumps(r.json()['license'])
        except:
            license_file_data = json.dumps(r.json())
        if not voucher:
            license_file = frappe.get_doc({
                "doctype": "File",
                "file_name": 'license_{order}_{position}_{position_id}.json'.format(order=order, position=position, position_id=position_id or 'no_id'),
                "folder": "Home/Attachments",
                "is_private": 1,
                "content": license_file_data,
                "attached_to_doctype": 'Purchase Order',
                "attached_to_name": order
            })
                
            license_file.save(ignore_permissions=True)
        else:
            license_file = frappe.get_doc({
                "doctype": "File",
                "file_name": 'license_{order}_{position}_{position_id}.json'.format(order=order, position=position, position_id=position_id or 'no_id'),
                "folder": "Home/Attachments",
                "is_private": 1,
                "content": license_file_data,
                "attached_to_doctype": 'Lizenzgutschein',
                "attached_to_name": voucher
            })
            license_file.save(ignore_permissions=True)
            voucher = frappe.get_doc("Lizenzgutschein", voucher)
            row = voucher.append('lizenzen', {})
            row.lizenz = license_file_data
            voucher.save()
        
    else:
        frappe.throw("<b>Es ist etwas schief gelaufen.</b><br><br><br>Die Antwort der Schnittstelle lautet:<br>Status: {status}<br>Error: {error}".format(status=r.status_code, error=r.text))

@frappe.whitelist()
def create_lizenzgutschein(purchase_order=None, positions_nummer=None, position_id=None, test=0, aktivierung=1, evse_count=1):
    sales_order = None
    if purchase_order:
        sales_order = frappe.get_value("Purchase Order", purchase_order, "sales_order")
    
    lizenzgutschein = frappe.get_doc({
        "doctype": "Lizenzgutschein",
        "purchase_order": purchase_order,
        "positions_nummer": positions_nummer,
        "position_id": position_id,
        "test": test,
        "aktivierung": aktivierung,
        "evse_count": evse_count,
        "kundenauftrag": sales_order
    })
    lizenzgutschein.save()
    frappe.db.commit()
