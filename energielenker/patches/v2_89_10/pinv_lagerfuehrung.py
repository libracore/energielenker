import frappe
from frappe import _

def execute():
    # this will add the main_project to all existing subprojects
    items = frappe.db.sql("""SELECT `name`, `item_code` FROM `tabPurchase Invoice Item`""", as_dict=True)
    counter = 1
    for item in items:
        lagerfuehrung = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
        update = frappe.db.sql("""UPDATE `tabPurchase Invoice Item` SET `ist_lagergefuehrt` = {0} WHERE `name` = '{1}'""".format(lagerfuehrung, item.name), as_list=True)
        print("Done {0} of {1}".format(counter, len(items)))
        counter += 1
    return
