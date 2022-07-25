# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def get_print_items(dt, dn):
    doc = frappe.get_doc(dt, dn)
    verpackung_versand = []
    summe_interne_positionen = 0
    table = ''
    positions_nummer = 1
    cur_icon = '&euro;' if doc.currency == 'EUR' else doc.currency
    if doc.shipping_address_name:
        country = frappe.db.get_value('Address', doc.shipping_address_name, 'country')
    else:
        country = frappe.db.get_value('Address', doc.customer_address, 'country')
    if country.lower() not in ('germany', 'deutschland'):
        ztn = True
    else:
        ztn = False
    
    # Gutschrift
    # --------------------------------------------------------------------------------------------------------------------------------------------
    if int(doc.is_return) == 1:
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
                            qty="{:,.2f}".format(item.qty*-1).replace(",", "'").replace(".", ",").replace("'", "."), \
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
                    positions_nummer += 1
                    table += tr
                
                elif int(item.interne_position) == 1:
                    summe_interne_positionen += item.amount
                
                elif int(item.kalkulationssumme_interner_positionen) == 1:
                    summe_interne_positionen += item.amount
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                            qty="{:,.2f}".format(item.qty*-1).replace(",", "'").replace(".", ",").replace("'", "."), \
                            cur_icon=cur_icon, \
                            rate="{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", "."), \
                            amount="{:,.2f}".format(item.amount*-1).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
                    positions_nummer += 1
                    table += tr
                
                else:
                    if item.discount_percentage:
                        if item.rate_with_margin:
                            rate = cur_icon + " " + "{:,.2f}".format(item.rate_with_margin).replace(",", "'").replace(".", ",").replace("'", ".") + \
                                    '<br>' + '-' + str(item.discount_percentage) + '%<br>' + cur_icon + " " + "{:,.2f}".format(item.rate*-1).replace(",", "'").replace(".", ",").replace("'", ".")
                        else:
                            rate = cur_icon + " " + "{:,.2f}".format(item.price_list_rate).replace(",", "'").replace(".", ",").replace("'", ".") + \
                                    '<br>' + '-' + str(item.discount_percentage) + '%<br>' + cur_icon + " " + "{:,.2f}".format(item.rate*-1).replace(",", "'").replace(".", ",").replace("'", ".")
                    else:
                        rate = "{:,.2f}".format(item.rate).replace(",", "'").replace(".", ",").replace("'", ".")
                    
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{qty}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {amount}</td>
                        </tr>
                        
                    """.format(position=positions_nummer, \
                            item_name=item.item_name, \
                            qty="{:,.2f}".format(item.qty*-1).replace(",", "'").replace(".", ",").replace("'", "."), \
                            cur_icon=cur_icon, \
                            rate=rate, \
                            amount="{:,.2f}".format(item.amount*-1).replace(",", "'").replace(".", ",").replace("'", "."))
                    
                    for line in item.description.split("</div>"):
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">{line}</td>
                                <td></td>
                            </tr>
                        """.format(line=line + '</div>')
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                    amount="{:,.2f}".format(item['amount']*-1).replace(",", "'").replace(".", ",").replace("'", "."))
            
            table += tr
        
        # Total Zeilen
        if doc.discount_amount:
            titel = 'Zwischensumme'
        else:
            titel = 'Summe netto'
        tr = """
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>{titel}</b></td>
                <td style="text-align: right;">{cur_icon} {amount}</td>
            </tr>
            
        """.format(titel=titel, \
                cur_icon=cur_icon, \
                amount="{:,.2f}".format(doc.total*-1).replace(",", "'").replace(".", ",").replace("'", "."))
        
        table += tr
        
        if doc.discount_amount:
            if doc.additional_discount_percentage:
                additional_discount_percentage = "(-" + doc.get_formatted('additional_discount_percentage') + ") "
            else:
                additional_discount_percentage = ''
            
            discount_amount = "{:,.2f}".format(doc.discount_amount*-1).replace(",", "'").replace(".", ",").replace("'", ".")
            net_total = "{:,.2f}".format(doc.net_total*-1).replace(",", "'").replace(".", ",").replace("'", ".")
            
            tr = """
                <tr class="blue-white">
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Rabatt</b></td>
                    <td style="text-align: right;">{additional_discount_percentage}{cur_icon} -{discount_amount}</td>
                </tr>
                <tr class="blue-white">
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
                    <td style="text-align: right;">{cur_icon} {net_total}</td>
                </tr>
                
            """.format(additional_discount_percentage=additional_discount_percentage, \
                    cur_icon=cur_icon, \
                    discount_amount=discount_amount, \
                    net_total=net_total)
            
            table += tr
        
        total_taxes_and_charges = "{:,.2f}".format(doc.total_taxes_and_charges*-1).replace(",", "'").replace(".", ",").replace("'", ".")
        grand_total = "{:,.2f}".format(doc.grand_total*-1).replace(",", "'").replace(".", ",").replace("'", ".")
        tr = """
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. 19% MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
            </tr>
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe brutto</b></td>
                <td style="text-align: right;">{cur_icon} {grand_total}</td>
            </tr>
            
        """.format(total_taxes_and_charges=total_taxes_and_charges, \
                cur_icon=cur_icon, \
                grand_total=grand_total)
        
        table += tr
    
    # Normale Rechnung
    # --------------------------------------------------------------------------------------------------------------------------------------------
    elif doc.billing_type == 'Rechnung':
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
                    positions_nummer += 1
                    table += tr
                
                elif int(item.interne_position) == 1:
                    summe_interne_positionen += item.amount
                
                elif int(item.kalkulationssumme_interner_positionen) == 1:
                    summe_interne_positionen += item.amount
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
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
                    
                    lieferscheine = get_lieferschein(doc.lieferschein_referenzen_ausblenden, item)
                    if lieferscheine:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Lieferscheine: {lieferscheine}</td>
                                <td></td>
                            </tr>
                        """.format(lieferscheine=lieferscheine)
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    elif lieferscheine:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>{titel}</b></td>
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
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Rabatt</b></td>
                    <td style="text-align: right;">{additional_discount_percentage}{cur_icon} -{discount_amount}</td>
                </tr>
                <tr class="blue-white">
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
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
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. 19% MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
            </tr>
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe brutto</b></td>
                <td style="text-align: right;">{cur_icon} {grand_total}</td>
            </tr>
            
        """.format(total_taxes_and_charges=total_taxes_and_charges, \
                cur_icon=cur_icon, \
                grand_total=grand_total)
        
        table += tr
    
    # Teilrechnung
    # --------------------------------------------------------------------------------------------------------------------------------------------
    elif doc.billing_type == 'Teilrechnung':
        if not doc.items[0].sales_order:
            return """
                <tr style="background-color: red !important;">
                    <td colspan = '5' style="font-size: 7.5pt;">Bitte befolgen Sie den korrekten Prozess zur Erstellung einer Teilrechnung! (Erstellung Rechnung aus Auftragsbestätigung)</td>
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
                            <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                            <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
                            <td style="text-align: right;">{cur_icon} {net_total}</td>
                        </tr>
                        <tr class="blue-white">
                            <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                            <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. {tax_rate}% MwSt.</b></td>
                            <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
                        </tr>
                        <tr class="blue-white">
                            <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                            <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe brutto</b></td>
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
    
    # Schlussrechnung
    # --------------------------------------------------------------------------------------------------------------------------------------------
    elif doc.billing_type == 'Schlussrechnung':
        if not doc.items[0].sales_order:
            return """
                <tr style="background-color: red !important;">
                    <td colspan = '5' style="font-size: 7.5pt;">Bitte befolgen Sie den korrekten Prozess zur Erstellung einer Schlussrechnung! (Erstellung Rechnung aus Auftragsbestätigung)</td>
                </tr>
            """
        sales_order = frappe.get_doc("Sales Order", doc.items[0].sales_order)
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
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    else:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
                    positions_nummer += 1
                    table += tr
                
                elif int(item.interne_position) == 1:
                    summe_interne_positionen += item.amount
                
                elif int(item.kalkulationssumme_interner_positionen) == 1:
                    summe_interne_positionen += item.amount
                    tr = """
                        <tr style="background-color: rgb(186, 210, 226) !important;">
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important; text-align: center;"><b>{position}</b></td>
                            <td style="border-right: 1px solid rgb(186, 210, 226) !important;">{item_name}</td>
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
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    else:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    else:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
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
                            <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;">{cur_icon} {rate}</td>
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
                    
                    if item.serial_no:
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                <td></td>
                            </tr>
                        """.format(serial_no=item.serial_no.replace("\n", "<br>"))
                    else:
                        serial_no = get_seriennummer(item)
                        if serial_no:
                            tr += """
                                <tr style="background-color: transparent !important;">
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                    <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Serien-Nummer:<br>{serial_no}</td>
                                    <td></td>
                                </tr>
                            """.format(serial_no=serial_no)
                    
                    if ztn:
                        zolltarifnummer = frappe.db.get_value('Item', item.item_code, 'customs_tariff_number')
                        tr += """
                            <tr style="background-color: transparent !important;">
                                <td style="border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                                <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;font-size: 8pt;">Zolltarifnummer: {zolltarifnummer}</td>
                                <td></td>
                            </tr>
                        """.format(zolltarifnummer=zolltarifnummer)
                    
                    positions_nummer += 1
                    table += tr
            else:
                # verpackung / versand
                verpackung_versand.append({
                    'name': item.item_name,
                    'amount': item.amount
                })
        
        # Abschlagspositionen
        total_anzahlung = 0
        total_anzahlung_mwst = 0
        if len(sales_order.billing_overview) > 0:
            tr = """
                <tr style="background-color: rgb(186, 210, 226) !important;">
                    <td style="text-align: center;"><b>{position}</b></td>
                    <td colspan = '4' style="font-size: 7.5pt;">Folgende Abschlagsrechnungen wurden Ihnen bereits zugesandt.<br>Zahlungseingänge sind aufgeführt soweit bereits gebucht.</td>
                </tr>
            """.format(position=positions_nummer)
            table += tr
        
        for teilrechnung in sales_order.billing_overview:
            if teilrechnung.sales_invoice != doc.name:
                tr_sales_invoice = frappe.get_doc("Sales Invoice", teilrechnung.sales_invoice)
                if teilrechnung.invoice_rhapsody:
                    tr_print_name = "RG-Nr. Rhapsody" + teilrechnung.invoice_rhapsody
                else:
                    tr_print_name = "Rechnung-Nr." + tr_sales_invoice.name
                tr_sales_invoice_posting_date = tr_sales_invoice.get_formatted('posting_date')
                tr_sales_invoice_total = "{:,.2f}".format(tr_sales_invoice.total).replace(",", "'").replace(".", ",").replace("'", ".")
                tr_sales_invoice_total_taxes_and_charges = "{:,.2f}".format(tr_sales_invoice.total_taxes_and_charges).replace(",", "'").replace(".", ",").replace("'", ".")
                tr_sales_invoice_grand_total = "{:,.2f}".format(tr_sales_invoice.grand_total).replace(",", "'").replace(".", ",").replace("'", ".")
                tr_sales_invoice_taxes_rate = "{:,.0f}".format(tr_sales_invoice.taxes[0].rate)
                if tr_sales_invoice.status == 'Paid':
                    tr_sales_invoice_paid_amount = cur_icon + "{:,.2f}".format(tr_sales_invoice.grand_total - tr_sales_invoice.outstanding_amount).replace(",", "'").replace(".", ",").replace("'", ".")
                else:
                    tr_sales_invoice_paid_amount = "-"
                
                tr = """
                    <tr>
                        <td style="text-align: center; border-right: 1px solid rgb(186, 210, 226) !important;"><i>{position}.{teilrechnung_idx}</i></td>
                        <td><i>Abschlag ({tr_sales_invoice_taxes_rate} % MwSt.)</i></td>
                        <td style="text-align: right;"><i></i></td>
                        <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><i></i></td>
                        <td style="text-align: right; "><i></i></td>
                    </tr>
                    <tr style="font-size: 7.5pt;">
                        <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                        <td colspan="3" style="border-right: 1px solid rgb(186, 210, 226) !important;">Abschlag {teilrechnung_idx}: {tr_print_name} vom {tr_sales_invoice_posting_date}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"></td>
                        <td colspan="3" style=" padding: 0px !important;">
                            <table style="width: 100%; font-size: 7.5pt;">
                                <tr>
                                    <td style="width: 30%;">
                                        - Nettobetrag:<br>
                                        - Mehrwertsteuer:<br>
                                        - Bruttobetrag:<br>
                                        - Zahlungseingang:
                                    </td>
                                    <td style="text-align: right;">
                                        {cur_icon} {tr_sales_invoice_total}<br>
                                        {cur_icon} {tr_sales_invoice_total_taxes_and_charges}<br>
                                        {cur_icon} {tr_sales_invoice_grand_total}<br>
                                        {tr_sales_invoice_paid_amount}
                                    </td>
                                    <td style="border-right: 1px solid rgb(186, 210, 226) !important; width: 50%;">&nbsp;</td>
                                </tr>
                            </table>
                        </td>
                        <td></td>
                    </tr>
                    
                """.format(position=positions_nummer, \
                        teilrechnung_idx=teilrechnung.idx, \
                        tr_sales_invoice_taxes_rate=tr_sales_invoice_taxes_rate, \
                        tr_print_name=tr_print_name, \
                        tr_sales_invoice_posting_date=tr_sales_invoice_posting_date, \
                        cur_icon=cur_icon, \
                        tr_sales_invoice_total=tr_sales_invoice_total, \
                        tr_sales_invoice_total_taxes_and_charges=tr_sales_invoice_total_taxes_and_charges, \
                        tr_sales_invoice_grand_total=tr_sales_invoice_grand_total, \
                        tr_sales_invoice_paid_amount=tr_sales_invoice_paid_amount)
                
                total_anzahlung += tr_sales_invoice.total
                total_anzahlung_mwst += tr_sales_invoice.total_taxes_and_charges
                table += tr
            
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
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>{titel}</b></td>
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
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Rabatt</b></td>
                    <td style="text-align: right;">{additional_discount_percentage}{cur_icon} -{discount_amount}</td>
                </tr>
                <tr class="blue-white">
                    <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                    <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe netto</b></td>
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
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>zzgl. 19% MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} {total_taxes_and_charges}</td>
            </tr>
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe inkl. MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} {grand_total}</td>
            </tr>
            
        """.format(total_taxes_and_charges=total_taxes_and_charges, \
                cur_icon=cur_icon, \
                grand_total=grand_total)
        
        table += tr
        
        total_brutto = "{:,.2f}".format(doc.grand_total - total_anzahlung - total_anzahlung_mwst).replace(",", "'").replace(".", ",").replace("'", ".")
        total_anzahlung = "{:,.2f}".format(total_anzahlung).replace(",", "'").replace(".", ",").replace("'", ".")
        total_anzahlung_mwst = "{:,.2f}".format(total_anzahlung_mwst).replace(",", "'").replace(".", ",").replace("'", ".")
        
        tr = """
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>abzg. bereits gezahlte Abschläge netto</b></td>
                <td style="text-align: right;">{cur_icon} -{total_anzahlung}</td>
            </tr>
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>abzgl. bereits gezahlte Abschläge 19 % MwSt.</b></td>
                <td style="text-align: right;">{cur_icon} -{total_anzahlung_mwst}</td>
            </tr>
            <tr class="blue-white">
                <td colspan="2" style="width: 50% ; background-color: white !important;"></td>
                <td colspan="2" style="text-align: right; border-right: 1px solid rgb(186, 210, 226) !important;"><b>Summe Brutto</b></td>
                <td style="text-align: right;">{cur_icon} {total_brutto}</td>
            </tr>
            
        """.format(cur_icon=cur_icon, \
                    total_anzahlung=total_anzahlung, \
                    total_anzahlung_mwst=total_anzahlung_mwst, \
                    total_brutto=total_brutto)
        
        table += tr
    
    return table

