# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from energielenker.energielenker.timesheet_manager import get_employee_rate_external, get_employee_rate_internal
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils.data import get_datetime, today, add_days


class PowerProject():
    def __init__(self, project):
        self.project = project
        self.subprojects = []
        
        for row in project.subprojects:
            pp = PowerProject(frappe.get_doc("Project", row.subproject))
            pp.project.update_costing()
            pp.update_kpis()
            self.subprojects.append(pp.project)
        
        self.check_completion()

    def update_kpis(self):
        self.update_erpnext_kpis()
        self.update_custom_kpis()
        self.update_dates()
        
        self.project.estimated_costing = self.project.geschaetzte_kosten
        
        self.project.calculate_gross_margin()

    def update_custom_kpis(self):
        custom_kpis = [
            "open_quotation_amount", # wird behalten
            "expected_billable_amount",
            "open_billable_amount",
            "expected_purchase_cost",
            "zeit_geplant_in_aufgaben", # neu
            "zeit_gebucht_ueber_zeiterfassung", # neu
            "noch_zu_erwarten", # neu
            "voraussichtliche_abweichung", # neu
            "zeit_geplant_in_aufgaben_eur", # neu
            "zeit_gebucht_ueber_zeiterfassung_eur", # neu
            "noch_zu_erwarten_eur", # neu
            "voraussichtliche_abweichung_eur", # neu
            "erwartete_fremdkosten_aus_auftraegen_eur", # neu
            "summe_einkaufskosten_via_einkaufsrechnung", # neu
            'auftragsummen_gesamt', # neu
            # ~ "total_amount",
            'gesamtkosten_aktuell', # neu
            'ergebnis_aktuell', # neu
            'marge_aktuell_prozent', # neu
            'ausgangsrechnungen_summe', # neu
            'geschaetzte_kosten_klon', # neu
            'ergebnis_geplant', # neu
            'marge_geplant_prozent', # neu
            'noch_nicht_in_rechnung_gestellt_summe' # neu
        ]

        for kpi in custom_kpis:
            self.update_custom_kpi(kpi)

    def update_erpnext_kpis(self):
        erpnext_kpis = [
            "actual_time", # --> wurde ersetzt durch zeit_gebucht_ueber_zeiterfassung
            "total_costing_amount",
            "total_expense_claim",
            "total_purchase_cost",
            "total_sales_amount",
            "total_billable_amount",
            "total_billed_amount",
            "total_consumed_material_cost"
        ]

        for kpi in erpnext_kpis:
            self.update_erpnext_kpi(kpi)
    
    def update_dates(self):
        # Schritt 1: Lesen / Setzen des tiefsten Startdatum
        start_dates = []
        for subproject in self.subprojects:
            start_dates += get_lowest_project_start_date(subproject.name)
        
        start_dates += get_lowest_project_start_date(self.project.name)
        
        self.project.set('actual_start_date', min(start_dates))
        
        # Schritt 2: Lesen / Setzen des höchsten Enddatums
        end_dates = []
        for subproject in self.subprojects:
            end_dates += get_highest_project_end_date(subproject.name)
        
        end_dates += get_highest_project_end_date(self.project.name)
        
        if len(end_dates) > 0:
            self.project.set('actual_end_date', max(end_dates))
        else:
            self.project.set('actual_end_date', self.project.expected_end_date)

    def update_custom_kpi(self, kpi):
        value_project = getattr(self, "get_{kpi}".format(kpi=kpi))()
        self.update_kpi(kpi, value_project)

    def update_erpnext_kpi(self, kpi):
        value_project = self.project.get(kpi) or 0
        self.update_kpi(kpi, value_project)

    def update_kpi(self, kpi, value_project):
        value_subprojects = 0
        if len(self.subprojects) > 0:
            if kpi in ('ergebnis_aktuell'):
                value_project = self.project.auftragsummen_gesamt - self.project.gesamtkosten_aktuell
            elif kpi in ('marge_aktuell_prozent'):
                value_project = ((100 / self.project.auftragsummen_gesamt) * self.project.ergebnis_aktuell) if self.project.auftragsummen_gesamt > 0 else 0
            elif kpi in ('ergebnis_geplant'):
                value_project = self.project.auftragsummen_gesamt - self.project.geschaetzte_kosten_klon
            elif kpi in ('marge_geplant_prozent'):
                value_project = ((100 / self.project.auftragsummen_gesamt) * self.project.ergebnis_geplant) if self.project.auftragsummen_gesamt > 0 else 0
        
        if kpi not in ('auftragsummen_gesamt', 'ergebnis_aktuell', 'marge_aktuell_prozent', 'ergebnis_geplant', 'marge_geplant_prozent', 'noch_nicht_in_rechnung_gestellt_summe'):
            for subproject in self.subprojects:
                value_subprojects += subproject.get(kpi)
        
        total = value_project + value_subprojects
        
        if kpi == 'auftragsummen_gesamt':
            self.project.set('total_amount', total)
        
        self.project.set(kpi, total)

    def get_expected_purchase_cost(self):
        return frappe.get_all(
            "Purchase Order Item",
            filters={
                "project": self.project.name,
                "docstatus": ["=", "1"]
            },
            fields=["sum(base_net_amount) as sum"],
        )[0].sum or 0

    def get_open_quotation_amount(self):
        return frappe.get_all(
            "Quotation",
            filters={
                "project": self.project.name,
                "status": ["in", ["Open", "Replied"]]
            },
            fields=["sum(grand_total) as sum"],
        )[0].sum or 0

    def get_open_billable_amount(self):
        open_tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Completed", "Cancelled"]]
            },
            fields=["expected_time", "actual_time", "completed_by"],
        )
        
        open_billable_amount = 0

        for task in open_tasks:
            open_billable_amount += (
                float(max(task.expected_time - task.actual_time, 0)) * float(self.get_employee_rate(task.completed_by))
            )
        
        return open_billable_amount

    def get_expected_billable_amount(self):
        tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name
            },
            fields=["expected_time", "completed_by"]
        )
        
        expected_billable_amount = 0

        for task in tasks:
            expected_billable_amount += (
                float(task.expected_time) * float(self.get_employee_rate(task.completed_by))
            )
        
        return expected_billable_amount
    
    # ~ def get_total_amount(self):
        # ~ return self.project.auftragsummen_gesamt
    
