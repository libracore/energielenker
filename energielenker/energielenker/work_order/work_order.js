// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order', {
    refresh: function() {
        console.log(cur_frm.doc.project);
        cur_frm.fields_dict['sales_order'].get_query = function() {
            if (cur_frm.doc.project) {
                 return {
                     filters: {
                         "project_clone": cur_frm.doc.project
                     }
                 }
            }
        };
    }
});
