// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quotation Template', {
    tc_name: function(frm) {
        cur_frm.add_fetch('tc_name', 'terms', 'terms');
        if (cur_frm.doc.tc_name) {
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    doctype: "Terms and Conditions",
                    name: cur_frm.doc.tc_name
                },
                callback: function (r) {
                    if (r.message) {
                        cur_frm.set_value('terms', r.message.terms);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Quotation Template Item', {
    item_code: function(frm, dt, dn) {
        console.log(frappe.model.get_value(dt, dn, 'item_code'));
    }
});