# NEU -----------------------------------------------------------------------
    
    def get_noch_zu_erwarten(self):
        noch_zu_erwarten = 0
        open_tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Completed", "Cancelled"]]
            },
            fields=["expected_time", "actual_time"]
        )
        
        for task in open_tasks:
            noch_zu_erwarten += (
                max(task.expected_time - task.actual_time, 0)
            )
        
        return noch_zu_erwarten
    
    def get_voraussichtliche_abweichung(self):
        voraussichtliche_abweichung = 0
        open_tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Cancelled"]]
            },
            fields=["expected_time", "actual_time", "status"]
        )
        
        for task in open_tasks:
            if task.status == 'Completed':
                voraussichtliche_abweichung += task.expected_time - task.actual_time
            else:
                if task.actual_time > task.expected_time:
                    voraussichtliche_abweichung += task.expected_time - task.actual_time
        
        return voraussichtliche_abweichung - self.project.gebuchte_stunden_in_rhapsody
    
    def get_zeit_geplant_in_aufgaben(self):
        return frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Cancelled"]]
            },
            fields=["sum(expected_time) as sum"]
        )[0].sum or 0
    
    def get_zeit_gebucht_ueber_zeiterfassung(self):
        from_time_sheet = frappe.db.sql("""SELECT
            SUM(`hours`) as `time`
            FROM `tabTimesheet Detail` WHERE `project` = '{project}' AND `docstatus` = 1""".format(project=self.project.name), as_dict=True)[0]
        stunden = from_time_sheet.time or 0
        return stunden + self.project.gebuchte_stunden_in_rhapsody
    
    def get_zeit_geplant_in_aufgaben_eur(self):
        eur = 0
        tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Cancelled"]]
            },
            fields=["expected_time", "completed_by"]
        )
        
        for task in tasks:
            eur += (
                float(self.get_employee_rate(task.completed_by, internal=True)) * float(task.expected_time)
            )
        
        return eur
    
    def get_employee_rate(self, employee, internal=False):
        # fix permission issue
        #employee = frappe.get_value("Employee", {"user_id": employee}, "name")
        employee = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user_id}'""".format(user_id=employee), as_dict=True)
        if len(employee) > 0:
            employee = employee[0].name
        else:
            employee = False
            
        if internal:
            return (
                get_employee_rate_internal(employee) 
                if employee
                else self.project.default_external_rate
            )
        
        else:
            return (
                get_employee_rate_external(employee) 
                if employee
                else self.project.default_external_rate
            )
    
    def get_zeit_gebucht_ueber_zeiterfassung_eur(self):
        eur = 0
        emp_hours = frappe.db.sql("""SELECT
                                        `ts`.`employee` AS `employee`,
                                        SUM(`tsd`.`hours`) AS `hours`
                                    FROM `tabTimesheet Detail` AS `tsd`
                                    LEFT JOIN `tabTimesheet` AS `ts` ON `ts`.`name` = `tsd`.`parent`
                                    WHERE `tsd`.`project` = '{project}' AND `tsd`.`docstatus` = 1
                                    GROUP BY `ts`.`employee`""".format(project=self.project.name), as_dict=True)
        for emp_hour in emp_hours:
            eur += (
                get_employee_rate_internal(emp_hour.employee) * emp_hour.hours
            )
        
        # rhapsody std
        eur += (self.project.gebuchte_stunden_in_rhapsody * float(self.project.default_external_rate))
        
        return eur
    
    def get_noch_zu_erwarten_eur(self):
        eur = 0
        open_tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Completed", "Cancelled"]]
            },
            fields=["expected_time", "actual_time", "completed_by"]
        )
        
        for task in open_tasks:
            eur += (
                float(max(task.expected_time - task.actual_time, 0)) * float(self.get_employee_rate(task.completed_by, internal=True))
            )
        
        return eur
        
    def get_voraussichtliche_abweichung_eur(self):
        eur = self.get_voraussichtliche_abweichung() * float(self.project.default_external_rate)
        return eur
        
    def get_erwartete_fremdkosten_aus_auftraegen_eur(self):
        amount = 0.00
        items = frappe.db.sql("""SELECT `item_code`, `qty` FROM `tabSales Order Item`
                                    WHERE `parent` IN (
                                        SELECT `name` FROM `tabSales Order` WHERE `project` = '{project}' AND `docstatus` = 1
                                    )
                                    AND `item_group` != 'Produkt Verkauf energielenker Arbeitszeit'""".format(project=self.project.name), as_dict=True)
                                    
        for item in items:
            price = frappe.get_all("Item Price", fields=["price_list_rate"],
                filters={"price_list": 'Standard Einkauf', "item_code": item.item_code})
            if price:
                amount += (price[0].price_list_rate * item.qty)
        
        return amount
    
    def get_summe_einkaufskosten_via_einkaufsrechnung(self):
        '''
        Anforderungen energielenker:
        - alle Einkaufsrechnungspositionen OHNE LAGERARTIKEL (Lagerartikel werden über Lagerbuchung oder Lieferschein bewertet)
          --> summe_einkaufsrechnungspositionen
        - Lagerbuchungspositionen (alle Buchungen ohne Eingangslager = Entnahme)
          --> summe_lagerbuchungspositionen
        - Lieferscheinpositionen (NUR LAGERARTIKEL)
          -> summe_Lieferscheinpositionen
        '''
        
        summe_einkaufsrechnungspositionen = frappe.db.sql("""SELECT
                                                                SUM(`amount`) AS `amount`
                                                            FROM `tabPurchase Invoice Item`
                                                            WHERE `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabPurchase Invoice`
                                                                WHERE `project` = '{project}'
                                                                AND `docstatus` = 1
                                                            )
                                                            AND `item_code` NOT IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabItem`
                                                                WHERE `is_stock_item` = 1
                                                            )""".format(project=self.project.name), as_dict=True)[0].amount or 0
        
        summe_lagerbuchungspositionen = frappe.db.sql("""SELECT
                                                            SUM(`amount`) AS `amount`
                                                        FROM `tabStock Entry Detail`
                                                        WHERE `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabStock Entry`
                                                            WHERE `project` = '{project}'
                                                            AND `docstatus` = 1
                                                            AND `stock_entry_type` = 'Material Issue'
                                                        )""".format(project=self.project.name), as_dict=True)[0].amount or 0
        
        _summe_Lieferscheinpositionen = frappe.db.sql("""SELECT
                                                            `qty` AS `qty`,
                                                            `name` AS `voucher_detail_no`
                                                        FROM `tabDelivery Note Item`
                                                        WHERE `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabDelivery Note`
                                                            WHERE `project` = '{project}'
                                                            AND `docstatus` = 1
                                                        )
                                                        AND `item_code` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabItem`
                                                            WHERE `is_stock_item` = 1
                                                        )""".format(project=self.project.name), as_dict=True)
        summe_Lieferscheinpositionen = 0
        for value in _summe_Lieferscheinpositionen:
            valuation_rate = frappe.db.sql("""SELECT `valuation_rate` FROM `tabStock Ledger Entry` WHERE `voucher_detail_no` = '{0}'""".format(value.voucher_detail_no), as_dict=True)
            if len(valuation_rate) > 0:
                valuation_rate = valuation_rate[0].valuation_rate
            else:
                valuation_rate = 0
            summe_Lieferscheinpositionen += (value.qty * valuation_rate)
        
        return (summe_einkaufsrechnungspositionen + summe_lagerbuchungspositionen + summe_Lieferscheinpositionen) + (float(self.project.erfasste_externe_kosten_in_rhapsody) or 0)
    
    def get_auftragsummen_gesamt(self):
        return self.project.total_sales_amount - get_projektbewertung_ignorieren_amount(self)
        
    def get_gesamtkosten_aktuell(self):
        return self.get_zeit_gebucht_ueber_zeiterfassung_eur() + self.get_summe_einkaufskosten_via_einkaufsrechnung()
    
    def get_ergebnis_aktuell(self):
        return self.get_auftragsummen_gesamt() - self.get_gesamtkosten_aktuell()
    
    def get_marge_aktuell_prozent(self):
        auftragsummen_gesamt = self.get_auftragsummen_gesamt() or 0
        if auftragsummen_gesamt > 0:
            percent = (100 / auftragsummen_gesamt) * self.get_ergebnis_aktuell()
        else:
            return 0
        return percent
    
    def get_ausgangsrechnungen_summe(self):
        return self.project.total_billed_amount
    
    def get_geschaetzte_kosten_klon(self):
        return self.project.geschaetzte_kosten + self.get_zeit_geplant_in_aufgaben_eur()
    
    def get_ergebnis_geplant(self):
        return self.get_auftragsummen_gesamt() - self.get_geschaetzte_kosten_klon()
    
    def get_marge_geplant_prozent(self):
        auftragsummen_gesamt = self.get_auftragsummen_gesamt() or 0
        if auftragsummen_gesamt > 0:
            return (100 / auftragsummen_gesamt) * self.get_ergebnis_geplant()
        else:
            return 0
    
    def get_noch_nicht_in_rechnung_gestellt_summe(self):
        return self.get_auftragsummen_gesamt() - self.get_ausgangsrechnungen_summe()
    
    def check_completion(self):
        if self.project.percent_complete == 100:
            self.project.set('actual_end_date', today())
        
