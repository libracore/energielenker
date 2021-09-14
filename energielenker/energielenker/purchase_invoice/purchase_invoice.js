// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
    validate: function(frm) {
        if (cur_frm.doc.project) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry) {
                if (!entry.project) {
                    entry.project = cur_frm.doc.project;
                } 
            });
        }
        return
    }
})
