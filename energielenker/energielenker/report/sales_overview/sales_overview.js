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
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "on_change": function(query_report) {
                set_date_filters(frappe.query_report.filters[1].value);
            }
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
	],
    "initial_depth": 0
};

function set_date_filters(year) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Fiscal Year",
            'name': year
        },
        'callback': function(response) {
            frappe.query_report.set_filter_value('from_date', response.message.year_start_date);
            frappe.query_report.set_filter_value('to_date', response.message.year_end_date);
        }
    });
    return
}