# /NEU -----------------------------------------------------------------------

def autoname(project, event):
    project.name = make_autoname(project.naming_series)

def onload(project, event):
    #if project.sales_order and not project.payment_schedule:
        #fetch_payment_schedule(project, project.sales_order)
    PowerProject(project).update_kpis()

def validate(project, event):
    validate_subprojects(project)
    PowerProject(project).update_kpis()
    mark_subprojects_as_subproject(project)
    
def mark_subprojects_as_subproject(project):
    for row in project.subprojects:
        subproject = frappe.get_doc("Project", row.subproject)
        if not subproject.subproject:
            subproject.subproject = 1
            subproject.save()

def validate_subprojects(project):
    for row in project.subprojects:
        if project.name == row.subproject:
            frappe.throw(_("Project cannot be a subproject of itself."))

        parent_project = frappe.get_value(
            "Subproject",
            {"subproject": row.subproject},
            "parent"
        )

        if parent_project and parent_project != project.name:
            frappe.throw(_("Subproject {} is already part of project {}.")
                .format(row.subproject, parent_project))

        if subproject_is_a_parent_of_project(row.subproject, project.name):
            frappe.throw(_("Subproject {} is actually a parent of project {}.")
                .format(row.subproject, project.name))

def subproject_is_a_parent_of_project(subproject, project):
    subprojects_of_subproject = get_subprojects(subproject)

    if not subprojects_of_subproject:
        return False

    if project in subprojects_of_subproject:
        return True

    for subproject in subprojects_of_subproject:
        if subproject_is_a_parent_of_project(subproject, project):
            return True

    return False

