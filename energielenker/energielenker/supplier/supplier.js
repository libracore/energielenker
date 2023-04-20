// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier', {
	onload: function(frm) {
		let currentDate = frappe.datetime.get_today();

		if (frm.doc.creation.split(" ")[0] === currentDate && frm.doc.selbstauskunft_einholen === 0) {
			frappe.msgprint({
				title: __('Hinweis'),
				indicator: 'red',
				message: __('Selbstauskunft einholen')
			});
			cur_frm.set_value('selbstauskunft_einholen', 1);
		}
    },
    refresh: function(frm) {
        set_timestamps(frm);
        cur_frm.fields_dict['kontaktperson_lieferant'].get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: {
                    "link_name": frm.doc.supplier_name
                }
            };
        };
    }
});

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
