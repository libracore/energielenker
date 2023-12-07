import frappe
from frappe import _
import json

def execute():
    print("Running default warehouse Patch...")
    items = frappe.db.sql("""SELECT `name` FROM `tabItem` WHERE `is_stock_item` = 1""", as_dict=True)
    total = len(items)
    loop = 1
    for item in items:
        print("{loop} of {total}".format(loop=loop, total=total))
        try:
            i = frappe.get_doc("Item", item.name)
            if len(i.item_defaults) > 0:
                if i.item_defaults[0].default_warehouse:
                    i.default_warehouse_readonly = i.item_defaults[0].default_warehouse
                    i.save()
        except Exception as err:
            print("{0} Failed: {1}".format(item.name, err))
        loop += 1
    print("Done")
    return
