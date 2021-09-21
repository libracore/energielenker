// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Order', {
	drop_ship_check: function(frm) {
	    cur_frm.add_fetch('customer_shipping','customer_name','customer_shipping_name');
	},
	customer_address: function(frm) {
	    if (cur_frm.doc.customer_address) {
	        cur_frm.set_value('shipping_address', cur_frm.doc.customer_address);
	    } else {
	        cur_frm.set_value('shipping_address', '');
	    }
	},
    validate: function(frm) {
        check_vielfaches(frm);
    }
})

function check_vielfaches(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        if (entry.vielfaches != 0) {
            var rest = entry.qty % entry.vielfaches;
            if (rest != 0) {
                frappe.msgprint( "Die Menge (" + entry.qty + ") der Postition " + entry.idx + " ist kein Vielfaches von " + entry.vielfaches, __("Validation") );
                frappe.validated=false;
            }
        } 
    });
}