def get_lieferschein(disable=False, item=None, no_join=False):
    if not item:
        return None
    if disable:
        if int(disable) == 0:
            disable = False
    if not disable:
        if item.delivery_note:
            if not no_join:
                return item.delivery_note
            else:
                return "('" + item.delivery_note + "')"
        elif item.so_detail:
            lieferscheine = frappe.db.sql("""SELECT `parent` FROM `tabDelivery Note Item` WHERE `docstatus` = 1 AND `so_detail` = '{so_detail}'""".format(so_detail=item.so_detail), as_dict=True)
            if len(lieferscheine) > 0:
                ls = []
                for lieferschein in lieferscheine:
                    ls.append(lieferschein.parent)
                
                if not no_join:
                    lieferscheine = ", ".join(ls)
                    return lieferscheine
                else:
                    if len(ls) > 1:
                        return tuple(ls)
                    else:
                        return "('{0}')".format(ls[0])
            
            else:
                return None
        else:
            return None
    else:
        return None

def get_seriennummer(item):
    lieferscheine = get_lieferschein(item=item, no_join=True)
    if lieferscheine:
        seriennummern = frappe.db.sql("""SELECT DISTINCT `serial_no` FROM `tabDelivery Note Item` WHERE `docstatus` = 1 AND `parent` IN {lieferscheine} AND `item_code` = '{item}' AND `serial_no` IS NOT NULL""".format(lieferscheine=lieferscheine, item=item.item_code), as_dict=True)
        if len(seriennummern) > 0:
            sns = []
            for sn in seriennummern:
                sns.append(str(sn.serial_no).replace("\n", "<br>"))
            return "<br>".join(sns)
        else:
            return False
    else:
        return False


