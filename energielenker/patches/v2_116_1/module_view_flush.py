import frappe
from frappe import _
import json

def execute():
    print("Running Patch module_view_flush...")
    users = frappe.db.sql("""SELECT `name`, `home_settings` FROM `tabUser` WHERE `enabled` = 1""", as_dict=True)
    total = len(users)
    loop = 1
    for user in users:
        print("{loop} of {total}".format(loop=loop, total=total))
        try:
            s = frappe.parse_json(user.home_settings)
            s['modules_by_category']['Modules'].append("energielenker")
            
            frappe.db.set_value("User", user.name, "home_settings", json.dumps(s))
            frappe.cache().hset('home_settings', user.name, s)
        except Exception as err:
            print("{0} Failed: {1}".format(user.name, err))
        loop += 1
    print("Done")
    return
