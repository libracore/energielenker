// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            if (frm.doc.bom_no) {
                set_bom_values(frm);
            }
        } else {
            check_not_transferred_items(frm);
        }
    }
});

function set_bom_values(frm) {
    frappe.call({
        'method': "energielenker.energielenker.work_order.work_order.get_bom_values",
        'args': {
            'bom': frm.doc.bom_no
        },
        'callback': function(response) {
            var item = response.message[0].item;
            var sales_order = response.message[0].sales_order;
            var project = response.message[0].project;
            var fg_warehouse = response.message[0].default_warehouse_readonly;
            var wip_warehouse = response.message[0].depot_warehouse;
            cur_frm.set_value("production_item", item);
            setTimeout(function(){
                cur_frm.set_value("project", project);
                cur_frm.set_value("fg_warehouse", fg_warehouse);
                cur_frm.set_value("wip_warehouse", wip_warehouse);
                cur_frm.set_value("sales_order", sales_order);
            }, 1000);
        }
    });
}

function check_not_transferred_items(frm) {
    if (frm.doc.status == "In Process" || frm.doc.status == "Stopped" || frm.doc.status == "Completed") {
        let affected_items = []
        for (let i = 0; i < frm.doc.required_items.length; i++) {
            if (frm.doc.required_items[i].required_qty > frm.doc.required_items[i].transferred_qty) {
                affected_items.push(frm.doc.required_items[i].item_code);
            }
        }
        if (affected_items.length > 0) {
            cur_frm.dashboard.add_comment("Achtung folgende Artikel wurden noch nicht komplett bezogen: " + affected_items.join(', '), 'red', true);
        }
    }
}

