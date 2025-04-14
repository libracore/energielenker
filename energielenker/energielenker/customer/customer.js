cur_frm.dashboard.add_transactions([
    {
        'label': 'Besuchsbericht',
        'items': [
            'Besuchsbericht'
        ]
    }
]);

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
       set_timestamps(frm);
       frappe.contacts.clear_address_and_contact(cur_frm);
       render_address_and_contact(cur_frm);
       frm.add_custom_button(__("Erstelle Supportrechnung"), function() {
            erstelle_supportrechnung(frm);
        });
        
        frm.set_query('manual_billing_address', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.name
                }
            };
        });
        
        frm.set_query('billing_contact', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.name
                }
            };
        });
        if (frm.doc.__islocal) {
            cur_frm.set_df_property('set_manual_billing_address', 'hidden', 1);
        }
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
        
        // calc and set sha256 hash
        var value;
        if (cur_frm.doc.website) {
            value = cur_frm.doc.website;
        } else {
            if(cur_frm.doc.keine_domain_vorhanden) {
                value = cur_frm.doc.email_id;
            } else {
                frappe.msgprint( __('Bitte hinterlegen Sie eine Website oder markieren Sie die Checkbox "Keine Domain vorhanden"'), __("Validation") );
                frappe.validated=false;
            }
        }
        
        frappe.call({
            "method": "energielenker.energielenker.utils.customer_hash.get_customer_hash",
            "args": {
                'value': value
            },
            "async": true,
            "callback": function(r) {
                cur_frm.set_value("hash", r.message);
            }
        });
        //Validate Navision Customer No.
        validate_navision_no(frm);
    },
    manual_billing_address: function(frm) {
        if (frm.doc.manual_billing_address) {
            frappe.call({
                method: 'frappe.contacts.doctype.address.address.get_address_display',
                args: {
                    address_dict: frm.doc.manual_billing_address
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('manual_billing_address_display', r.message);
                    }
                }
            });
        } else {
           frm.set_value('manual_billing_address_display', null); 
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
        } else {
           frm.set_value('billing_contact_display', null); 
        }
    },
    set_manual_billing_address: function(frm) {
        if (!frm.doc.set_manual_billing_address) {
            frm.set_value('manual_billing_address', null);
            frm.set_value('manual_billing_address_display', null);
            frm.set_value('billing_contact', null);
            frm.set_value('billing_contact_display', null);
        }
    }
})

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

function render_address_and_contact(frm) {
    if (!frm.doc.__islocal) {
    // render address
        if(cur_frm.fields_dict['address_html'] && "addr_list" in cur_frm.doc.__onload) {
            $(cur_frm.fields_dict['address_html'].wrapper)
                .html(frappe.render_template("energielenker_address_list",
                    cur_frm.doc.__onload))
                .find(".btn-address").on("click", function() {
                    frappe.new_doc("Address");
                });
        }

        //~ // render contact
        if(cur_frm.fields_dict['contact_html'] && "contact_list" in cur_frm.doc.__onload) {
            $(cur_frm.fields_dict['contact_html'].wrapper)
                .html(frappe.render_template("kontakt_template",
                    cur_frm.doc.__onload))
                .find(".btn-contact").on("click", function() {
                    frappe.new_doc("Contact");
                }
            );
        }
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
    frappe.call({
        "method": "energielenker.energielenker.customer.customer.get_adressen_zum_verrechnen",
        "args": {
                'customer': frm.doc.name
            },
        "async": true,
        "callback": function(res) {
            var adressen = res.message;
            var fieldlist = [
                {'fieldname': 'von', 'fieldtype': 'Date', 'label': 'Von', 'reqd': 1},
                {'fieldname': 'bis', 'fieldtype': 'Date', 'label': 'Bis', 'reqd': 1}
            ];
            if (!cur_frm.doc.ist_support_kunde) {
                fieldlist.push({'fieldname': 'adresse', 'fieldtype': 'Link', 'label': 'Adresse (Produktionsstandort)', 'reqd': 1, 'options': 'Address',
                    'get_query': function() {
                        return { 'filters': {
                                'name': ['in', adressen]
                            }
                        };
                    }
                });
            }
            frappe.prompt(
                fieldlist,
                function(values){
                    frappe.call({
                        "method": "energielenker.energielenker.customer.customer.erstelle_supportrechnung",
                        "args": {
                            'customer': frm.doc.name,
                            'von': values.von,
                            'bis': values.bis,
                            'adresse': values.adresse,
                            'support_kunde': cur_frm.doc.ist_support_kunde
                        },
                        "async": true,
                        "callback": function(r) {
                            frappe.dom.freeze(__("Bitte warten, die Rechnung wird erstellt..."));
                            var jobname = r.message;
                            if (jobname) {
                                let calc_refresher = setInterval(calc_refresher_handler, 3000, jobname);
                                function calc_refresher_handler(jobname) {
                                    frappe.call({
                                    'method': "energielenker.energielenker.customer.customer.check_supportrechnung_job",
                                        'args': {
                                            'jobname': jobname
                                        },
                                        'callback': function(res) {
                                            if (res.message == 'refresh') {
                                                clearInterval(calc_refresher);
                                                cur_frm.reload_doc();
                                                frappe.dom.unfreeze();
                                                frappe.db.get_value("Customer", cur_frm.doc.name, 'supportrechnung_sinv').then(function(res){
                                                    if (res.message.supportrechnung_sinv != 'no sinv') {
                                                        frappe.set_route("Form", "Sales Invoice", res.message.supportrechnung_sinv)
                                                    } else {
                                                        frappe.msgprint("Keine Daten zum verrechnen gefunden.");
                                                    }
                                                })
                                            }
                                        }
                                    });
                                }
                            }
                        }
                    });
                },
                'Erstelle Supportrechnung',
                'Erstellen'
            )
        }
    });
}

function validate_navision_no(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.customer.customer.check_navision_no',
        'args': {
            'doc_name': frm.doc.name,
            'navision_no': frm.doc.navision_nr
        },
        'callback': function(response) {
            if (response.message) {
                frappe.msgprint("Diese Navision Kundennummer wird bereits in Kunde " + response.message + " verwendet")
                frappe.validated = false
            }
        }
    });
}
