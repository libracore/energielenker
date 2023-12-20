// Copyright (c) 2023, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Price", {
	after_save: function (frm) {
		if (cur_frm.doc.price_list_rate)  {
			if(frm.doc.price_list_rate != frm.doc.previous_price_list_rate) {
				update_bom_item_cost(frm);
			} 
		}
	},

});

function update_bom_item_cost(frm) {
    frappe.call({
        'method': "energielenker.energielenker.item_price.item_price.update_bom_item_cost",
        'args': {
			'name': frm.doc.name,
			'item_code': frm.doc.item_code,
            'rate': frm.doc.price_list_rate,
            'rm_cost_as_per': "Price List",
            'price_list': frm.doc.price_list,
            
        },
    });
}
