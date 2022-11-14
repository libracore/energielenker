frappe.ui.form.on('Auto Repeat', {
    validate: function(frm) {
        cur_frm.set_value('notify_by_email', 1);
        if (!cur_frm.doc.recipients) {
            cur_frm.set_value('recipients', frappe.session.user_email);
        }
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
