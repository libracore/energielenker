// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
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
        
        if (cur_frm.doc.customer) {
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
            });
        }
        
        // hack für server seitig erstelle rechnungen: neu setzen mwst template damit die mwst Tabelle befüllt wird.
        if ((cur_frm.doc.taxes_and_charges)&&(cur_frm.doc.taxes.length < 1)) {
            var taxes = cur_frm.doc.taxes_and_charges;
            cur_frm.set_value("taxes_and_charges", "");
            cur_frm.set_value("taxes_and_charges", taxes);
        }
        
        cost_center_query(frm);
    },
    customer: function(frm) {
        shipping_address_query(frm);
    },
    validate: function(frm) {
        check_navision(frm);
        check_vielfaches(frm);
        try {
            cur_frm.set_value("apply_discount_on", "Net Total");
        } catch (err) {}
    },
    project: function(frm) {
       fetch_customer_an_cost_center(frm);
    },
    onload: function(frm) {
        if (cur_frm.doc.items) {
            if (cur_frm.doc.items[0].delivery_note) {
                if (cur_frm.doc.docstatus == 0) {
                    cur_frm.set_value("is_pos", 1);
                }
            }
        }
        fetch_customer_an_cost_center(frm);
    },
    navision_konto: function(frm) {
        if (!cur_frm.doc.navision_konto||cur_frm.doc.navision_konto == '') {
            cur_frm.set_value('navision_kontonummer', '');
        }
    }
});

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
                        cur_frm.set_value('cost_center', project_type.cost_center);
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
