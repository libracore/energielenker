import frappe
from frappe import _
from frappe.utils.data import add_months, nowdate

def execute():
    # this will return back all the quotations that are still valid to "Open" and the quotations that have less than 6 months old to "Expired"
    months = add_months(nowdate(), -5)
    expired_quotations_list = frappe.db.sql("""SELECT `name` FROM `tabQuotation` WHERE `status` = 'Lost' AND `valid_till` BETWEEN '{months}' AND '{nowdate}'""".format(months=months, nowdate=nowdate()), as_dict=True)
    valid_quotations_list = frappe.db.sql("""SELECT `name` FROM `tabQuotation` WHERE `status` = 'Lost' AND `valid_till` > '{nowdate}'""".format(nowdate=nowdate()), as_dict=True)
    
    for q in expired_quotations_list:
        quotation = frappe.get_doc("Quotation", q['name'])
        if quotation.lost_reasons and quotation.lost_reasons[0].lost_reason == 'unbekannt (Ausschreibung)':
            frappe.db.set(quotation, 'status', 'Expired')
            quotation.lost_reasons = []
            quotation.save()
            print("Expired {0}".format(quotation.name))
    
    for q in valid_quotations_list:
        quotation = frappe.get_doc("Quotation", q['name'])
        if quotation.lost_reasons and quotation.lost_reasons[0].lost_reason == 'unbekannt (Ausschreibung)':
            frappe.db.set(quotation, 'status', 'Open')
            quotation.lost_reasons = []
            quotation.save()
            print("Open {0}".format(quotation.name))

    return
