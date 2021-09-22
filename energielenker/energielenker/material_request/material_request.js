frappe.ui.form.on('Material Request', {
    validate: function(frm) {
        if (cur_frm.doc.project) {
            copy_project(frm);
        }
    }
})

function copy_project(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.project = cur_frm.doc.project
    });
    cur_frm.refresh_field('items');
}
