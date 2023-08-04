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
        }
]
