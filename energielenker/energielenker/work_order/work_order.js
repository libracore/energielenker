// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            if (frm.doc.bom_no) {
                set_values(frm);
            }
        }
    },
    project: function(frm) {
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

function set_values(frm) {
    frappe.call({
        'method': "energielenker.energielenker.work_order.work_order.get_values",
        'args': {
            'bom': frm.doc.bom_no
        },
        'callback': function(response) {
            var item = response.message[0].item;
            var sales_order = response.message[0].sales_order;
            var project = response.message[0].project;
            var fg_warehouse = response.message[0].default_warehouse_readonly;
            cur_frm.set_value("production_item", item);
            cur_frm.set_value("sales_order", sales_order);
            cur_frm.set_value("project", project);
            cur_frm.set_value("fg_warehouse", fg_warehouse);
        }
    });
}
