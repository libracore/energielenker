// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Overview"] = {
	"filters": [
        {
            "fieldname":"type",
            "label": __("Type"),
            "fieldtype": "Select",
            "options": "Sold Items\nSales Invoice per Cost Center\nSales Order per Cost Center",
            "reqd": 1
        },
        {
            "fieldname":"year_filter",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": get_options()
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        }
	]
};

function get_options() {
    
    return " \n2024"
}
