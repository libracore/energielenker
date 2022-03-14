frappe.ui.form.on('Customer', {
    refresh: function(frm) {
       frappe.contacts.clear_address_and_contact(cur_frm);
       render_address_and_contact(cur_frm);
       frm.add_custom_button(__("Erstelle Supportrechnung"), function() {
            erstelle_supportrechnung(frm);
        });
    },
    customer_primary_contact: function(frm) {
        fetch_email(frm);
    },
    adresse_verknupfen: function(frm) {
        adresse_verknupfen(frm);
    },
    kontakt_verknupfen: function(frm) {
        kontakt_verknupfen(frm);
    },
    validate: function(frm) {
        cur_frm.set_value("adresse_lookup", "");
        cur_frm.set_value("kontakt_lookup", "");
    }
})

function render_address_and_contact(frm) {
    // render address
    if(cur_frm.fields_dict['address_html'] && "addr_list" in cur_frm.doc.__onload) {
        $(cur_frm.fields_dict['address_html'].wrapper)
            .html(frappe.render_template("energielenker_address_list",
                cur_frm.doc.__onload))
            .find(".btn-address").on("click", function() {
                frappe.new_doc("Address");
            });
    }

    // render contact
    if(cur_frm.fields_dict['contact_html'] && "contact_list" in cur_frm.doc.__onload) {
        $(cur_frm.fields_dict['contact_html'].wrapper)
            .html(frappe.render_template("contact_list",
                cur_frm.doc.__onload))
            .find(".btn-contact").on("click", function() {
                frappe.new_doc("Contact");
            }
        );
    }
}

function adresse_verknupfen(frm) {
    if (cur_frm.doc.adresse_lookup) {
        frappe.call({
            method: "energielenker.energielenker.customer.customer.adresse_verknupfen",
            args: {
                "address": cur_frm.doc.adresse_lookup,
                "customer": cur_frm.doc.name
            },
            callback: function (r) {
                cur_frm.reload_doc();
            }
        });
    }
}

function kontakt_verknupfen(frm) {
    if (cur_frm.doc.kontakt_lookup) {
        frappe.call({
            method: "energielenker.energielenker.customer.customer.kontakt_verknupfen",
            args: {
                "contact": cur_frm.doc.kontakt_lookup,
                "customer": cur_frm.doc.name
            },
            callback: function (r) {
                cur_frm.reload_doc();
            }
        });
    }
}

function erstelle_supportrechnung(frm) {
    frappe.prompt([
        {'fieldname': 'von', 'fieldtype': 'Date', 'label': 'Von', 'reqd': 1},
        {'fieldname': 'bis', 'fieldtype': 'Date', 'label': 'Bis', 'reqd': 1},
        {'fieldname': 'adresse', 'fieldtype': 'Link', 'label': 'Adresse (Produktionsstandort)', 'reqd': 1, 'options': 'Address',
            'get_query': function() {
                return { 'filters': { 'link_doctype': "Customer", "link_name": frm.doc.name } };
            }
        }
    ],
    function(values){
        frappe.call({
            "method": "energielenker.energielenker.customer.customer.erstelle_supportrechnung",
            "args": {
                    'customer': frm.doc.name,
                    'von': values.von,
                    'bis': values.bis,
                    'adresse': values.adresse
                },
            "async": true,
            "freeze": true,
            "freeze_message": "Bitte warten, die Rechnung wird erstellt...",
            "callback": function(r) {
                if (r.message != 'no sinv') {
                    frappe.set_route("Form", "Sales Invoice", r.message)
                } else {
                    frappe.msgprint("Keine Daten zum verrechnen gefunden.");
                }
            }
        });
    },
    'Erstelle Supportrechnung',
    'Erstellen'
    )
}
