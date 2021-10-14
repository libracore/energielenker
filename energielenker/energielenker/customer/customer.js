frappe.ui.form.on('Customer', {
    refresh: function(frm) {
       frappe.contacts.clear_address_and_contact(cur_frm);
       render_address_and_contact(cur_frm);
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
