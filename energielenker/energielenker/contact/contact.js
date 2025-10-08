frappe.ui.form.on('Contact', {
    validate: function(frm) {
        cur_frm.set_value('department', cur_frm.doc.department_clone);
        //Restrict length of First and Last Name to 40 Characters
        check_character_amount(frm);
    },
    refresh: function(frm) {
        set_timestamps(frm);
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

function check_character_amount(frm) {
    if (frm.doc.first_name && frm.doc.first_name.length > 40) {
        frappe.msgprint(__("Nachname darf nicht länger als 40 Zeichen sein."));
        frappe.validated = false;
    }
    if (frm.doc.last_name && frm.doc.last_name.length > 40) {
        frappe.msgprint(__("Vorname darf nicht länger als 40 Zeichen sein."));
        frappe.validated = false;
    }
}
