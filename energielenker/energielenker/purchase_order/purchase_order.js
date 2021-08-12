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
	}
})
