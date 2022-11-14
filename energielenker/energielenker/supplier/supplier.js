// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier', {
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
