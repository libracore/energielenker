// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ladepunkt Key API', {
	refresh: function(frm) {
		frm.fields_dict.users.grid.get_field('user').get_query =   
		function() {                                                                      
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		};
	}
});
