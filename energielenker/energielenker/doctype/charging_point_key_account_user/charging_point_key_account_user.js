// Copyright (c) 2024, libracore AG and Contributors

frappe.ui.form.on("Charging Point Key Account User", {
	refresh: function(frm) {
		frm.fields_dict.users.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}
		frm.refresh_field("users");
	}
});
