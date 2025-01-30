import frappe

def execute():
    sales_orders = frappe.get_all("Sales Order", filters={"docstatus": 1}, fields=["name"])

    for sales_order in sales_orders:
        work_orders = frappe.get_all("Work Order", filters={"sales_order": sales_order.name, "docstatus": 1}, fields=["name"])
        if len(work_orders) > 0:
            frappe.db.sql("""UPDATE `tabSales Order` SET `has_work_order` = 1 WHERE `name` = '{sales_order}'""".format(sales_order=sales_order.name))
    return