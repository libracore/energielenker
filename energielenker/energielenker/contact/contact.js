frappe.ui.form.on('Contact', {
    validate: function(frm) {
        cur_frm.set_value('department', cur_frm.doc.department_clone);
    }
})
