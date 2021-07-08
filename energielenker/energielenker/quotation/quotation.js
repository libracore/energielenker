frappe.ui.form.on('Quotation', {
    party_name: function(frm) {
        if (cur_frm.doc.quotation_to == 'Customer') {
            setTimeout(function(){ shipping_address_query(frm); }, 500);
        }
    }
})

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
