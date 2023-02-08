frappe.ui.form.on('Cost Center', {
	after_save: function(frm) {
		if (frm.doc.navision_shortcutdimensionscode_1) {
			frappe.call({
				method: "erpnext.accounts.utils.update_number_field",
				args: {
					doctype_name: frm.doc.doctype,
					name: frm.doc.name,
					field_name: "navision_shortcutdimensionscode_1",
					number_value: frm.doc.navision_shortcutdimensionscode_1,
					company: frm.doc.company
				},
				callback: function(r) {
					if(r.message) {
						frappe.set_route("Form", "Cost Center", r.message);
					} else {
						frm.set_value("cost_center_number", frm.doc.navision_shortcutdimensionscode_1,);
					}
				}
			});
		}
	},
})
