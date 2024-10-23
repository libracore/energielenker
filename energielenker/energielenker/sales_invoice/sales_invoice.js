// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt
frappe.ui.form.on('Sales Invoice Item', {
    items_add(frm, cdt, cdn) {

    }
});
frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {

       set_timestamps(frm);
       setTimeout(function(){ 
            try {
                cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
                    function() {                                                                      
                    return {
                            query: "energielenker.energielenker.item.item.item_query",
                            filters: {'is_sales_item': 1}
                        }
                    }
            } catch (err) {}
        }, 1000);
        
        //po_no number is automatically set if the sinv is duplicated.
        if(frm.doc.docstatus!=0) {
            // remove button "Duplicate" in Menu
            if($("[data-label='Duplicate']").length > 0) {
                $("[data-label='Duplicate']")[0].parentElement.remove();
            }

            cur_frm.page.add_menu_item(__("Duplicate"), function() {
                frm.copy_doc();
                var last_route = frappe.route_history[0][2];
                if (last_route) {
                    console.log("route", last_route)

                    frappe.call({
                        'method': "frappe.client.get",
                        'args': {
                            'doctype': "Sales Invoice",
                            'name': last_route
                        },
                        'callback': function(response) {
                            var sinv = response.message;
                            cur_frm.set_value('po_no', sinv.po_no);
                        }
                    });
                }
          });
        }
        
        if (cur_frm.doc.customer) {
            filter_contact(frm);
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Customer",
                    'name': cur_frm.doc.customer
                },
                'async': false,
                'callback': function(response) {
                    var customer = response.message;
                    cur_frm.fields_dict['navision_konto'].get_query = function(doc) {
                         return {
                             filters: {
                                 "ic": customer.navision_internal_ic,
                                 "deaktiviert": 0
                             }
                         }
                    }
                    
                    if (cur_frm.doc.docstatus == 0) {
                        if (!cur_frm.doc.ignoriere_automatische_zahlungsbedingung_zuordnung) {
                            // Kundenspezifische Zahlungsbedingung hat vorrang
                            if (customer.payment_terms) {
                                if (cur_frm.doc.payment_terms_template != customer.payment_terms) {
                                    cur_frm.set_value("payment_schedule", []);
                                    cur_frm.set_value("payment_terms_template", "");
                                    cur_frm.set_value("payment_terms_template", customer.payment_terms);
                                }
                            } else {
                                // prüfung der Zahlungsbedingung
                                if ((customer.navision_internal_ic)&&(cur_frm.doc.payment_terms_template != '100% 14 Tage')) {
                                    cur_frm.set_value("payment_schedule", []);
                                    cur_frm.set_value("payment_terms_template", "");
                                    cur_frm.set_value("payment_terms_template", "100% 14 Tage");
                                }
                                if ((!customer.navision_internal_ic)&&(cur_frm.doc.payment_terms_template != '100% 21 Tage')) {
                                    cur_frm.set_value("payment_schedule", []);
                                    cur_frm.set_value("payment_terms_template", "");
                                    cur_frm.set_value("payment_terms_template", "100% 21 Tage");
                                }
                            }
                        }
                    } 
                }
            });
        }
        
        // hack für server seitig erstelle rechnungen: neu setzen mwst template damit die mwst Tabelle befüllt wird.
        if ((cur_frm.doc.taxes_and_charges)&&(cur_frm.doc.taxes.length < 1)) {
            var taxes = cur_frm.doc.taxes_and_charges;
            cur_frm.set_value("taxes_and_charges", "");
            cur_frm.set_value("taxes_and_charges", taxes);
        }
        
        cost_center_query(frm);
        
        if (cur_frm.doc.navision_deviation) {
            frappe.msgprint("Achtung, folgende Positionen besitzen eine abweichende Navision Kontonummer:<br>" + cur_frm.doc.navision_deviation, "Abweichende Navision Kontonummern");
        }
        
        if (cur_frm.doc.__islocal) {
            check_foreign_customers(frm.doc.customer);
        }
        
        frm.set_query('billing_address_name', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.customer
                }
            };
        });
        
        frm.set_query('billing_contact', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.customer
                }
            };
        });
    },
    before_save(frm) {
		set_zusatzgeschaft(frm);
	    get_customer_inovice_note(frm);
	},
    customer: function(frm) {
        shipping_address_query(frm);
        check_foreign_customers(frm.doc.customer);
        remove_billing_address(frm);
    },
    validate: function(frm) {
        check_navision(frm);
        check_vielfaches(frm);
   	    set_leistungsdatum(frm);
   	    check_stundensatz(frm);
        
        try {
            cur_frm.set_value("apply_discount_on", "Net Total");
        } catch (err) {}
        
        if (cur_frm.doc.ignore_pricing_rule) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry){
                entry.pricing_rules = null;
            });
        }
    },
    before_submit: function(frm) {
    },
    project: function(frm) {
       fetch_customer_an_cost_center(frm);
    },
    onload: function(frm) {
        fetch_customer_an_cost_center(frm);
    },
    navision_konto: function(frm) {
        if (!cur_frm.doc.navision_konto||cur_frm.doc.navision_konto == '') {
            cur_frm.set_value('navision_kontonummer', '');
        }
    },
    contact_person_two: function(frm) {
        frappe.call({
            'method': "frappe.client.get_list",
            'args':{
                'doctype': "Contact",
                'filters': [
                    ["name","IN", [frm.doc.contact_person_two]]
                 ],
                'fields': ["salutation", "first_name", "last_name", "email_id" ,"phone"]
            },
            'callback': function (response) {
                var res = response.message;
                var info;
                var full_name = res[0].first_name + " " + res[0].last_name;
                
                if ( res[0].salutation ) {
                    full_name = `${res[0].salutation} ${full_name}`;
                }
                
                if ( res[0].email_id && res[0].phone) {
                    info = `${full_name} <br> Email: ${res[0].email_id} <br> Phone: ${res[0].phone}`;
                    cur_frm.set_value("contact_display_two", info);
                } else if ( res[0].email_id ) {
                    info = `${full_name} <br> Email: ${res[0].email_id}`;
                    cur_frm.set_value("contact_display_two", info);
                } else if ( res[0].phone ) {
                    info = `${full_name} <br> Phone: ${res[0].phone}`;
                    cur_frm.set_value("contact_display_two", info);
                } else {
                    cur_frm.set_value("contact_display_two", full_name);
                }
            }
        });
    },
    billing_address_name: function(frm) {
        if (frm.doc.billing_address_name) {
            frappe.call({
                method: 'frappe.contacts.doctype.address.address.get_address_display',
                args: {
                    address_dict: frm.doc.billing_address_name
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('billing_address', r.message);
                    }
                }
            });
        }
    },
    billing_contact: function(frm) {
        if (frm.doc.billing_contact) {
            frappe.call({
                method: 'frappe.contacts.doctype.contact.contact.get_contact_details',
                args: {
                    contact: frm.doc.billing_contact
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('billing_contact_display', r.message.contact_display);
                    }
                }
            });
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

function set_zusatzgeschaft(frm) {
	if (frm.doc.items[0].sales_order) {
		frappe.call({
			"method": "frappe.client.get",
			"args": {
				"doctype": "Sales Order",
				'name': frm.doc.items[0].sales_order
			},
			"callback": function(response) {
				var zusatzgeschaft = response.message.zusatzgeschaft;
				if (zusatzgeschaft === 1) {
					cur_frm.set_value("zusatzgeschaft", 1);
					frm.fields_dict['zusatzgeschaft'].refresh();
				} else {
					cur_frm.set_value("zusatzgeschaft", 0);
					frm.fields_dict['zusatzgeschaft'].refresh();
				}
			}
		});
	}
}

function filter_contact(frm) {
    frm.set_query("contact_person_two" , function() {
        return {
            filters: {
                link_name: frm.doc.customer
            }
        }
    }) 
}

frappe.ui.form.on("Sales Invoice Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Invoice Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Invoice Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Sales Invoice Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Sales Invoice Item", "with_bom", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

function fetch_customer_an_cost_center(frm) {
    if (cur_frm.doc.project) {
       frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Project",
                'name': cur_frm.doc.project
            },
            'callback': function(response) {
                var project = response.message;
                if (!cur_frm.doc.customer) {
                    cur_frm.set_value('customer', project.customer);
                }
                frappe.call({
                    'method': "frappe.client.get",
                    'args': {
                        'doctype': "Project Type",
                        'name': project.project_type
                    },
                    'callback': function(response) {
                        var project_type = response.message;
                        if (!cur_frm.doc.cost_center) {
                            cur_frm.set_value('cost_center', project_type.cost_center);
                        }
                    }
                });
            }
        });
    }
}

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
                if (item.with_bom == 1) {
                    item.typ = 'St.';
                } else {
                    if (item.kalkulationssumme_interner_positionen == 1) {
                        item.typ = 'KS';
                    } else {
                        item.typ = 'Norm.';
                    }
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

function check_navision(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Customer",
            "name": cur_frm.doc.customer
        },
        "callback": function(r) {
            var customer = r.message;
            if (!customer.navision_nr) {
                frappe.msgprint( "Der Kunde besitzt noch keine Navision Nr.", __("Validation") );
                frappe.validated=false;
            }
        }
    });
}

