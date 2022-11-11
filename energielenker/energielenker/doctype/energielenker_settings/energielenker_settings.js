// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('energielenker Settings', {
    refresh: function(frm) {
        set_timestamps(frm);
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
