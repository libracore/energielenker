// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Delivery Note", {
    refresh: function(frm) {
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {}
                }
            }
        }, 1000);
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
    }
});

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
