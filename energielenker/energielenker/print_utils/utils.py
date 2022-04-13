# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def get_print_items(dt, dn):
    doc = frappe.get_doc(dt, dn)
    # ~ items = doc.items
    # ~ print_items = []
    verpackung_versand = []
    summe_interne_positionen = 0
    table = ''
    positions_nummer = 1
    cur_icon = '&euro;' if doc.currency == 'EUR' else doc.currency
    
    # Normale Rechnung
    if doc.billing_type == 'Rechnung':
        for item in doc.items:
            if item.item_group != 'Verpackung / Versand':
                if int(item.textposition) == 1:
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                        </tr>
                        
                    """.format(position=positions_nummer, item_name=item.item_name)
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    positions_nummer += 1
                    table += tr
                
                elif int(item.alternative_position) == 1:
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">Optional:<br>{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{qty}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                        </tr>
                        
                    """.format(position=positions_nummer, \
                            item_name=item.item_name, \
                            qty="{:,.2f}".format(item.qty).replace(",", "'").replace(".", ",").replace("'", "."), \
                            cur_icon=cur_icon, \
                            rate="{:,.2f}".format(item.preis_alternative_position).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    positions_nummer += 1
                    table += tr
                
                elif int(item.interne_position) == 1:
                    summe_interne_positionen += item.amount
                
                elif int(item.kalkulationssumme_interner_positionen) == 1:
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">Optional:<br>{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{qty}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
                        </tr>
                        
                    """.format(position=positions_nummer, \
                            item_name=item.item_name, \
                            qty=1, \
                            cur_icon=cur_icon, \
                            rate="{:,.2f}".format(summe_interne_positionen).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    positions_nummer += 1
                    table += tr
                    summe_interne_positionen = 0
                
                elif int(item.is_supplement) == 1:
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">Nachtrag:<br>{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{qty}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {amount}</td>
                        </tr>
                        
                    """.format(position=positions_nummer, \
                            item_name=item.item_name, \
                            qty="{:,.2f}".format(item.qty).replace(",", "'").replace(".", ",").replace("'", "."), \
                            cur_icon=cur_icon, \
                            rate="{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", "."), \
                            amount="{:,.2f}".format(item.amount).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    positions_nummer += 1
                    table += tr
                
                else:
                    if item.discount_percentage:
                        if item.rate_with_margin:
                            rate = cur_icon + " " + "{:,.2f}".format(item.rate_with_margin).replace(",", "'").replace(".", ",").replace("'", ".") + \
                                    '<br>' + '-' + str(item.discount_percentage) + '%<br>' + cur_icon + " " + "{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", ".")
                        else:
                            rate = cur_icon + " " + "{:,.2f}".format(item.price_list_rate).replace(",", "'").replace(".", ",").replace("'", ".") + \
                                    '<br>' + '-' + str(item.discount_percentage) + '%<br>' + cur_icon + " " + "{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", ".")
                    else:
                        rate = "{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", ".")
                    
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{qty}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{rate}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {amount}</td>
                        </tr>
                        
                    """.format(position=positions_nummer, \
                            item_name=item.item_name, \
                            qty="{:,.2f}".format(item.qty).replace(",", "'").replace(".", ",").replace("'", "."), \
                            cur_icon=cur_icon, \
                            rate=rate, \
                            amount="{:,.2f}".format(item.amount).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    positions_nummer += 1
                    table += tr
            else:
                # verpackung / versand
                verpackung_versand.append({
                    'name': item.item_name,
                    'amount': item.amount
                })
            
        for item in verpackung_versand:
            tr = """
                <tr class="blue-white">
                    <td colspan="4" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
                    <td style="text-align: right;">{cur_icon} {amount}</td>
                </tr>
                
            """.format(item_name=item['name'], \
                    cur_icon=cur_icon, \
                    amount="{:,.2f}".format(item['amount']).replace(",", "'").replace(".", ",").replace("'", "."))
            
            table += tr
        
        # Total Zeilen
        if doc.discount_amount:
            titel = 'Zwischensumme'
        else:
            titel = 'Summe netto'
        tr = """
            <tr class="blue-white">
                <td style="background-color: white !important" colspan ="3"></td>
                <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>{titel}</b></td>
                <td style="text-align: right;">{cur_icon} {amount}</td>
            </tr>
            
        """.format(titel=titel, \
                cur_icon=cur_icon, \
                amount="{:,.2f}".format(doc.total).replace(",", "'").replace(".", ",").replace("'", "."))
        
        table += tr
        
        if doc.discount_amount:
            if doc.additional_discount_percentage:
                additional_discount_percentage = "(-" + doc.get_formatted('additional_discount_percentage') + ") "
            else:
                additional_discount_percentage = ''
            
            discount_amount = "{:,.2f}".format(doc.discount_amount).replace(",", "'").replace(".", ",").replace("'", ".")
            net_total = "{:,.2f}".format(doc.net_total).replace(",", "'").replace(".", ",").replace("'", ".")
            
            tr = """
                <tr class="blue-white">
                    <td style="background-color: white !important" colspan ="3"></td>
                    <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Rabatt</b></td>
                    <td style="text-align: right;">{additional_discount_percentage}{cur_icon} -{discount_amount}</td>
                </tr>
                <tr class="blue-white">
                    <td style="background-color: white !important" colspan ="3"></td>
                    <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
                    <td style="text-align: right;">{cur_icon} {net_total}</td>
                </tr>
                
            """.format(additional_discount_percentage=additional_discount_percentage, \
                    cur_icon=cur_icon, \
                    discount_amount=discount_amount, \
                    net_total=net_total)
            
            table += tr
        
        total_taxes_and_charges = "{:,.2f}".format(doc.total_taxes_and_charges).replace(",", "'").replace(".", ",").replace("'", ".")
        grand_total = "{:,.2f}".format(doc.grand_total).replace(",", "'").replace(".", ",").replace("'", ".")
        tr = """
            <tr class="blue-white">
                <td style="background-color: white !important" colspan ="3"></td>
                <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. 19% MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
            </tr>
            <tr class="blue-white">
                <td style="background-color: white !important" colspan ="3"></td>
                <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe brutto</b></td>
                <td style="text-align: right;">{cur_icon} {grand_total}</td>
            </tr>
            
        """.format(total_taxes_and_charges=total_taxes_and_charges, \
                cur_icon=cur_icon, \
                grand_total=grand_total)
        
        table += tr
    # Teilrechnung
    elif doc.billing_type == 'Teilrechnung':
        if not doc.items[0].sales_order:
            return """
                <tr style="background-color: red !important;">
                    <td colspan = '5' style="font-size: 7.5pt;">Bitte befolgen Sie den korrekten Prozess zur Erstellung einer Schlussrechnung! (Erstellung Rechnung aus Auftragsbestätigung)</td>
                </tr>
            """
        else:
            sales_order = frappe.get_doc("Sales Order", doc.items[0].sales_order)
            for teilrechnung in sales_order.billing_overview:
                if teilrechnung.sales_invoice == doc.name:
                    total = "{:,.2f}".format(doc.total).replace(",", "'").replace(".", ",").replace("'", ".")
                    idx = teilrechnung.idx
                    project = sales_order.project
                    billing_portion = "{:,.1f}".format(teilrechnung.billing_portion).replace(",", "'").replace(".", ",").replace("'", ".")
                    net_total = "{:,.2f}".format(doc.net_total).replace(",", "'").replace(".", ",").replace("'", ".")
                    tax_rate = doc.taxes[0].rate
                    total_taxes_and_charges = "{:,.2f}".format(doc.total_taxes_and_charges).replace(",", "'").replace(".", ",").replace("'", ".")
                    grand_total = "{:,.2f}".format(doc.grand_total).replace(",", "'").replace(".", ",").replace("'", ".")
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>1</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">Abschlag</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">1</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {total}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {total}</td>
                        </tr>
                        <tr>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b></b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">
                            {idx}. Teilzahlung zu Projekt Nr. {project}<br>
                            {billing_portion} % der Auftragssumme</td>
                            <td colspan='3' style="border-right: 1px solid rgb(186, 210, 226) !important;">
                        </tr>
                        <!-- Total Zeilen -->
                        <tr class="blue-white">
                            <td style="background-color: white !important" colspan ="3"></td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
                            <td style="text-align: right;">{cur_icon} {net_total}</td>
                        </tr>
                        <tr class="blue-white">
                            <td style="background-color: white !important" colspan ="3"></td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. {tax_rate}% MwSt.</b></td>
                            <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
                        </tr>
                        <tr class="blue-white">
                            <td style="background-color: white !important" colspan ="3"></td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe brutto</b></td>
                            <td style="text-align: right;">{cur_icon} {grand_total}</td>
                        </tr>
                        
                    """.format(total=total, \
                                idx=idx, \
                                project=project, \
                                billing_portion=billing_portion, \
                                net_total=net_total, \
                                tax_rate=tax_rate, \
                                total_taxes_and_charges=total_taxes_and_charges, \
                                grand_total=grand_total, \
                                cur_icon=cur_icon)
                    
                    table += tr
        
    
    return table
