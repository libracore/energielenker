# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from energielenker.energielenker.timesheet_manager import get_employee_rate_external, get_employee_rate_internal
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils.data import get_datetime, today, add_days
from frappe.utils import cint
from datetime import datetime


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
        #Update Sales Order Status in Payment Forecast
        self.update_so_status()

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
        ts_dates = []
        for subproject in self.subprojects:
            sub_p_ts_entries = frappe.db.sql("""SELECT
                                            `from_time`,
                                            `to_time`
                                        FROM `tabTimesheet Detail`
                                        WHERE `project` = '{0}'""".format(subproject.name), as_dict=True)
            for ts_entry in sub_p_ts_entries:
                ts_dates.append(ts_entry.from_time.strftime("%Y-%m-%d"))
                ts_dates.append(ts_entry.to_time.strftime("%Y-%m-%d"))
        
        p_ts_entries = frappe.db.sql("""SELECT
                                        `from_time`,
                                        `to_time`
                                    FROM `tabTimesheet Detail`
                                    WHERE `project` = '{0}'""".format(self.project.name), as_dict=True)
        for ts_entry in p_ts_entries:
            ts_dates.append(ts_entry.from_time.strftime("%Y-%m-%d"))
            ts_dates.append(ts_entry.to_time.strftime("%Y-%m-%d"))
        
        if len(ts_dates) > 0:
            self.project.set('actual_start_date', datetime.strptime(min(ts_dates), "%Y-%m-%d").strftime("%d.%m.%Y"))
            self.project.set('actual_end_date', max(ts_dates))
        else:
            self.project.set('actual_start_date', None)
            self.project.set('actual_end_date', None)

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
        
        self.get_total_amount_without_zusatzgeschaft()
        
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
   
   # nur die Aufträge netto aufsummiert, welche nicht (!) den Haken "Zusatzgeschäft" im Kundenauftrag tragen.
    def get_total_amount_without_zusatzgeschaft(self):
        auftragswert_hauptauftrage = frappe.db.sql("""select sum(base_net_total)
            from `tabSales Order` where project = %s and docstatus=1 and zusatzgeschaft = 0""", self.project.name)

        self.project.auftragswert_hauptauftrage = auftragswert_hauptauftrage and auftragswert_hauptauftrage[0][0] or 0
    
