frappe.ui.form.on('Address', {
    validate: function(frm) {
        if (cur_frm.doc.plz) {
            cur_frm.set_value('pincode', cur_frm.doc.plz);
        } else {
            cur_frm.set_value('pincode', '');
        }
    }
})
