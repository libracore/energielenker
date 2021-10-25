frappe.ui.form.on('Timesheet', {
    validate: function(frm) {
       var time_logs = cur_frm.doc.time_logs;
       time_logs.forEach(function(entry) {
           if (!entry.issue) {
               if (!entry.task) {
                    frappe.msgprint( __("Please set a task or issue"), __("Validation") );
                    frappe.validated=false;
                }
            } 
        });
    }
})
