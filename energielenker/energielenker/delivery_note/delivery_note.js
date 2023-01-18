// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

var so_return;

frappe.ui.form.on("Delivery Note", {
	onload: function(frm) {
		// If you create an DN from the project, it will make sure to take the address set on the project than the customer primary address.
		var last_route = frappe.route_history.slice(-2, -1)[0];
		if (last_route) {
			if (last_route[1] == "Project") {
				frappe.call({
					'method': "frappe.client.get",
					'args': {
						'doctype': "Project",
						'name': last_route[2]
					},
					'callback': function(response) {
						var project_address = response.message.shipping_address;
						console.log("PROJECT", project_address)
						if (project_address) {
							setTimeout(() => {
								cur_frm.set_value('shipping_address_name', project_address);
							}, 1500);
						}
					}
				});
			}
		}
	},
	
	refresh: function(frm) {
		set_timestamps(frm);
		setTimeout(() => {
			frm.remove_custom_button('Sales Return', 'Create');
			frm.page.add_inner_button('Sales Return', function() { 
				cur_frm.cscript.make_sales_return()
				so_return = "Return";
				}, 'Create')
			
		}, 10);
		
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {}
                }
            }
        }, 1000);
        
        if (frm.doc.freigabe_berechnung_ab) {
			var nowdate = frappe.datetime.get_today();
			if (frm.doc.freigabe_berechnung_ab == nowdate) {
				cur_frm.set_value('zur_berechnung_freigegeben', 1);
			} else {
				cur_frm.set_value('zur_berechnung_freigegeben', 0);
			}
			
		}
		        
    },
	
	before_save(frm) {
		if (so_return == "Return"){
			frappe.confirm('<strong> Der entsprechende Kundenauftrag wurde wiedereröffnet.</strong> <br> Möchten Sie, dass der Auftrag geschlossen bleibt? ',
				() => {
					// action to perform if Continue is selected
					cur_frm.set_value('so_return', 1);
					so_return = "Leave SO Close";
				},() => {
					// action to perform if No is selected
					console.log("leave open")
					so_return = "Leave SO Open";
				}
			)
		}
	},
	
	on_submit: function(frm) {
		if (cur_frm.doc.so_return){
			update_so_status(frm);
		}
	},
    
    customer: function(frm) {
        shipping_address_query(frm);
    },
    
    project: function(frm) {
       if (frm.doc.__islocal && cur_frm.doc.project) {
           frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    cur_frm.set_value('customer', project.customer);
                }
            });
        }
    },
    
    shipping_address_name: function(frm) {
        if (cur_frm.doc.shipping_address_name) {
            fetch_kontakt_aus_lieferadresse(frm);
        } else {
            cur_frm.set_value("kontakt_aus_lieferadresse", '');
            cur_frm.set_value("kontaktname_aus_lieferadresse", '');
        }
    },
    
    validate: function(frm) {
        if (cur_frm.doc.shipping_address_name) {
            fetch_kontakt_aus_lieferadresse(frm);
        } else {
            cur_frm.set_value("kontakt_aus_lieferadresse", '');
            cur_frm.set_value("kontaktname_aus_lieferadresse", '');
        }
        
        if (cur_frm.doc.ignore_pricing_rule) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry){
                entry.pricing_rules = null;
            });
        }
    },
    
    deliver_to(frm) {
	    //set default customer and clearing the fields when re-selecting
	    cur_frm.set_value('customer', "Dummy-Kunde (nicht deaktivieren!)");
	    
	    if (frm.doc.deliver_to == "Customer") {
	        cur_frm.set_value('customer', "");
	        cur_frm.set_value('supplier', "");
	        cur_frm.set_value('lead', "");
	    } else if (frm.doc.deliver_to == "Lead") {
	        cur_frm.set_value('supplier', "");
	        cur_frm.set_value('tax_id', "");
	    } else if (frm.doc.deliver_to == "Supplier") {
	        cur_frm.set_value('lead', "");
	        cur_frm.set_value('tax_id', "");
	    }
	    
	    // Saving without customer address must not be possible.
	    if (frm.doc.deliver_to == "Customer") {
			frm.set_df_property("customer_address", "reqd", 1);
			frm.set_df_property("new_customer_address", "reqd", 0);
	    } else {
			frm.set_df_property("customer_address", "reqd", 0);
			frm.set_df_property("new_customer_address", "reqd", 1);
	    } 
	    
	    cur_frm.set_value('new_address_name', "");
	    cur_frm.set_value('new_contact_name', "");
	    cur_frm.set_value('new_customer_address', "");
	    cur_frm.set_value('shipping_address_name', "");
	    cur_frm.set_value('contact_person', "");
	    cur_frm.set_value('customer_address', "");
	    
	    //Set new tax_id if exist for the supplier
	    cur_frm.add_fetch('supplier','tax_id','tax_id');
	},
	lead(frm) {
	    set_new_address_and_contact_filter(frm, "Lead");
	    if (frm.doc.lead) {
			frappe.call({
				'method': "frappe.client.get_list",
				'args':{
					'doctype': "Lead",
					'filters': [
						["name","IN", [cur_frm.doc.lead]]
					],
					'fields': ["company_name"]
				},
				'callback': function (response) {
					var lead_name = response.message;
					cur_frm.set_value('title', lead_name[0].company_name);
				}
			});
		}    

	},
	supplier(frm) {
	    set_new_address_and_contact_filter(frm, "Supplier");
	    if (frm.doc.supplier) {
			cur_frm.set_value('title', cur_frm.doc.supplier);
		}
	},
	//Setting the new values into the original fields to be displayed and fetch in the print-format
	new_address_name(frm) {
	    if (frm.doc.new_address_name) {
            cur_frm.set_value('shipping_address_name', frm.doc.new_address_name);
        }
	},
	new_contact_name (frm) {
	    if (frm.doc.new_contact_name) {
            cur_frm.set_value('contact_person', frm.doc.new_contact_name);
        }
	},
	new_customer_address (frm) {
	    if (frm.doc.new_customer_address) {
            cur_frm.set_value('customer_address', frm.doc.new_customer_address);
        }
	}
});

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

