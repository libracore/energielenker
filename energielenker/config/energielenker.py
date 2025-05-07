from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Energielenker"),
            "icon": "fa fa-money-bill",
            "items": [
                {
                    "type": "doctype",
                    "name": "Depot",
                    "label": _("Kommissionierung"),
                    "description": _("Depot")
                },
                {
                    "type": "report",
                    "name": "Customer Overview",
                    "label": _("Kundenübersicht"),
                    "doctype": "Customer",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Sales Overview",
                    "label": _("Verkaufsübersicht"),
                    "doctype": "Sales Order",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Lead Source Report",
                    "label": _("Lead Quelle"),
                    "doctype": "Sales Order",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "energielenker Stock Balance",
                    "label": _("energielenker Stock Balance"),
                    "doctype": "Stock Ledger Entry",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "IBN remote",
                    "label": _("IBN remote"),
                    "doctype": "Sales Order",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Service projects",
                    "label": _("Service projects"),
                    "doctype": "Project",
                    "is_query_report": True
                }
            ]
        },
        {
            "label": _("Dashboards"),
            "icon": "fa fa-money-bill",
            "items": [
                {
                    "type": "page",
                    "name": "vertriebs-dashboard",
                    "label": _("Vertriebs-Dashboard"),
                    "description": _("Vertriebs-Dashboard")
                },
                {
                    "type": "page",
                    "name": "controlling-dashboard",
                    "label": _("Controlling-Dashboard"),
                    "description": _("Controlling-Dashboard")
                }
            ]
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-money-bill",
            "items": [
                {
                    "type": "doctype",
                    "name": "energielenker Settings",
                    "label": _("energielenker Settings"),
                    "description": _("energielenker Settings")
                }
            ]
        },
        {
            "label": _("API"),
            "icon": "fa fa-money-bill",
            "items": [
                {
                    "type": "doctype",
                    "name": "Ladepunkt Key API",
                    "label": _("Ladepunkt Key API"),
                    "description": _("Ladepunkt Key API")
                },
                {
                    "type": "doctype",
                    "name": "Ladepunkt Key API Purchase Order",
                    "label": _("Ladepunkt Key API - Purchase Order"),
                    "description": _("Ladepunkt Key API Purchase Order")
                },
                {
                    "type": "doctype",
                    "name": "Lizenz Anfrage",
                    "label": _("Lizenz Anfrage"),
                    "description": _("Lizenz Anfrage")
                }
            ]
        },
        {
            "label": _("Ladepunkt-Key Webshop"),
            "icon": "fa fa-money-bill",
            "items": [
                {
                    "type": "doctype",
                    "name": "Charging Point Key Account",
                    "label": _("Charging Point Key Account"),
                    "description": _("Charging Point Key Account")
                },
                {
                    "type": "doctype",
                    "name": "Webshop Settings",
                    "label": _("Webshop Settings"),
                    "description": _("Webshop Settings")
                }
            ]
        }
    ]
