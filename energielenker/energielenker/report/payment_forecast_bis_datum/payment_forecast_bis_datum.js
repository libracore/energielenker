// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Forecast bis Datum"] = {
    "filters": [
        {
            "fieldname":"date",
            "label": __("Zahlungsdatum bis einschl."),
            "fieldtype": "Date",
            "default": frappe.datetime.year_end(),
            "reqd": 1
        },
        {
            "fieldname":"not_null",
            "label": __("Saldo > 0"),
            "fieldtype": "Check",
            "default": 1
        }
    ]
};
