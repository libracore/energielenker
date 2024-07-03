frappe.ui.form.on('Quotation', {

    refresh: function(frm) {
	   // remove button "Duplicate" in Menu
        if($("[data-label='" + __("Duplicate") + "']").length > 0) {
			$("[data-label='" + __("Duplicate") + "']")[0].parentElement.remove();
        } 

		cur_frm.page.add_menu_item(__("Duplicate"), function() {
			frappe.confirm('Sollen die Preise mit der gültigen Preisliste überschrieben werden?',
				() => {
					// action to perform if Yes is selected
					cur_frm.set_value('dont_copy_current_rate', 1);
					frm.copy_doc();
					setTimeout(function(){ 
						for (var i = 0; i < cur_frm.doc.items.length; i++) {
							(function(index) {
								frappe.call({
									method: 'frappe.client.get_value',
									args: {
										doctype: 'Item Price',
										filters: {
											"item_code": cur_frm.doc.items[index].item_code,
											"selling": 1
										},
										fieldname: ['price_list_rate']
									},
									callback: function(response) {
										if (response.message) {
											var currentSellingRate = response.message.price_list_rate;
											console.log('Current Selling Rate:', currentSellingRate);
											frappe.model.set_value(cur_frm.doc.items[index].doctype, cur_frm.doc.items[index].name, 'rate', currentSellingRate);
										} else {
											console.log('Item price not found.');
										}
									}
								});
							})(i);
						}
						
						//For future duplications
						cur_frm.set_value('dont_copy_current_rate', 0);
					}, 2000);
					
				}, () => {
					// action to perform if No is selected
					frm.copy_doc();
					cur_frm.set_value('dont_copy_current_rate', 0);
					
				}
			)
		});
	    
       set_timestamps(frm)
       setTimeout(function(){ 
            cur_frm.fields_dict.items.grid.get_field('item_code').get_query = function(doc) {                                                                      
                    return {
                        query: "energielenker.energielenker.item.item.item_query",
                        filters: {'is_sales_item': 1}
                    }
            }
        }, 1000);
        
        if (cur_frm.doc.docstatus == 1 ) {
			if( frappe.datetime.get_diff(cur_frm.doc.valid_till, frappe.datetime.get_today()) <= 0) {
				cur_frm.add_custom_button(__('Sales Order'),
				cur_frm.cscript['Make Expired Sales Order'], __('Create'));
			}
		}
        
        if (frm.doc.__islocal && cur_frm.doc.project) {
           frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    cur_frm.set_value('party_name', project.customer);
                }
            });
        }    
        
        if (frm.doc.__islocal) {
            frm.add_custom_button(__("Get Quotation Template"), function() {
                get_quotation_template(frm);
            });
        }
        
        cost_center_query(frm);
        set_row_options(frm);
    },
    party_name: function(frm) {
        if (cur_frm.doc.quotation_to == 'Customer') {
            setTimeout(function(){ shipping_address_query(frm); }, 500);
        }
    },
    validate: function(frm) {
        check_vielfaches(frm);
        calculate_part_list_prices(frm);
        
        if (cur_frm.doc.part_list_items) {
            for (i=0; i < cur_frm.doc.part_list_items.length; i++) {
                if (cur_frm.doc.part_list_items[i].qty && cur_frm.doc.part_list_items[i].rate) {
                    frappe.model.set_value(cur_frm.doc.part_list_items[i].doctype, cur_frm.doc.part_list_items[i].name, "amount", cur_frm.doc.part_list_items[i].qty * cur_frm.doc.part_list_items[i].rate);
                } else {
                    frappe.model.set_value(cur_frm.doc.part_list_items[i].doctype, cur_frm.doc.part_list_items[i].name, "amount", 0);
                }
            }
        }
    },
    wahrscheindlichkeit: function(frm) {
        if (cur_frm.doc.wahrscheindlichkeit > 100) {
            cur_frm.set_value('wahrscheindlichkeit', 100);
            frappe.msgprint( "Die Wahrscheindlichkeit kann nicht über 100% liegen", __("Validation") );
        }
    }
})

frappe.ui.form.on('Quotation Item', {
    with_bom(frm, cdt, cdn) {
        set_row_options(frm);
    },
    item_code(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
           frappe.db.get_value("Item", row.item_code, "part_list_item").then( (value) => {
               if (value.message.part_list_item == 1) {
                    frappe.model.set_value(cdt, cdn, 'with_bom', 1);
                }
            });
        }
    }
});

