from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Seriennummer"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Seriennummer energielenker",
                    "label": _("Seriennummer energielenker"),
                    "description": _("Seriennummer energielenker")
                }
            ]
        },
        {
            "label": _("Einstellungen"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "energielenker Settings",
                    "label": _("energielenker"),
                    "description": _("energielenker Settings")
                }
            ]
        },
        {
            "label": _("Stammdaten"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Quotation Template",
                    "label": _("Quotation Template"),
                    "description": _("Quotation Template")
                },
                {
                    "type": "doctype",
                    "name": "Navision Kontenplan",
                    "label": _("Navision Kontenplan"),
                    "description": _("Navision Kontenplan")
                },
                {
                    "type": "doctype",
                    "name": "Contact Function",
                    "label": _("Contact Function"),
                    "description": _("Contact Function")
                },
                {
                    "type": "doctype",
                    "name": "Project Status",
                    "label": _("Project Status"),
                    "description": _("Project Status")
                },
                {
                    "type": "doctype",
                    "name": "Project Team",
                    "label": _("Project Team"),
                    "description": _("Project Team")
                }
            ]
        }
    ]