def get_subprojects(project):
    subprojects = frappe.get_all(
        "Subproject",
        filters={
            "parent": project,
        },
        fields=["subproject"],
        as_list=True
    )

    return [subproject[0] for subproject in subprojects]

@frappe.whitelist()
def get_contact_details(doc):
    from frappe.contacts.doctype.address.address import get_condensed_address

    contact = frappe.get_doc("Contact", doc).as_dict()

    contact["email_ids"] = frappe.get_list("Contact Email", filters={
            "parenttype": "Contact",
            "parent": contact.name,
            "is_primary": 0
        }, fields=["email_id"])

    contact["phone_nos"] = frappe.get_list("Contact Phone", filters={
            "parenttype": "Contact",
            "parent": contact.name,
            "is_primary_phone": 0,
            "is_primary_mobile_no": 0
        }, fields=["phone"])

    if contact.address:
        address = frappe.get_doc("Address", contact.address)
        contact["address"] = get_condensed_address(address)

    return {"contact_list": [contact]}

@frappe.whitelist()
def clear_payment_schedule(project, sales_order):
    frappe.db.sql("""DELETE FROM `tabPayment Forecast` WHERE `parent` = '{project}' AND `order` = '{sales_order}'""".format(project=project, sales_order=sales_order), as_list=True)
    return
    
