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
    "Item": "energielenker/item/item.js"
}

doctype_list_js = {
    "Project" : "energielenker/project/project_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
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
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Project": {
        "autoname": "energielenker.energielenker.project.project.autoname",
        "onload": "energielenker.energielenker.project.project.onload",
        "validate": "energielenker.energielenker.project.project.validate"
    },
    "Task": {
        "on_update": "energielenker.energielenker.task.task.on_update"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"energielenker.tasks.all"
# 	],
# 	"daily": [
# 		"energielenker.tasks.daily"
# 	],
# 	"hourly": [
# 		"energielenker.tasks.hourly"
# 	],
# 	"weekly": [
# 		"energielenker.tasks.weekly"
# 	]
# 	"monthly": [
# 		"energielenker.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "energielenker.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "energielenker.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "energielenker.task.get_dashboard_data"
# }
