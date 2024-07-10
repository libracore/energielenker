// Copyright (c) 2024, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Bundle', {
    before_save: function(frm) {
        frappe.call({
            'method': 'energielenker.energielenker.product_bundle.product_bundle.mark_items',
            'args': {
                'parent_item': frm.doc.new_item_code,
                'items': frm.doc.items
            }
        });
    }
});

frappe.ui.form.on('Product Bundle Item', {
    before_items_remove(frm, cdt, cdn) {
        var row = locals[cdt][cdn]
        var item_code = row.item_code
        //frappe.call to remove parent from item product bundle field
    }
});
