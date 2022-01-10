frappe.ui.form.on('Customer', {
    refresh: function(frm) {
       frappe.contacts.clear_address_and_contact(cur_frm);
       render_address_and_contact(cur_frm);
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


