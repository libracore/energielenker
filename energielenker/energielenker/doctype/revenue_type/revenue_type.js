// Copyright (c) 2025, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revenue Type', {
    //Handle Checkbox "For fixed Items"
    for_hardware: function(frm) {
        set_fixed_check(frm);
        if (frm.doc.for_hardware && frm.doc.for_support) {
            cur_frm.set_value("for_support", 0);
        }
    },
    for_support: function(frm) {
        set_fixed_check(frm);
        if (frm.doc.for_hardware && frm.doc.for_support) {
            cur_frm.set_value("for_hardware", 0);
        }
    }
});

function set_fixed_check(frm) {
    if (frm.doc.for_hardware || frm.doc.for_support) {
        cur_frm.set_value("for_fixed_items", 0);
    } else {
        cur_frm.set_value("for_fixed_items", 1);
    }
}
