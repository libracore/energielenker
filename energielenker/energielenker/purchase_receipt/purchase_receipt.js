// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Receipt', {
    validate: function(frm) {
        if (cur_frm.doc.project) {
            copy_project(frm);
        }
    },
    refresh: function(frm) {
        set_timestamps(frm);
    },
    on_submit: function(frm) {
        check_for_shortage(frm);
    }
})

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

function copy_project(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.project = cur_frm.doc.project
    });
    cur_frm.refresh_field('items');
}

function check_for_shortage(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.purchase_invoice.purchase_invoice.check_for_shortage',
        'args': {
            'purchase_receipt': frm.doc.name
        },
        'callback': function(response) {
            if (response.message) {
                frappe.msgprint("Folgende Artikel haben aktuell eine Unterdeckung: " + response.message, "Achtung!")
            }
        }
    });
}
