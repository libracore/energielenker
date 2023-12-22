import frappe
from frappe import _

def execute():
    print("Running stock reconciliation Patch...")
    try:
        srs = frappe.db.sql("""
            SELECT `name`
            FROM `tabStock Reconciliation`
            WHERE `docstatus` = 1
        """, as_dict=True)
        for sr in srs:
            record = frappe.get_doc("Stock Reconciliation", sr.name)
            difference_amount = 0.0
            for item in record.items:
                difference_amount += item.amount_difference
            update_sr = frappe.db.sql("""
                UPDATE `tabStock Reconciliation`
                SET `difference_amount` = '{difference_amount}'
                WHERE `name` = '{sr}'
            """.format(difference_amount=difference_amount, sr=sr.name), as_list=True)
    except Exception as err:
        print("failed: {0}".format(str(err)))