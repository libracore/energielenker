// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        cur_frm.fields_dict['kontaktperson_lieferant'].get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: {
                    "link_name": frm.doc.supplier_name
                }
            };
        };
    }
});
