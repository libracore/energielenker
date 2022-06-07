frappe.ui.form.on('Address', {
    validate: function(frm) {
        if (cur_frm.doc.plz) {
            cur_frm.set_value('pincode', cur_frm.doc.plz);
        } else {
            cur_frm.set_value('pincode', '');
        }
        if (cur_frm.doc.company_adr_line2) {
           cur_frm.set_value('address_line2', cur_frm.doc.company_adr_line2);
        } else {
           cur_frm.set_value('address_line2', '');
        }
    },
    refresh: function(frm) {
        cur_frm.fields_dict['support_wird_verrechnet_ueber'].get_query = function(doc) {
             return {
                 filters: {
                     "ist_support_kunde": 1
                 }
             }
        }
    }
})
