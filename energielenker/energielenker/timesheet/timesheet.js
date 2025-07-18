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
       //Check Service Project entries
       check_service_projects(frm);
       
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

frappe.ui.form.on('Timesheet Detail', {
    task(frm, cdt, cdn) {
        //Autoset Expected Time from Task
        set_task_time(frm, cdt, cdn);
    }
});

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

function check_service_projects(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.timesheet.timesheet.check_service_projects',
        'args': {
            'doc': frm.doc
        },
        'callback': function(response) {
            if (response.message) {
                frappe.msgprint(response.message, "Dienstleistungsprojekt")
                frappe.validated=false;
            }
        }
    });
}

function set_task_time(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.task) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Task",
                'name': row.task
            },
            'callback': function(response) {
                if (response.message) {
                    frappe.model.set_value(cdt, cdn, "expected_hours", response.message.expected_time);
                }
            }
        });
    } else {
        frappe.model.set_value(cdt, cdn, "expected_hours", 0);
    }
}
