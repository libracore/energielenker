frappe.ui.form.on('Address', {
    validate: function(frm) {
        if (cur_frm.doc.plz) {
            cur_frm.set_value('pincode', cur_frm.doc.plz);
        } else {
            cur_frm.set_value('pincode', '');
        },
	if (cur_frm.doc.company_adr_line2) {
	   cur_frm.set_value('address_line2', cur_frm.doc.company_adr_line2);
	} else {
	   cur_frm.set_value('address_line2', '');
	}
    }
})