@frappe.whitelist()
def make_sales_invoice(order, percent, amount, percent_billed, invoice_date, invoice_type):
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    if invoice_type == 'Teilrechnung':
        si = make_sales_invoice(order, ignore_permissions=True)
        order = frappe.get_doc("Sales Order", order)
        si.billing_type = 'Teilrechnung'
        si.set_posting_time = 1
        si.posting_date = invoice_date
        si.apply_discount_on = 'Net Total'
        si = si.insert(ignore_permissions=True)
        si.payment_schedule = []
        si.payment_terms_template = '100% 14 Tage' if order.navision_interal_ic == 1 else '100% 21 Tage'
        si.due_date = add_days(si.posting_date, 14) if si.payment_terms_template == '100% 14 Tage' else add_days(si.posting_date, 21)

        for item in si.items:
            item.qty = (item.qty / (100 - float(percent_billed))) * float(percent)

        si.save(ignore_permissions=True)
        
        invoice_row = order.append('billing_overview', {})
        invoice_row.creation_date = today()
        invoice_row.billing_portion = percent
        invoice_row.amount = amount
        invoice_row.due_date = invoice_date
        invoice_row.sales_invoice = si.name
        order.save(ignore_permissions=True)
        
        return si.name

@frappe.whitelist()
def get_order_payment_forecast_details(order, amount):
    order = frappe.get_doc("Sales Order", order)
    data = {
        'percent_to_bill': 0,
        'percent_already_billed': order.per_billed,
        'grand_total': order.grand_total
    }
    
    if order.per_billed < 100:
        for entry in order.payment_schedule:
            if float(entry.payment_amount) == float(amount):
                data['percent_to_bill'] = entry.invoice_portion
    
    return data

