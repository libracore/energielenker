// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lead", {
    status: function(frm) {
        if (cur_frm.doc.status == 'Do Not Contact') {
            cur_frm.set_value("do_not_contact", 1);
        }
    },
    do_not_contact: function(frm) {
        if (cur_frm.doc.do_not_contact) {
            cur_frm.set_value("status", "Do Not Contact");
        }
    }
});
