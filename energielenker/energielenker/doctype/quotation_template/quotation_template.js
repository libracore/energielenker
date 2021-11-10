// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quotation Template', {
//
});

frappe.ui.form.on('Quotation Item', {
    item_code: function(frm) {
        cur_frm.add_fetch('item_code', 'item_name', 'item_name');
        cur_frm.add_fetch('item_code', 'description', 'description');
        cur_frm.add_fetch('item_code', 'stock_uom', 'uom');
    }
});

frappe.ui.form.on('Payment Schedule', {
    item_code: function(frm) {
        cur_frm.add_fetch('payment_terms_template', 'payment_term', 'payment_term');
        cur_frm.add_fetch('payment_terms_template', 'description', 'description');
    }
});
