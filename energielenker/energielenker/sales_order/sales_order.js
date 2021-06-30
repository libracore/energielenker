// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
    on_submit: function (frm) {
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
    },
    after_cancel: function(frm) {
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
});
