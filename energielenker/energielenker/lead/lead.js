// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lead", {
	
	refresh: function(frm) {
		set_timestamps(frm)
	},
    status: function(frm) {
        if (cur_frm.doc.status == 'Do Not Contact') {
            cur_frm.set_value("do_not_contact", 1);
        }
    },
    do_not_contact: function(frm) {
        if (cur_frm.doc.do_not_contact) {
            cur_frm.set_value("status", "Do Not Contact");
        }
    },
    validate: function(frm) {
        // calc and set sha256 hash
        var value;
        if (cur_frm.doc.website) {
            value = cur_frm.doc.website;
        } else {
            if(cur_frm.doc.keine_domain_vorhanden) {
                value = cur_frm.doc.email_id;
            } else {
                frappe.msgprint( __('Bitte hinterlegen Sie eine Website oder markieren Sie die Checkbox "Keine Domain vorhanden"'), __("Validation") );
                frappe.validated=false;
            }
        }
        
        frappe.call({
            "method": "energielenker.energielenker.utils.customer_hash.get_customer_hash",
            "args": {
                'value': value
            },
            "async": true,
            "callback": function(r) {
                cur_frm.set_value("hash", r.message);
            }
        });
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