# NEU -----------------------------------------------------------------------
    
    def get_noch_zu_erwarten(self):
        noch_zu_erwarten = 0
        open_tasks = frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Completed", "Cancelled"]]
            },
            fields=["expected_time", "forecast_additional_hours", "actual_time"]
        )
        
        for task in open_tasks:
            noch_zu_erwarten += (
                max(task.expected_time + task.forecast_additional_hours - task.actual_time, 0)
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
            fields=["expected_time", "forecast_additional_hours", "actual_time", "status"]
        )
        
        for task in open_tasks:
            if task.status == 'Completed':
                voraussichtliche_abweichung += task.expected_time + task.forecast_additional_hours - task.actual_time
            else:
                if task.actual_time > task.expected_time + task.forecast_additional_hours:
                    voraussichtliche_abweichung += task.expected_time + task.forecast_additional_hours - task.actual_time
        
        return voraussichtliche_abweichung - self.project.gebuchte_stunden_in_rhapsody
    
    def get_zeit_geplant_in_aufgaben(self):
        return frappe.get_all(
            "Task",
            filters={
                "project": self.project.name,
                "status": ["not in", ["Cancelled"]]
            },
            fields=["sum(expected_time) + sum(forecast_additional_hours) as sum"]
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
            fields=["expected_time", "forecast_additional_hours", "completed_by"]
        )
        
        for task in tasks:
            eur += (
                float(self.get_employee_rate(task.completed_by, internal=True)) * float(task.expected_time + task.forecast_additional_hours)
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
            fields=["expected_time", "forecast_additional_hours", "actual_time", "completed_by"]
        )
        
        for task in open_tasks:
            eur += (
                float(max(task.expected_time + task.forecast_additional_hours - task.actual_time, 0)) * float(self.get_employee_rate(task.completed_by, internal=True))
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
                                    
        part_list_items = frappe.db.sql("""SELECT `item_code`, `qty` FROM `tabSales Order Part List Item`
                                    WHERE `parent` IN (
                                        SELECT `name` FROM `tabSales Order` WHERE `project` = '{project}' AND `docstatus` = 1
                                    )""".format(project=self.project.name), as_dict=True)
                                    
        for item in items:
            price = frappe.get_all("Item Price", fields=["price_list_rate"],
                filters={"price_list": 'Standard Einkauf', "item_code": item.item_code})
            if price:
                amount += (price[0].price_list_rate * item.qty)
        
        if len(part_list_items) > 0:
            for part_list_item in part_list_items:
                price = frappe.get_all("Item Price", fields=["price_list_rate"],
                    filters={"price_list": 'Standard Einkauf', "item_code": part_list_item.item_code})
                if price:
                    amount += (price[0].price_list_rate * part_list_item.qty)
        
        return amount
    
    def get_summe_einkaufskosten_via_einkaufsrechnung(self):
        '''
        Anforderungen energielenker:
        - alle Einkaufsrechnungspositionen OHNE LAGERARTIKEL (Lagerartikel werden über Lagerbuchung, Lieferschein oder summe_direktlieferungen bewertet)
          --> summe_einkaufsrechnungspositionen
        - Lagerbuchungspositionen (alle Buchungen ohne Eingangslager = Entnahme)
          --> summe_lagerbuchungspositionen
        - Lieferscheinpositionen (NUR LAGERARTIKEL)
          -> summe_Lieferscheinpositionen
        Ergänzung 10.03.2025 (Herr Ruhkamp)
        - alle Einkaufsrechnungspositionen MIT LAGERARTIKEL welcher über eine Direktlieferung(drop-ship) ausgeliefert werden
          --> summe_direktlieferungen
        Ergänzung 26.03.2025 (Herr Ruhkamp)
        - alle Expense Claims mit Projektbezug (Andere Ausgaben)
          --> summe_ausgaben
        '''
        
        if not self.project.einkaufskosten_manuell_festsetzen == 1:
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
            
            summe_direktlieferungen = frappe.db.sql("""SELECT
                                                                    SUM(`amount`) AS `amount`
                                                                FROM `tabPurchase Invoice Item`
                                                                WHERE `parent` IN (
                                                                    SELECT
                                                                        `name`
                                                                    FROM `tabPurchase Invoice`
                                                                    WHERE `project` = '{project}'
                                                                    AND `update_stock` = 0
                                                                    AND `docstatus` = 1
                                                                )
                                                                AND `item_code` IN (
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
                                                            
            summe_lagerbuchungspositionen_negativ = frappe.db.sql("""SELECT
                                                                SUM(`amount`) AS `amount`
                                                            FROM `tabStock Entry Detail`
                                                            WHERE `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabStock Entry`
                                                                WHERE `project` = '{project}'
                                                                AND `docstatus` = 1
                                                                AND `stock_entry_type` = 'Material Receipt'
                                                            )""".format(project=self.project.name), as_dict=True)[0].amount or 0
            
            _summe_Lieferscheinpositionen = frappe.db.sql("""SELECT
                                                                `qty` AS `qty`,
                                                                `name` AS `voucher_detail_no`,
                                                                `serial_no`
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
            
            summe_ausgaben = frappe.db.sql("""SELECT
                                                    SUM(`grand_total`) AS `amount`
                                                FROM
                                                    `tabExpense Claim`
                                                WHERE
                                                    `project` = '{project}'
                                                AND
                                                    `approval_status` = "Approved"
                                                AND
                                                    `docstatus` = 1""".format(project=self.project.name), as_dict=True)[0].amount or 0
            
            summe_Lieferscheinpositionen = 0
            for value in _summe_Lieferscheinpositionen:
                valuation_rate = 0
                if not value.get('serial_no'):
                    valuation_rate = frappe.db.sql("""SELECT `valuation_rate` FROM `tabStock Ledger Entry` WHERE `voucher_detail_no` = '{0}'""".format(value.voucher_detail_no), as_dict=True)
                    if len(valuation_rate) > 0:
                        valuation_rate = valuation_rate[0].valuation_rate
                else:
                    serial_no = value.get('serial_no').replace(" ", "").split("/n")[0]
                    basic_rate = frappe.db.sql("""SELECT `basic_rate` FROM `tabStock Entry Detail` WHERE `serial_no` LIKE "%{0}%" """.format(serial_no), as_dict=True)
                    if len(basic_rate) > 0:
                        valuation_rate = basic_rate[0].basic_rate
                summe_Lieferscheinpositionen += (value.qty * (valuation_rate or 0))
            
            return (summe_einkaufsrechnungspositionen + summe_direktlieferungen + summe_lagerbuchungspositionen + summe_Lieferscheinpositionen - summe_lagerbuchungspositionen_negativ + summe_ausgaben) + (float(self.project.erfasste_externe_kosten_in_rhapsody) or 0)
        else:
            return self.project.summe_einkaufskosten_via_einkaufsrechnung
    def get_auftragsummen_gesamt(self):
        if not self.project.auftragsumme_manuell_festsetzen == 1:
            return self.project.total_sales_amount - get_projektbewertung_ignorieren_amount(self)
        else:
            return self.project.auftragsummen_gesamt
        
    def get_gesamtkosten_aktuell(self):
        return self.get_zeit_gebucht_ueber_zeiterfassung_eur() + self.get_summe_einkaufskosten_via_einkaufsrechnung()
    
    def get_ergebnis_aktuell(self):
        auftragsummen_gesamt = self.get_auftragsummen_gesamt() or 0
        gesamtkosten_aktuell = self.get_gesamtkosten_aktuell() or 0
        if self.project.status == "Completed" and auftragsummen_gesamt < gesamtkosten_aktuell:
            return gesamtkosten_aktuell - auftragsummen_gesamt
        else:
            return auftragsummen_gesamt - gesamtkosten_aktuell
    
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
        auftragsummen_gesamt = self.get_auftragsummen_gesamt() or 0
        geschaetzte_kosten_klon = self.get_geschaetzte_kosten_klon() or 0
        if self.project.status == "Completed" and auftragsummen_gesamt < geschaetzte_kosten_klon:
            return geschaetzte_kosten_klon - auftragsummen_gesamt
        else:
            return auftragsummen_gesamt - geschaetzte_kosten_klon
    
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
    
    def update_so_status(self):
        if len(self.project.get('payment_schedule')) > 0:
            for order in self.project.get('payment_schedule'):
                status = frappe.get_value("Sales Order", order.get('order'), "status")
                if status == "Closed" or status == "Completed":
                    order.set("so_closed", 1)
                else:
                    order.set("so_closed", 0)
        
        frappe.db.commit()
        
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
    #update Project KPIs for Sales Overview
    project_doc = frappe.get_doc("Project", project)
    project_doc.save()
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
            
        #update Discount if only Amount is set
        if order.discount_amount and not order.additional_discount_percentage:
            si.discount_amount = order.discount_amount / 100 * cint(percent)

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
            payment_entry = frappe.get_doc("Payment Entry", _payment_entry.parent)
            new_payment_entry = frappe.copy_doc(payment_entry)
            new_payment_entry.references = []
            new_payment_entry.save(ignore_permissions=True)
            
            # link new payment entry with sales order
            row = new_payment_entry.append('references', {})
            row.reference_doctype = "Sales Order"
            row.reference_name = sales_order.name
            row.allocated_amount = new_payment_entry.paid_amount
            row.outstanding_amount = new_payment_entry.paid_amount
            
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
    from frappe.utils.background_jobs import enqueue
    args = {}
    enqueue("energielenker.energielenker.project.project._auto_kpi_refresh", queue='long', job_name='Auto-KPI-Refresh', timeout=6000, **args)

def _auto_kpi_refresh():
    projects = frappe.db.sql("""SELECT `name` FROM `tabProject`""", as_dict=True)
    errors = []
    successes = []
    for _project in projects:
        try:
            project = frappe.get_doc("Project", _project.name)
            PowerProject(project).update_kpis()
            project.save()
            successes.append(_project.name)
        except:
            errors.append(_project.name)
    if len(errors) > 0:
        frappe.log_error("{0}".format(str(errors)), 'auto_kpi_refresh_errors')
    if len(successes) > 0:
        frappe.log_error("{0}".format(str(successes)), 'auto_kpi_refresh_successes')

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


@frappe.whitelist()
def update_payment_scheudle(name=None, invoice=None, invoice_date=None, amount=None, schlussrechnung=False):
    frappe.db.set_value("Payment Forecast", name, "invoice_created", 1, update_modified=False)
    frappe.db.set_value("Payment Forecast", name, "invoice", invoice, update_modified=False)
    frappe.db.set_value("Payment Forecast", name, "invoice_date", invoice_date, update_modified=False)
    if schlussrechnung:
        frappe.db.set_value("Payment Forecast", name, "amount", amount, update_modified=False)
    return

@frappe.whitelist()
def payment_forecast_rollback_invoice(so, sinv, project):
    def get_payments(sinv, docstatus=1):
        payments = frappe.db.sql("""
                                 SELECT `parent` AS `name`
                                 FROM `tabPayment Entry Reference`
                                 WHERE `reference_name` = '{0}'
                                 AND `docstatus` = {1}
                                 """.format(sinv, docstatus), as_dict=True)
        return payments
    
    def get_advance_payments(sinv):
        payments = []
        sinv = frappe.get_doc("Sales Invoice", sinv)
        for advance_payment in sinv.advances:
            payments.append({
                "name": advance_payment.reference_name
            })
        
        return payments

    def cancel_payments(payments):
        try:
            for payment in payments:
                p = frappe.get_doc("Payment Entry", payment.get("name"))
                p.cancel()
            return False
        except Exception as err:
            return err
    
    def check_for_schluss_rg(so):
        so = frappe.get_doc("Sales Order", so)
        for rg in so.billing_overview:
            if rg.billing_portion == 100:
                return True
        
        return False
    
    def cancel_invoice(sinv):
        try:
            sinv = frappe.get_doc("Sales Invoice", sinv)
            if sinv.docstatus == 1:
                sinv.cancel()
            elif sinv.docstatus == 0:
                sinv.submit()
                sinv.cancel()
            return False
        except Exception as err:
            return err
    
    def remove_sinv_from_so(so, sinv):
        try:
            so = frappe.get_doc("Sales Order", so)
            new_billing_overview = []
            for rg in so.billing_overview:
                if rg.sales_invoice != sinv:
                    new_billing_overview.append(rg)
            
            so.billing_overview = new_billing_overview
            so.save()
            return False
        except Exception as err:
            return err
    
    def remove_sinv_from_project(project, sinv):
        try:
            project = frappe.get_doc("Project", project)
            for rg in project.payment_schedule:
                if rg.invoice == sinv:
                    rg.invoice = None
                    rg.invoice_date = None
                    rg.invoice_created = 0
            project.save()
            return False
        except Exception as err:
            return err
    
    def cancel_returns(so, sinv):
        try:
            so = frappe.get_doc("Sales Order", so)
            for rg in so.billing_overview:
                if rg.sales_invoice != sinv:
                    return_sinvs = frappe.db.sql("""
                                                 SELECT `name`
                                                 FROM `tabSales Invoice`
                                                 WHERE `is_return` = 1
                                                 AND `return_against` = '{0}'
                                                 AND `docstatus` = 1
                                                 """.format(rg.sales_invoice), as_dict=True)
                    for return_sinv in return_sinvs:
                        r_sinv = frappe.get_doc("Sales Invoice", return_sinv.name)
                        r_sinv.cancel()
            return False
        except Exception as err:
            return err
    
    def resubmit_payments(so, sinv):
        try:
            so = frappe.get_doc("Sales Order", so)
            for rg in so.billing_overview:
                if rg.sales_invoice != sinv:
                    payments = get_payments(rg.sales_invoice, docstatus=2)
                    if len(payments) > 1:
                        return 'Mehrere stornierte Zahlungen zu {0} vorhanden'.format(rg.sales_invoice)
                    for payment in payments:
                        set_as_draft = frappe.db.sql("""
                                                     UPDATE `tabPayment Entry`
                                                     SET `docstatus` = 0
                                                     WHERE `name` = '{0}'
                                                     """.format(payment.name), as_list=True)
                        p = frappe.get_doc("Payment Entry", payment.name)
                        p.submit()
            return False
        except Exception as err:
            return err
    
    def return_data(status, typ=None, payments=None, info=None):
        data = {
            'status': status,
            'typ': typ,
            'payments': payments,
            'info': info
        }

        return data
    
    sinv = frappe.get_doc("Sales Invoice", sinv)

    if sinv.billing_type == 'Teilrechnung':
        if check_for_schluss_rg(so):
            return return_data(301, info='')
        
        payments = get_payments(sinv.name)
        if len(payments) > 0:
            error_in_cp = cancel_payments(payments)
            if error_in_cp:
                return return_data(302, info=error_in_cp)
        
        error_in_ri = remove_sinv_from_so(so, sinv.name)
        if error_in_ri:
            return return_data(304, info=error_in_ri)
        
        error_in_rip = remove_sinv_from_project(project, sinv.name)
        if error_in_rip:
            return return_data(305, info=error_in_rip)
        
        error_in_ci = cancel_invoice(sinv.name)
        if error_in_ci:
            return return_data(303, info=error_in_ci)
        
        return return_data(200, typ='Teilrechnung', payments=payments)
    
    elif sinv.billing_type == 'Schlussrechnung':
        error_in_ri = remove_sinv_from_so(so, sinv.name)
        if error_in_ri:
            return return_data(304, info=error_in_ri)
        
        error_in_rip = remove_sinv_from_project(project, sinv.name)
        if error_in_rip:
            return return_data(305, info=error_in_rip)
        
        advance_payments = get_advance_payments(sinv.name)
        if len(advance_payments) > 0:
            error_in_cp = cancel_payments(advance_payments)
            if error_in_cp:
                return return_data(302, info=error_in_cp)
        
        error_in_ci = cancel_invoice(sinv.name)
        if error_in_ci:
            return return_data(303, info=error_in_ci)
        
        error_in_cr = cancel_returns(so, sinv.name)
        if error_in_cr:
            return return_data(306, info=error_in_cr)
        
        error_in_rsp = resubmit_payments(so, sinv.name)
        if error_in_rsp:
            return return_data(308, info=error_in_rsp)
        
        return return_data(200, typ='Schlussrechnung')
    else:
        return return_data(307, info='Unbekannter Rechnungstyp')

@frappe.whitelist()
def check_order_payment_forecast_errors(order):
    o = frappe.get_doc("Sales Order", order)
    #Check if Customer is blocked
    if cint(frappe.db.get_value("Customer", o.get('customer'), "blocked_customer")) == 1:
        return {
            'errors': 1,
            'msg': "Die Rechnung konnte nicht erstellt werden, da Kunde der {0} gesperrt ist. <br> Entsperren Sie diesen Kunden und versuchen Sie es erneut.".format(o.get('customer'))
        }
    
    #Check if any Item is disabled or must be whole number
    disabled_items = 0
    whole_number_uom = 0
    disabled_msg = ''
    whole_number_msg = ''
    for item in o.items:
        if cint(frappe.db.get_value("Item", item.item_code, "disabled")) == 1:
            disabled_items += 1
            disabled_msg += '''
                <br>Zeile: {0} // Artikel: {1}
            '''.format(item.idx, item.get('item_name'))
        elif cint(frappe.db.get_value("UOM", item.get('uom'), "must_be_whole_number")) == 1:
            whole_number_uom += 1
            whole_number_msg += '''
                <br>Zeile: {0} // Artikel: {1} // Einheit: <b>{2}</b>
            '''.format(item.idx, item.get('item_name'), item.get('uom'))
            
    #Part List Items
    for pl_item in o.part_list_items:
        if cint(frappe.db.get_value("Item", pl_item.item_code, "disabled")) == 1:
            disabled_items += 1
            disabled_msg += '''
                <br>Zeile: {0}(Stücklistenartikel) // Artikel: {1}
            '''.format(pl_item.idx, pl_item.get('item_name'))
        elif cint(frappe.db.get_value("UOM", pl_item.get('uom'), "must_be_whole_number")) == 1:
            whole_number_uom += 1
            whole_number_msg += '''
                <br>Zeile: {0}(Stücklistenartikel) // Artikel: {1} // Einheit: <b>{2}</b>
            '''.format(pl_item.idx, pl_item.get('item_name'), pl_item.get('uom'))
            
    if disabled_items > 0:
        return {
            'errors': disabled_items,
            'msg': "Die Rechnung konnte nicht erstellt werden.<br>Nachfolgende Artikel sind deaktivert:<br>{0}<br><br>Aktivieren Sie diese und versuchen Sie es erneut.".format(disabled_msg)
        }
    elif whole_number_uom > 0:
        return {
            'errors': whole_number_uom,
            'msg': "Die Rechnung konnte nicht erstellt werden.<br>Nachfolgende Einheiten müssen ganze Zahl sein:<br>{0}<br><br>Entfernen Sie dies und versuchen Sie es erneut.".format(whole_number_msg)
        }
    else:
        #Check for Cancelled Payments
        cancelled_payments, cancelled_payments_msg = check_for_chancelled_payments(o)
        if cancelled_payments > 0:
            return {
                'errors': cancelled_payments,
                'msg': "Folgende Zahlungen sind abgebrochen und würden zum Absturz vom Prozess führen:<br>{0}<br><br>Bereinigen Sie die Zahlungen und versuchen Sie es erneut.".format(cancelled_payments_msg)
            }
    return {
            'errors': 0,
            'msg': ""
            }
    
    
def check_open_depots(self, event):
    if self.open_depots:
        if self.open_depots > 0 and self.status != "Open":
            frappe.throw("Projekt enthält offene Kommissionierungen und kann nicht geschlossen werden!")
    return

def check_for_chancelled_payments(order_doc):
    cancelled_payments = 0
    cancelled_payments_msg = ''
    for invoice in order_doc.billing_overview:
        stock_uom_check(invoice.get('sales_invoice'))
        cancelled_invoice_payments = frappe.db.sql("""
                                            SELECT
                                                `parent`
                                            FROM
                                                `tabPayment Entry Reference`
                                            WHERE
                                                `reference_name` = '{si}'
                                            AND
                                                `docstatus` = 2""".format(si=invoice.get('sales_invoice')), as_dict=True)
        if len(cancelled_invoice_payments) > 0:
            for cancelled_invoice_payment in cancelled_invoice_payments:
                cancelled_payments += 1
                cancelled_payments_msg += '''
                <br>Zahlung: {0} (Rechnung: {1})
                '''.format(cancelled_invoice_payment.get('parent'), invoice.get('sales_invoice'))
            
    return cancelled_payments, cancelled_payments_msg

def stock_uom_check(invoice):
    invoice_doc = frappe.get_doc("Sales Invoice", invoice)
    for item in invoice_doc.get('items'):
        if item.get('stock_qty') != item.get('qty'):
            frappe.db.set_value('Sales Invoice Item', item.get('name'), 'qty', item.get('stock_qty'))
            frappe.db.commit()
    return

def update_project_manager(self, event):
    #get before save project manager
    old_pm = frappe.db.get_value("Project", self.get('name'), "project_manager_name")
    
    #check project manager has changed
    if old_pm != self.get('project_manager_name'):
        #if it has changed, get all releated Documents and update them
        documents_to_update = frappe.db.sql("""
                                            SELECT
                                                `name`,
                                                'Sales Order' AS `doctype`
                                            FROM
                                                `tabSales Order`
                                            WHERE
                                                `project_clone` = '{project}'
                                            AND
                                                (`project_manager_name` != '{pm}'
                                            OR
                                                `project_manager_name` IS NULL)
                                            AND
                                                `docstatus` != 2
                                                
                                            UNION ALL
                                            
                                            SELECT
                                                `name`,
                                                'Sales Invoice' AS `doctype`
                                            FROM
                                                `tabSales Invoice`
                                            WHERE
                                                `project` = '{project}'
                                            AND
                                                (`project_manager_name` != '{pm}'
                                            OR
                                                `project_manager_name` IS NULL)
                                            AND
                                                `docstatus` != 2
                                                
                                            UNION ALL
                                            
                                            SELECT
                                                `name`,
                                                'Delivery Note' AS `doctype`
                                            FROM
                                                `tabDelivery Note`
                                            WHERE
                                                `project` = '{project}'
                                            and
                                                (`project_manager_name` != '{pm}'
                                            OR
                                                `project_manager_name` IS NULL)
                                            AND
                                                `docstatus` != 2""".format(pm=self.get('project_manager_name'), project=self.get('name')), as_dict=True)
                                                
        for doc in documents_to_update:
            frappe.set_value(doc.get('doctype'), doc.get('name'), "project_manager_name", self.get('project_manager_name'))
            
        return

@frappe.whitelist()
def check_service_project_orders(project):
    orders = frappe.db.sql("""
                            SELECT
                                `name`
                            FROM
                                `tabSales Order`
                            WHERE
                                `docstatus` = 1
                            AND
                                `project` = '{project}';""".format(project=project), as_dict=True)
    
    return orders

@frappe.whitelist()
def update_service_orders(project, service_check):
    #Check if Service Project Check has been changed
    old_check = frappe.db.get_value("Project", project, "is_service_project")
    
    if service_check != old_check:
        #Get all orders for related Project
        orders = frappe.db.sql("""
                                SELECT
                                    `name`
                                FROM
                                    `tabSales Order`
                                WHERE
                                    `project` = '{project}';""".format(project=project), as_dict=True)
        
        #Update Orders and its Positions
        if len(orders) > 0:
            for order in orders:
                frappe.db.set_value("Sales Order", order.get('name'), "is_service_project", service_check)
                position_update = frappe.db.sql("""
                                                UPDATE
                                                    `tabSales Order Item`
                                                SET
                                                    `is_service_project_item` = {check}
                                                WHERE
                                                    `parent` = '{sales_order}';""".format(check=service_check, sales_order=order.get('name')), as_dict=True)
                
    return