function check_vielfaches(frm) {
    if (cur_frm.doc.billing_type == 'Rechnung') {
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
                    entry.vielfaches = item.verkauf_vielfaches;
                }
            });
        } 
    });
    cur_frm.refresh_field('items');
    validate_vielfaches(frm);
    }
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

function cost_center_query(frm) {
    cur_frm.fields_dict['cost_center'].get_query = function(doc) {
        return {
            filters: {
                'auswahl_unterbinden': 0
            }
        }
    };
}

function get_customer_inovice_note(frm) {
    frappe.call({
        'method': "frappe.client.get_list",
        'args':{
     	    'doctype': "Customer",
         	'filters': [
         	    ["name","IN", [cur_frm.doc.customer]]
         	],
            'fields': ["leave_invoice_note", "invoice_note_box"]
        },
        'callback': function (r) {
            var customer = r.message[0];
            
            if (customer.leave_invoice_note === 1) {
                frappe.msgprint({
                    title: __('Dieser Kunde hat einen Rechnungsvermerk hinterlassen:'),
                    indicator: 'red',
                    message: __(` &nbsp;  &nbsp; ${ customer.invoice_note_box }`)
                });
            }
        }
    });
}

function set_leistungsdatum(frm) {
	var dnote = frm.doc.items[0].delivery_note;
	if (dnote) {
		frappe.call({
			"method": "frappe.client.get",
			"args": {
				"doctype": "Delivery Note",
				"name": dnote
			},
			"callback": function(r) {
				var response = r.message;
				
				cur_frm.set_value("leistungsdatum", response.posting_date);
			}
		});
	}	
}

