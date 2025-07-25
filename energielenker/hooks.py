# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "energielenker"
app_title = "energielenker"
app_publisher = "libracore"
app_description = "energielenker Soloutions"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@libracore.com"
app_license = "MIT"

fixtures = [
    {"dt": "Contract Template", "filters": [["name", "in", ["Dienstleistungsvertrag", "Werkvertrag"]]]}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/energielenker/css/energielenker.css"
# app_include_js = "/assets/energielenker/js/energielenker.js"
app_include_css = [
    "/assets/energielenker/css/energielenker.css"
]
app_include_js = [
    "/assets/js/energielenkertemplates.min.js",
    "/assets/energielenker/js/energielenker.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/energielenker/css/energielenker.css"
# web_include_js = "/assets/energielenker/js/energielenker.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Project": "energielenker/project/project.js",
    "Sales Order": "energielenker/sales_order/sales_order.js",
    "Quotation": "energielenker/quotation/quotation.js",
    "Sales Invoice": "energielenker/sales_invoice/sales_invoice.js",
    "Delivery Note": "energielenker/delivery_note/delivery_note.js",
    "Address": "energielenker/address/address.js",
    "Contact": "energielenker/contact/contact.js",
    "Purchase Order": "energielenker/purchase_order/purchase_order.js",
    "Purchase Invoice": "energielenker/purchase_invoice/purchase_invoice.js",
    "Item": "energielenker/item/item.js",
    "Material Request": "energielenker/material_request/material_request.js",
    "Purchase Receipt": "energielenker/purchase_receipt/purchase_receipt.js",
    "Issue": "energielenker/issue/issue.js",
    "Task": "energielenker/task/task.js",
    "Customer": "energielenker/customer/customer.js",
    "Timesheet": "energielenker/timesheet/timesheet.js",
    "Stock Entry": "energielenker/stock_entry/stock_entry.js",
    "Request for Quotation": "energielenker/request_for_quotation/request_for_quotation.js",
    "Supplier": "energielenker/supplier/supplier.js",
    "BOM": "energielenker/bom/bom.js",
    "Auto Repeat": "energielenker/auto_repeat/auto_repeat.js",
    "Lead": "energielenker/lead/lead.js",
    "Cost Center": "energielenker/cost_center/cost_center.js",
    "Item Price": "energielenker/item_price/item_price.js",
    "Stock Reconciliation": "energielenker/stock_reconciliation/stock_reconciliation.js",
    "Work Order": "energielenker/work_order/work_order.js",
    "Product Bundle": "energielenker/product_bundle/product_bundle.js",
    "Warehouse": "energielenker/warehouse/warehouse.js"
}

doctype_list_js = {
    "Project" : "energielenker/project/project_list.js",
    "Sales Invoice" : "energielenker/sales_invoice/sales_invoice_list.js",
    "Sales Order" : "energielenker/sales_order/sales_order_list.js",
    "Quotation": "energielenker/quotation/quotation_list.js",
    "Purchase Order": "energielenker/purchase_order/purchase_order_list.js",
    "Purchase Invoice": "energielenker/purchase_invoice/purchase_invoice_list.js",
    "Purchase Receipt": "energielenker/purchase_receipt/purchase_receipt_list.js",
    "Delivery Note": "energielenker/delivery_note/delivery_note_list.js",
    "Task": "energielenker/task/task_list.js",
    "Material Request" : "energielenker/material_request/material_request_list.js",
    "Address" : "energielenker/address/address_list.js",
    "Contact" : "energielenker/contact/contact_list.js",
    "Customer" : "energielenker/customer/customer_list.js",
    "Issue" : "energielenker/Issue/issue_list.js",
    "Item" : "energielenker/Item/item_list.js",
    "Lead" : "energielenker/Lead/lead_list.js",
    "Stock Entry" : "energielenker/Stock Entry/stock_entry_list.js",
    "Supplier" : "energielenker/Supplier/supplier_list.js",
    "Timesheet" : "energielenker/Timesheet/timesheet_list.js",
    "ToDo" : "energielenker/ToDo/todo_list.js",
    "Work Order" : "energielenker/Work Order/work_order_list.js"
}

jenv = {
    "methods": [
        "get_print_items:energielenker.energielenker.print_utils.utils.get_print_items",
        "get_delivery_note_lizenzgutschein:energielenker.energielenker.doctype.lizenzgutschein.lizenzgutschein.get_delivery_note_lizenzgutschein",
        "get_lizenz_qty_so:energielenker.energielenker.doctype.lizenzgutschein.lizenzgutschein.get_lizenz_qty_so",
        "get_items_html:energielenker.energielenker.doctype.depot.depot.get_items_html",
        "get_bom_items:energielenker.energielenker.stock_entry.stock_entry.get_bom_items",
        "rounded:frappe.utils.data.rounded",
        "format_qty:energielenker.energielenker.print_utils.utils.format_qty",
        "get_billing_status:energielenker.energielenker.print_utils.utils.get_billing_status"
    ]
}

# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#   "Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "energielenker.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "energielenker.install.before_install"
# after_install = "energielenker.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "energielenker.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#   "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#   "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Project": {
        "autoname": "energielenker.energielenker.project.project.autoname",
        "onload": "energielenker.energielenker.project.project.onload",
        "validate": "energielenker.energielenker.project.project.validate",
        "on_update": "energielenker.energielenker.zahlungsplan.zahlungsplan.update_projektbewertung_ignorieren_in_project_or_in_so",
        "before_save": ["energielenker.energielenker.project.project.check_open_depots", "energielenker.energielenker.project.project.update_project_manager"]
    },
    "Task": {
        "on_update": "energielenker.energielenker.task.task.on_update"
    },
    "Sales Order": {
        "on_submit": [
            "energielenker.energielenker.sales_order.sales_order.fetch_payment_schedule_from_so",
            "energielenker.energielenker.sales_order.sales_order.update_delivery_status"
        ],
        "validate": "energielenker.energielenker.utils.utils.get_plz_gebiet",
        "after_insert": "energielenker.energielenker.sales_invoice.sales_invoice.set_billing_information"
    },
    "Timesheet": {
        "after_insert": "energielenker.energielenker.timesheet.timesheet.assign_read_for_all",
        "on_submit": "energielenker.energielenker.issue.issue.set_booked_hours",
        "on_cancel": "energielenker.energielenker.issue.issue.set_booked_hours",
        "on_update_after_submit": "energielenker.energielenker.timesheet.timesheet.validate_manual_invoice"
    },
    "Item": {
        "after_insert": "energielenker.energielenker.item.item.check_item_code"
    },
    "Sales Invoice": {
        "validate": "energielenker.energielenker.sales_invoice.sales_invoice.validate_navision_of_items",
        "on_submit": "energielenker.energielenker.sales_invoice.sales_invoice.charged_at_cost",
        "before_submit": "energielenker.energielenker.sales_invoice.sales_invoice.set_navision_export_check",
        "on_cancel": "energielenker.energielenker.sales_invoice.sales_invoice.charged_at_cost",
        "after_insert": "energielenker.energielenker.sales_invoice.sales_invoice.set_billing_information"
    },
    "Purchase Invoice": {
        "validate": "energielenker.energielenker.purchase_invoice.purchase_invoice.validate_lagerfuehrung_of_items"
    },
    "Delivery Note": {
        "validate": "energielenker.energielenker.delivery_note.delivery_note.validate_valuation_rate",
        "before_submit": "energielenker.energielenker.delivery_note.delivery_note.check_depot_delivery",
        "on_submit": "energielenker.energielenker.delivery_note.delivery_note.set_invoiced_items"
    },
    "Issue": {
        "onload": "energielenker.energielenker.issue.issue.onload_functions",
        "after_insert": "energielenker.energielenker.issue.issue.mark_for_reply"
    },
    "Communication": {
        "after_insert": "energielenker.energielenker.issue.issue.add_mail_as_description_to_issue"
    },
    "ToDo": {
        "after_insert": "energielenker.energielenker.todo.todo.check_for_assigment",
        "on_update": "energielenker.energielenker.todo.todo.check_for_assigment"
    },
    "Email Queue": {
        "after_insert": "energielenker.energielenker.utils.admin_mails.stop"
    },
    "Lead": {
        "on_trash": "energielenker.energielenker.utils.lead.delete_events"
    },
    "Address": {
        "validate": "energielenker.energielenker.utils.lead.insert_plz_gebiet"
    },
    "Quotation": {
        "validate": "energielenker.energielenker.utils.utils.get_plz_gebiet",
        "on_submit": "energielenker.energielenker.lead.lead.update_lead_status",
        "before_update_after_submit": "energielenker.energielenker.lead.lead.update_lead_status",
        "on_cancel": "energielenker.energielenker.lead.lead.update_lead_status"
    },
    "Product Bundle": {
        "on_trash": "energielenker.energielenker.product_bundle.product_bundle.delete_redord"
    },
    "BOM": {
        "autoname": "energielenker.energielenker.bom.bom.autoname"
    },
    "Work Order": {
        "on_submit": "energielenker.energielenker.work_order.work_order.set_has_work_order_in_sales_order",
        "on_cancel": "energielenker.energielenker.work_order.work_order.unset_has_work_order_in_sales_order"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "energielenker.energielenker.project.project.auto_kpi_refresh",
        "energielenker.energielenker.quotation.quotation.change_status_from_old_angebote",
        "energielenker.energielenker.utils.auto_reminder.check_for_reminder",
        "energielenker.energielenker.utils.auto_email_report.send_monthly_reports",
        "energielenker.energielenker.quotation.quotation.update_quotation_status",
        "energielenker.energielenker.doctype.depot.depot.daily_depot_check",
        "energielenker.energielenker.purchase_order.purchase_order.autoclose_purchase_order",
        "energielenker.energielenker.todo.todo.reminder_email"
    ],
    "all": [
        "energielenker.energielenker.issue.issue.delete_based_on_mark"
    ]
}

# Testing
# -------

# before_tests = "energielenker.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#   "frappe.desk.doctype.event.event.get_events": "energielenker.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#   "Task": "energielenker.task.get_dashboard_data"
# }