@frappe.whitelist()
def make_final_sales_invoice(order, invoice_date):
    sales_order = frappe.get_doc("Sales Order", order)
    
    # ammend all existing payments of pre invoices from sales order and link it from sinv to sales order
    for entry in sales_order.billing_overview:
        pre_invoice = entry.sales_invoice
        payment_entries = frappe.get_all('Payment Entry Reference', filters={'reference_name': pre_invoice, 'reference_doctype': 'Sales Invoice'}, fields=['parent'])
        for _payment_entry in payment_entries:
            # cancel old payment entry
            payment_entry = frappe.get_doc("Payment Entry", _payment_entry.parent)
            payment_entry.cancel()
            frappe.db.commit()
    
    # make return to all pre invoices
    for entry in sales_order.billing_overview:
        # create return invoice
        from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return
        pre_invoice_return = make_sales_return(entry.sales_invoice)
        pre_invoice_return.update_billed_amount_in_sales_order = 1
        pre_invoice_return.save(ignore_permissions=True)
        pre_invoice_return.submit()
        frappe.db.commit()
    
    for entry in sales_order.billing_overview:
        pre_invoice = entry.sales_invoice
        payment_entries = frappe.get_all('Payment Entry Reference', filters={'reference_name': pre_invoice, 'reference_doctype': 'Sales Invoice'}, fields=['parent'])
        for _payment_entry in payment_entries:
            # copy old payment erntry
            new_payment_entry = frappe.copy_doc(payment_entry)
            new_payment_entry.references = []
            new_payment_entry.save(ignore_permissions=True)
            
            # link new payment entry with sales order
            row = new_payment_entry.append('references', {})
            row.reference_doctype = "Sales Order"
            row.reference_name = sales_order.name
            row.allocated_amount = new_payment_entry.paid_amount
            
            new_payment_entry.save(ignore_permissions=True)
            new_payment_entry.submit()
            frappe.db.commit()
    
    # create final invoice
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    si = make_sales_invoice(order, ignore_permissions=True)
    si.billing_type = 'Schlussrechnung'
    si.navision_konto = sales_order.navision_konto
    si.navision_kontonummer = sales_order.navision_kontonummer
    si.allocate_advances_automatically = 1
    si.set_posting_time = 1
    si.posting_date = invoice_date
    si.apply_discount_on = 'Net Total'
    for item in si.items:
        item.qty = frappe.db.sql("""SELECT `qty` FROM `tabSales Order Item` WHERE `name` = '{so_detail}'""".format(so_detail=item.so_detail), as_dict=True)[0].qty
    si = si.insert(ignore_permissions=True)
    si.payment_schedule = []
    si.payment_terms_template = ''
    si.save(ignore_permissions=True)
    
    # update sales order
    order = frappe.get_doc("Sales Order", order)
    invoice_row = order.append('billing_overview', {})
    invoice_row.creation_date = today()
    invoice_row.billing_portion = 100
    invoice_row.amount = si.grand_total
    invoice_row.due_date = invoice_date
    invoice_row.sales_invoice = si.name
    order.save(ignore_permissions=True)
    
    return {
        'invoice': si.name,
        'amount': si.outstanding_amount
    }