function check_stundensatz(frm) {
    var items = cur_frm.doc.items;
    var billed_hours = 0;
    // Check Stundensatz nur direkte Weiterberechnung
    items.forEach(function(entry) {
        if (entry.item_code === "A-0001882") {
			billed_hours = billed_hours + entry.qty;
        } 
    });
    
    if (billed_hours > 0) {
		frappe.call({
			'method': 'frappe.client.get_value',
			'args': {
				'doctype': 'Project',
				'filters': { 'name': cur_frm.doc.project },
				'fieldname': 'noch_nicht_abgerechnete_stunden'
			},
			'callback': function(response) {
				var booked_hours = response.message.noch_nicht_abgerechnete_stunden;
				console.log("booked_hours", booked_hours);
				console.log("billed_hours", billed_hours);
				console.log("check_stundensatz", booked_hours - billed_hours);
				
				frappe.call({
					'method': 'frappe.client.set_value',
					'args': {
						'doctype': 'Project',
						'name': cur_frm.doc.project,
						'fieldname': {
							'noch_nicht_abgerechnete_stunden': booked_hours - billed_hours
						},
					}
				});
			}
		});
	}
}

function remove_billing_address(frm) {
    cur_frm.set_value("billing_address_name", null);
    cur_frm.set_value("billing_address", null);
    cur_frm.set_value("billing_contact", null);
    cur_frm.set_value("billing_contact_display", null);
}

