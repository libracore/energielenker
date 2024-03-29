from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
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
                    "name": "Lizenz Anfrage",
                    "label": _("Lizenz Anfrage"),
                    "description": _("Lizenz Anfrage")
                }
            ]
        }
    ]