@frappe.whitelist()
def auto_kpi_refresh():
    projects = frappe.db.sql("""SELECT `name` FROM `tabProject`""", as_dict=True)
    errors = []
    for _project in projects:
        try:
            project = frappe.get_doc("Project", _project.name)
            PowerProject(project).update_kpis()
            project.save()
        except:
            errors.append(_project.name)
    if len(errors) > 0:
        frappe.log_error("{0}".format(str(errors)), 'auto_kpi_refresh')

def get_projektbewertung_ignorieren_amount(self):
    return float(frappe.db.sql("""SELECT IFNULL(SUM(`base_net_total`), 0) AS `qty` FROM `tabSales Order` WHERE `project` = '{0}' AND `docstatus` = 1 AND `projektbewertung_ignorieren` = 1""".format(self.project.name), as_dict=True)[0].qty)

def get_lowest_project_start_date(project):
    # act_start_date von Task
    start_date = frappe.db.sql("""SELECT 
                                    MIN(`act_start_date`) AS `lowest_start_date`
                                FROM `tabTask`
                                WHERE `project` = '{project}'""".format(project=project), as_dict=True)
    if start_date[0].lowest_start_date:
        return [start_date[0].lowest_start_date]
    else:
        # Fallback 1: exp_start_date von Task
        start_date = frappe.db.sql("""SELECT 
                                        MIN(`exp_start_date`) AS `lowest_start_date`
                                    FROM `tabTask`
                                    WHERE `project` = '{project}'""".format(project=project), as_dict=True)
        if start_date[0].lowest_start_date:
            return [start_date[0].lowest_start_date]
        else:
            # Fallback 2: creation von Task
            start_date = frappe.db.sql("""SELECT 
                                            MIN(`creation`) AS `lowest_start_date`
                                        FROM `tabTask`
                                        WHERE `project` = '{project}'""".format(project=project), as_dict=True)
            if start_date[0].lowest_start_date:
                return [start_date[0].lowest_start_date.date()]
            else:
                # Fallback 3: tiefstes creation Datum von Projekt und dazugehörigen Tasks
                start_date = frappe.db.sql("""SELECT 
                                                MIN(`date`) AS `lowest_start_date`
                                            FROM (
                                            SELECT 
                                                `creation` AS `date`
                                            FROM `tabTask`
                                            WHERE `project` = '{project}'
                                            UNION
                                            SELECT 
                                                `creation` AS `date`
                                            FROM `tabProject`
                                            WHERE `name` = '{project}'
                                            ) AS `tbl`""".format(project=project), as_dict=True)
                if start_date[0].lowest_start_date:
                    return [start_date[0].lowest_start_date.date()]
                else:
                    # Last Fallback
                    return ['1900-01-01']

def get_highest_project_end_date(project):
    # act_end_date von abgeschlossenem Task
    end_date = frappe.db.sql("""SELECT 
                                    MAX(`act_end_date`) AS `highest_end_date`
                                FROM `tabTask`
                                WHERE `project` = '{project}'
                                AND `status` = 'Completed'""".format(project=project), as_dict=True)
    if end_date[0].highest_end_date:
        return [end_date[0].highest_end_date]
    else:
        # Fallback 1: exp_end_date von abgeschlossenem Task
        end_date = frappe.db.sql("""SELECT 
                                        MAX(`exp_end_date`) AS `highest_end_date`
                                    FROM `tabTask`
                                    WHERE `project` = '{project}'
                                    AND `status` = 'Completed'""".format(project=project), as_dict=True)
        if end_date[0].highest_end_date:
            return [end_date[0].highest_end_date]
        else:
            return []
