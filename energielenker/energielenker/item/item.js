// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
    refresh: function(frm) {
        set_timestamps(frm);
    },
    validate: function(frm) {
        if (frm.doc.__islocal) {
           cur_frm.set_value("naming_series", 'A-.#######');
        }
        if (cur_frm.doc.supplier_items) {
            var supplier_items = cur_frm.doc.supplier_items;
            var suchliste_list = [];
            for (var i=0; i < supplier_items.length; i++) {
                suchliste_list.push(supplier_items[i].supplier_part_no);
            }
            var suchliste = suchliste_list.join();
            frm.set_value("suchfeld", suchliste);
        }
        
        // set default warehouse in read only field (just as info)
        var default_warehouse_readonly = '';
        if (cur_frm.doc.is_stock_item) {
            if (cur_frm.doc.item_defaults.length > 0) {
                if (cur_frm.doc.item_defaults[0].default_warehouse) {
                    default_warehouse_readonly = cur_frm.doc.item_defaults[0].default_warehouse;
                }
            }
        }
        frm.set_value("default_warehouse_readonly", default_warehouse_readonly);
    },
    item_name: function(frm) {
        if (cur_frm.doc.item_name) {
            cur_frm.set_value("item_purchasing_name", cur_frm.doc.item_name);
        }
    }
});

frappe.ui.form.on('Item Default', {
    navision_konto: function(frm, cdt, cdn) {
        var item_defaults = locals[cdt][cdn];
        if (item_defaults.navision_konto) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Navision Kontenplan",
                    'name': item_defaults.navision_konto
                },
                'async': false,
                'callback': function(response) {
                    var navision_kontonummer = response.message.konto;
                    item_defaults.navision_kontonummer = navision_kontonummer;
                    cur_frm.refresh_field('item_defaults');
                }
            });
        } else {
            item_defaults.navision_kontonummer = '';
            cur_frm.refresh_field('item_defaults');
        }
    }
})

// Change the timeline specification, from "X days ago" to the exact date and time
function set_timestamps(frm){
    setTimeout(function() {
        // mark navbar
        var timestamps = document.getElementsByClassName("frappe-timestamp");
        for (var i = 0; i < timestamps.length; i++) {
            timestamps[i].innerHTML = timestamps[i].title
        }
    }, 1000);
}
