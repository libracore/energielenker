// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
    validate: function(frm) {
        var supplier_items = cur_frm.doc.supplier_items;
        var suchliste_list = [];
        for (var i=0; i < supplier_items.length; i++) {
            suchliste_list.push(supplier_items[i].supplier_part_no);
        }
        var suchliste = suchliste_list.join();
        frm.set_value("suchfeld", suchliste);
    }
});
