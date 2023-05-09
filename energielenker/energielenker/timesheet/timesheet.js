frappe.ui.form.on('Timesheet', {
    onload: function(frm) {
        //task number is automatically stored in the time recording.
        var last_route = frappe.route_history.slice(-2, -1)[0];
        if (last_route) {
            if (last_route[1] == "Task") {
                
                var child = frm.add_child("time_logs");;
                frappe.model.set_value(child.doctype, child.name, 'task', last_route[2]);
                refresh_field("time_logs")
            }
        }
    },

    validate: function(frm) {
       var time_logs = cur_frm.doc.time_logs;
       time_logs.forEach(function(entry) {
           if (!entry.issue) {
               if (!entry.task) {
                    frappe.msgprint( __(`Bitte stellen Sie eine Aufgabe oder ein Ticket, Reihe ${entry.idx}`),  __("Validation") );
                    frappe.validated=false;
                }
            } 
        });
    },
    refresh: function(frm) {
        set_timestamps(frm);
        var addrowbutton = document.getElementsByClassName("grid-add-row")[0];
        addrowbutton.innerHTML = "Reihe hinzufügen";

    }
})

// Change the timeline specification, from "X days ago" to the exact date and time
function set_timestamps(frm){
    setTimeout(function() {
        // mark navbar
        var timestamps = document.getElementsByClassName("frappe-timestamp");
        for (var i = 0; i < timestamps.length; i++) {
            timestamps[i].innerHTML = timestamps[i].title;
        }
    }, 1000);
}
