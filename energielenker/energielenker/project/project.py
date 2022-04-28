# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from energielenker.energielenker.timesheet_manager import get_employee_rate_external, get_employee_rate_internal
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils.data import get_datetime, today


class PowerProject():
    def __init__(self, project):
        self.project = project
        self.subprojects = []
        
        for row in project.subprojects:
            pp = PowerProject(frappe.get_doc("Project", row.subproject))
            pp.project.update_costing()
            pp.update_kpis()
            self.subprojects.append(pp.project)

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
            "total_amount",
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
        dates = [
            ("actual_start_date", False),
            ("actual_end_date", True)
        ]

        for (date, startdate) in dates:
            self.update_date(date, startdate)

    def update_date(self, date, startdate):
        dates = [subproject.get(date) for subproject in self.subprojects if subproject.get(date)]
        project_date = self.project.get(date)

        if project_date:
            dates.append(get_datetime(project_date))

        if dates:
            self.project.set(date, max(dates) if startdate else min(dates))

    def update_custom_kpi(self, kpi):
        value_project = getattr(self, "get_{kpi}".format(kpi=kpi))()
        self.update_kpi(kpi, value_project)

    def update_erpnext_kpi(self, kpi):
        value_project = self.project.get(kpi) or 0
        self.update_kpi(kpi, value_project)

    def update_kpi(self, kpi, value_project):
        value_subprojects = 0

        for subproject in self.subprojects:
            value_subprojects += subproject.get(kpi)

        self.project.set(kpi, value_project + value_subprojects)

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
                max(task.expected_time - task.actual_time, 0) 
                * self.get_employee_rate(task.completed_by)
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
                task.expected_time 
                * self.get_employee_rate(task.completed_by)
            )
        
        return expected_billable_amount
    
    def get_total_amount(self):
        return self.project.total_sales_amount
    
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
                self.get_employee_rate(task.completed_by, internal=True) * task.expected_time
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
        median = 0
        alle_std_saetze = 0
        anz_members = 0
        for member in self.project.members:
            member_satz = self.get_employee_rate(member.employee, internal=True)
            if member_satz > 0:
                alle_std_saetze += member_satz
                anz_members += 1
        if anz_members > 0:
            median = (alle_std_saetze / anz_members)
        eur += (self.project.gebuchte_stunden_in_rhapsody * median)
        
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
                max(task.expected_time - task.actual_time, 0) * self.get_employee_rate(task.completed_by, internal=True)
            )
        
        return eur
        
    def get_voraussichtliche_abweichung_eur(self):
        eur = self.get_voraussichtliche_abweichung() * self.project.default_external_rate
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
        return self.project.total_purchase_cost + self.project.erfasste_externe_kosten_in_rhapsody
    
    def get_auftragsummen_gesamt(self):
        return self.project.total_sales_amount
        
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
            
            # copy old payment erntry
            new_payment_entry = frappe.copy_doc(payment_entry)
            new_payment_entry.save(ignore_permissions=True)
            
            # link new payment entry with sales order
            new_payment_entry.references = []
            row = new_payment_entry.append('references', {})
            row.reference_doctype = "Sales Order"
            row.reference_name = sales_order.name
            row.allocated_amount = new_payment_entry.paid_amount
            
            new_payment_entry.save(ignore_permissions=True)
            new_payment_entry.submit()
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

def auto_kpi_refresh():
    projects = frappe.db.sql("""SELECT `name` FROM `tabProject`""", as_dict=True)
    for _project in projects:
        project = frappe.get_doc("Project", _project.name)
        PowerProject(project).update_kpis()
        project.save()
