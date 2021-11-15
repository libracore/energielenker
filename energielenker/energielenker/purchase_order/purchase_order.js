// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Order', {
	refresh: function(frm) {
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {'is_purchase_item': 1}
                }
            }
        }, 1000);
    },
    drop_ship_check: function(frm) {
	    cur_frm.add_fetch('customer_shipping','customer_name','customer_shipping_name');
	},
	supplier_ship_check: function(frm) {
	    cur_frm.add_fetch('supplier_to_supplier','supplier_name','supplier_to_supplier_name');
	},
	customer_address: function(frm) {
	    if (cur_frm.doc.customer_address) {
	        cur_frm.set_value('shipping_address', cur_frm.doc.customer_address);
	    } else {
	        cur_frm.set_value('shipping_address', '');
	    }
	},
	/*fill in address in field shipping_address*/
	supplier_to_supplier_address: function(frm) {
	    if (cur_frm.doc.supplier_to_supplier_address) {
	        cur_frm.set_value('shipping_address', cur_frm.doc.supplier_to_supplier_address);
	    } else {
	        cur_frm.set_value('shipping_address', '');
	    }
	},
	/*show only address of that supplier*/
	supplier_to_supplier: function(frm) {
   	    cur_frm.fields_dict['supplier_to_supplier_address'].get_query = function(doc, cdt, cdn) {
	        var d = locals[cdt][cdn];          
        	    return {
             		filters: {
              	     		"link_name": frm.doc.supplier_to_supplier
			}                       
            	    }
	    }
	},
	customer_shipping: function(frm) {
   	    cur_frm.fields_dict['customer_address'].get_query = function(doc, cdt, cdn) {
	        var d = locals[cdt][cdn];          
        	    return {
             		filters: {
              	     		"link_name": frm.doc.customer_shipping
			}                       
            	    }
	    }
	},
    validate: function(frm) {
        check_vielfaches(frm);
        if (cur_frm.doc.project) {
            copy_project(frm);
        }
    }
})

function check_vielfaches(frm) {
    var items = cur_frm.doc.items;
    // check if vielfaches is defined
    items.forEach(function(entry) {
        if (!entry.vielfaches) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Item",
                    'name': entry.item_code
                },
                'async': false,
                'callback': function(response) {
                    var item = response.message;
                    entry.vielfaches = item.einkauf_vielfaches;
                }
            });
        } 
    });
    cur_frm.refresh_field('items');
    validate_vielfaches(frm);
}

function validate_vielfaches(frm) {
    var items = cur_frm.doc.items;
    // validate vielfaches
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

function copy_project(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.project = cur_frm.doc.project
    });
    cur_frm.refresh_field('items');
}
