frappe.ui.form.on('Auto Repeat', {
    validate: function(frm) {
        cur_frm.set_value('notify_by_email', 1);
        cur_frm.set_value('recipients', frappe.session.user_email);
    }
})
