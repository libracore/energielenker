import frappe
from frappe import _

def execute():
    items = frappe.db.sql("""SELECT `name`, `item_code` FROM `tabDelivery Note Item`""", as_dict=True)
    counter = 1
    for item in items:
        valuation_rate = frappe.db.get_value('Item', item.item_code, 'valuation_rate')
        update = frappe.db.sql("""UPDATE `tabDelivery Note Item` SET `valuation_rate` = {0} WHERE `name` = '{1}'""".format(valuation_rate, item.name), as_list=True)
        print("Done {0} of {1}".format(counter, len(items)))
        counter += 1
    return
