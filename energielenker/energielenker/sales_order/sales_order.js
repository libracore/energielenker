// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
    on_submit: function (frm) {
        if (cur_frm.doc.project) {
            // add fetch payment forecast
            frappe.call({
                method: "energielenker.energielenker.project.project.fetch_payment_schedule",
                args: {
                    "project": cur_frm.doc.project,
                    "sales_order": cur_frm.doc.name,
                    "payment_schedule": cur_frm.doc.payment_schedule
                },
                callback: function (r) {}
            });
        }
    },
    after_cancel: function(frm) {
        if (cur_frm.doc.project) {
            // clear fetched payment forecast
            frappe.call({
                method: "energielenker.energielenker.project.project.clear_payment_schedule",
                args: {
                    "project": cur_frm.doc.project,
                    "sales_order": cur_frm.doc.name
                },
                callback: function (r) {}
            });
        }
    },
    customer: function(frm) {
        shipping_address_query(frm);
    },
    validate: function(frm) {
        check_navision(frm);
    }
});

function shipping_address_query(frm) {
    cur_frm.fields_dict['shipping_address_name'].get_query = function(doc) {
        return {
            query: 'frappe.contacts.doctype.address.address.address_query',
            filters: {
                'link_doctype': 'Customer',
                'link_name': cur_frm.doc.customer,
                'produktionsstandort': 1
            }
        }
    };
}

function check_navision(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Customer",
            "name": cur_frm.doc.customer
        },
        "callback": function(r) {
            var customer = r.message;
            if (!customer.navision_nr) {
                frappe.msgprint( "Der Kunde besitzt noch keine Navision Nr.", __("Validation") );
                frappe.validated=false;
            }
        }
    });
}
