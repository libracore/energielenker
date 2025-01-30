import frappe

def execute():
    work_orders = frappe.get_all("Work Order", filters={"docstatus": 1}, fields=["name", "sales_order"])
    i = 0

    for work_order in work_orders:
        if (work_order.sales_order):
            i += 1
            frappe.db.sql("""UPDATE `tabSales Order` SET `has_work_order` = 1 WHERE `name` = '{sales_order}'""".format(sales_order=work_order.sales_order))

    frappe.db.commit()
    return