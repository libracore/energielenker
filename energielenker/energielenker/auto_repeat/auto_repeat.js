frappe.ui.form.on('Auto Repeat', {
    validate: function(frm) {
        cur_frm.set_value('notify_by_email', 1);
        if (!cur_frm.doc.recipients) {
            cur_frm.set_value('recipients', frappe.session.user_email);
        }
    }
})
