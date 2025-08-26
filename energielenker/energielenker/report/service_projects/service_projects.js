// Copyright (c) 2025, libracore and contributors
// For license information, please see license.txt

frappe.query_reports["Service projects"] = {
	"filters": [
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": new Date().getFullYear() + "-01-01"
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        }
    ],
    "initial_depth": 0
};

/* add event listener for double clicks to move up */
cur_page.container.addEventListener("dblclick", function(event) {
    // restrict to this report to prevent this event on other reports once loaded
    if (window.location.toString().includes("/Service%20projects") ) {
        let row = event.delegatedTarget.getAttribute("data-row-index");
        let column = event.delegatedTarget.getAttribute("data-col-index");
        
        if (column.toString() === "13") {                 // 13 is the column index of "Create invoice"
            console.log("Create invoice for " + frappe.query_report.data[row]['customer']);
            let project = frappe.query_report.data[row]['project'];
            frappe.dom.freeze('Bitte warten, die Rechnungen werden erzeugt...');
            frappe.call({
                'method': "energielenker.energielenker.report.service_projects.service_projects.create_invoice",
                'args': {
                    'from_date': (frappe.query_report.get_filter_value("from_date") || "2000-01-01"),
                    'to_date': (frappe.query_report.get_filter_value("to_date") || "2099-12-31"),
                    'project': project
                },
                'callback': function(response) {
                    if (response.message && response.message.length == 1) {
                        frappe.show_alert( __("Created") + ": <a href='/desk#Form/Sales Invoice/" + response.message[0]
                            + "'>" + response.message + "</a>");
                        frappe.query_report.refresh();
                    } else if (response.message && response.message.length > 1) {
                        let msg = "Folgende Rechnungen wurden erstellt:<br>"
                        for (let i = 0; i < response.message.length; i++) {
                            msg = msg + "<br>-" + response.message[i];
                        }
                        frappe.msgprint(msg, "Rechnungen erstellt.");
                    } else {
                        frappe.show_alert("Irgendetwas ist bei der Verrechnung schief gelaufen.")
                    }
                    frappe.dom.unfreeze();
                }
            });
        }
    }
});