frappe.ui.form.on("Delivery Note Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Notey Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

function check_text_and_or_alternativ(item) {
    if (item.textposition == 1 || item.alternative_position == 1) {
        item.discount_percentage = 100.00;
        item.discount_amount = item.price_list_rate;
        item.rate = 0.00;
        cur_frm.refresh_field('items');
    } else {
        item.discount_percentage = 0.00;
        item.discount_amount = 0.00;
        item.rate = item.price_list_rate;
        cur_frm.refresh_field('items');
    }
}

function set_item_typ(item) {
    if (item.textposition == 1) {
        item.typ = 'Txt';
    } else {
        if (item.alternative_position == 1) {
            item.typ = 'Alt.';
        } else {
            if (item.interne_position == 1) {
                item.typ = 'Int. ';
            } else {
                if (item.kalkulationssumme_interner_positionen == 1) {
                    item.typ = 'KS';
                } else {
                    item.typ = 'Norm.';
                }
            }
        }
    }
    cur_frm.refresh_field('items');
}

function shipping_address_query(frm) {
    cur_frm.fields_dict['shipping_address_name'].get_query = function(doc) {
        return {
            query: 'frappe.contacts.doctype.address.address.address_query',
            filters: {
                'link_doctype': 'Customer',
                'link_name': cur_frm.doc.customer,
                'produktionsstandort': 1
            }
        }
    };
}

function fetch_kontakt_aus_lieferadresse(frm) {
    frappe.call({
        'method': "energielenker.energielenker.delivery_note.delivery_note.fetch_kontakt_aus_lieferadresse",
        'args': {
            'lieferadresse': cur_frm.doc.shipping_address_name
        },
        'callback': function(response) {
            if (response.message) {
                var kontakt = response.message;
                if (kontakt != 'keiner') {
                    cur_frm.set_value("kontakt_aus_lieferadresse", kontakt.link);
                    cur_frm.set_value("kontaktname_aus_lieferadresse", kontakt.name);
                }
            }
        }
    });
}

function update_so_status(frm) {
	cur_frm.doc.items.forEach(function(entry) {	
		if (entry.against_sales_order) {
			frappe.call({
				method: "erpnext.selling.doctype.sales_order.sales_order.update_status",
				args: {status: 'Closed', name: entry.against_sales_order}
			});
		}
	});
}

function set_new_address_and_contact_filter(frm, filter) {
    var deliver_to = "";
    
    if (filter == "Supplier") {
        deliver_to = frm.doc.supplier;
    } else {
        deliver_to = frm.doc.lead;
    }
    
    frm.set_query("new_address_name", function() {
		return {
			filters: {
				link_name: deliver_to
			}                       
		}
	});
	
	frm.set_query("new_contact_name", function() {
		return {
			filters: {
				link_name: deliver_to
			}                       
		}
	});
}