frappe.ui.form.on('Quotation Part List Item', {
    qty(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        } else {
            frappe.model.set_value(cdt, cdn, "amount", 0);
        }
    },
    rate(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        } else {
            frappe.model.set_value(cdt, cdn, "amount", 0);
        }
    },
    part_list_items_add(frm) {
    set_row_options(frm);
    }
});

// Allow Expired Quotation to be transferable to Sales Order
cur_frm.cscript['Make Expired Sales Order'] = function() {
    console.log("click make expired so")
	frappe.model.open_mapped_doc({
		method: "energielenker.energielenker.quotation.quotation._make_sales_order",
		args: {
		    'source_name': cur_frm.doc.name,
		},
		frm: cur_frm
	})
}

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

frappe.ui.form.on("Quotation Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "with_bom", function(frm, cdt, cdn) {
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
                'link_doctype': cur_frm.doc.quotation_to,
                'link_name': cur_frm.doc.party_name,
                'produktionsstandort': 1
            }
        }
    };
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
                    entry.vielfaches = item.verkauf_vielfaches;
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

function get_quotation_template(frm) {
    frappe.prompt([
        {'fieldname': 'tpl', 'fieldtype': 'Link', 'options': 'Quotation Template', 'label': 'Quotation Template', 'reqd': 1}  
    ],
    function(values){
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Quotation Template",
                'name': values.tpl
            },
            'callback': function(response) {
                var template = response.message;
                var tbl = cur_frm.doc.items || [];
                var i = tbl.length;
                while (i--)
                {
                    cur_frm.get_field("items").grid.grid_rows[i].remove();
                }
                cur_frm.refresh();
                template.items.forEach(function(entry) {
                    if (entry.item_code != null) {
                        var child = cur_frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', entry.item_code);
                        frappe.model.set_value(child.doctype, child.name, 'description', entry.description);
                        frappe.model.set_value(child.doctype, child.name, 'qty', entry.qty);
                        frappe.model.set_value(child.doctype, child.name, 'textposition', entry.textposition);
                        frappe.model.set_value(child.doctype, child.name, 'alternative_position', entry.alternative_position);
                        frappe.model.set_value(child.doctype, child.name, 'interne_position', entry.interne_position);
                        frappe.model.set_value(child.doctype, child.name, 'kalkulationssumme_interner_positionen', entry.kalkulationssumme_interner_positionen);
                        frappe.model.set_value(child.doctype, child.name, 'typ', entry.typ);
                        cur_frm.refresh_field('items');
                         if (entry.textposition == 1 || entry.alternative_position == 1) {
                            
                            setTimeout(function(){
                                frappe.model.set_value(child.doctype, child.name, "discount_percentage", 100.00);
                                frappe.model.set_value(child.doctype, child.name, "rate", 0.00);
                                cur_frm.refresh_field('items');
                            }, 1000);
                        }
                    } 
                });
                cur_frm.set_value('ansprechpartner', template.ansprechpartner);
                cur_frm.refresh_field('ansprechpartner');
                cur_frm.set_value('payment_terms_template', template.payment_terms_template);
                cur_frm.refresh_field('payment_terms_template');
                cur_frm.set_value('terms', template.terms);
                cur_frm.refresh_field('terms');
            }
        });
    },
    'Quotation Template',
    'Get'
    )
}

function set_row_options(frm) {
    if (frm.doc.part_list_items) {
        var options = [];
        for (i=0; i < frm.doc.items.length; i++) {
            if (frm.doc.items[i].with_bom) {
                options.push(frm.doc.items[i].idx);
            }
        }
        var options_string = options.join("\n");
        cur_frm.get_field("part_list_items").grid.docfields[4].options = options_string;
        cur_frm.refresh_field("part_list_items");
    }
}

function calculate_part_list_prices(frm) {
    for (i=0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].with_bom) {
            var amount = 0
            for (j=0; j < frm.doc.part_list_items.length; j++) {
                if (frm.doc.part_list_items[j].belongs_to == i + 1) {
                    amount += frm.doc.part_list_items[j].amount
                }
            }
            frappe.model.set_value(frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "rate", amount);
        }
    }
}
