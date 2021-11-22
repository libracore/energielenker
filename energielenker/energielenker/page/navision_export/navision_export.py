# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import six
import json
from six import BytesIO
import openpyxl
from openpyxl.styles import Font

@frappe.whitelist()
def get_data(suchparameter, exportieren=False):
    if isinstance(suchparameter, six.string_types):
        suchparameter = json.loads(suchparameter)
    
    if not exportieren:
        # show data
        data = get_datas(suchparameter)
        if data:
            if suchparameter["ansicht_auswahl"] == 'SalesHeader':
                return frappe.render_template('templates/navision_export/navision_exp_salesheader.html', {'invoices': data})
            else:
                return False
        else:
            return False
    else:
        if exist_navisionexport_folder():
            # SalesHeader
            salesheader_raw_data = get_datas(suchparameter)
            salesheader_data = [["Belegart","Nr.","Verk. an Deb.-Nr.","Rech. an Deb.-Nr.","Buchungsdatum","Buchungsbeschreibung","Fälligkeitsdatum","Shortcutdimensionscode 1","Belegdatum","Externe Belegnummer","Datum der Leistung von","Datum der Leistung bis"]]
            
            for sinv in salesheader_raw_data:
                data = []
                data.append("Rechnung")
                data.append("212ERP" + sinv["sinv"].replace("RE", ""))
                data.append(sinv["navision_kundennummer"])
                data.append(sinv["navision_kundennummer"])
                data.append(frappe.utils.get_datetime(sinv["rechnungsdatum"]).strftime('%d.%m.%Y'))
                data.append(sinv["buchungsbeschreibung"])
                data.append(frappe.utils.get_datetime(sinv["due_date"]).strftime('%d.%m.%Y'))
                data.append("1000800")
                data.append(frappe.utils.get_datetime(sinv["rechnungsdatum"]).strftime('%d.%m.%Y'))
                data.append(sinv["sinv"])
                salesheader_data.append(data)
            
            salesline_data = [["Belegart","Belegnr.","Zeilennr.","Art","Nr.","Lagerortcode","Beschreibung","Einheit","Menge","VK-Preis","Shortcutdimensionscode 1","MwSt.-Geschäftsbuchungsgruppe","MwSt.-Produktbuchungsgruppe","Einheitencode"]]
            
            xlsx_file = make_navision_xlsx(salesheader_data, salesline_data)
            file_data = xlsx_file.getvalue()
            
            _file = frappe.get_doc({
            "doctype": "File",
            "file_name": "{title}_{date_von}_{date_bis}.xlsx".format(date_von=suchparameter["date_von"], date_bis=suchparameter["date_bis"], title='SalesHeader'),
            "folder": "Home/NavisionExport",
            "is_private": 1,
            "content": file_data})
            _file.save()
            
            return True
    # fallback
    return False

def exist_navisionexport_folder():
    exist = frappe.db.sql("""SELECT COUNT(`name`) AS `qty` FROM `tabFile` WHERE `name` = 'Home/NavisionExport' AND `is_folder` = 1""", as_dict=True)
    if exist[0].qty != 1:
        new_folder = frappe.get_doc({
            "doctype": "File",
            "file_name": "NavisionExport",
            "folder": "Home",
            "is_folder": 1
        })
        new_folder.insert()
        frappe.db.commit()
    return True
        
        
def make_navision_xlsx(salesheader_data, salesline_data):

    wb = openpyxl.Workbook(write_only=True)
    
    # SalesHeader
    ws = wb.create_sheet('SalesHeader', 0)
    row1 = ws.row_dimensions[1]
    row1.font = Font(name='Calibri',bold=False)
    for row in salesheader_data:
        clean_row = []
        for item in row:
            clean_row.append(item)

        ws.append(clean_row)
        
    # SalesLine
    ws = wb.create_sheet('SalesLine', 1)
    row1 = ws.row_dimensions[1]
    row1.font = Font(name='Calibri',bold=False)
    for row in salesline_data:
        clean_row = []
        for item in row:
            clean_row.append(item)

        ws.append(clean_row)

    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    return xlsx_file

def get_datas(suchparameter):
    if suchparameter["ansicht_auswahl"] == 'SalesHeader':
        # SalesHeader
        sinvs = frappe.db.sql("""SELECT `name`, `customer`, `posting_date`, `due_date`, `billing_type`, `project` FROM `tabSales Invoice` WHERE `posting_date` BETWEEN '{date_von}' AND '{date_bis}' AND `docstatus` = 1""".format(date_von=suchparameter["date_von"], date_bis=suchparameter["date_bis"]), as_dict=True)
        datas = []
        for sinv in sinvs:
            navision_kundennummer = frappe.get_doc("Customer", sinv.customer).navision_nr
            buchungsbeschreibung = sinv.billing_type
            if buchungsbeschreibung != 'Rechnung':
                buchungsbeschreibung += ' zu Projekt Nr. {projekt}'.format(projekt=sinv.project)
            data = {
                'sinv': sinv.name,
                'navision_kundennummer': navision_kundennummer,
                'rechnungsdatum': sinv.posting_date,
                'buchungsbeschreibung': buchungsbeschreibung,
                'due_date': sinv.due_date
            }
            datas.append(data)
        if len(datas) > 0:
            return datas
        else:
            return False
    else:
        # SalesLine
        return False
    # fallback
    return False
