// Copyright (c) 2024, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        set_timestamps(frm);
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {}
                }
            }
        }, 1000);
    }
})

frappe.ui.form.on('Stock Entry Detail', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.item_code) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Item",
                    'name': row.item_code
                },
                'callback': function(response) {
                    var default_warehouse = response.message.default_warehouse_readonly;
                    if (default_warehouse) {
                        frappe.model.set_value(cdt, cdn, "s_warehouse", default_warehouse);
                    }
                }
            });
            if (frm.doc.source_depot) {
                frappe.call({
                    'method': "frappe.client.get",
                    'args': {
                        'doctype': "Depot",
                        'name': frm.doc.source_depot
                    },
                    'callback': function(response) {
                        var depot_warehouse = response.message.to_warehouse;
                        frappe.model.set_value(cdt, cdn, "t_warehouse", depot_warehouse);
                    }
                });
            }
        } else {
            frappe.model.set_value(cdt, cdn, "s_warehouse", "");
            frappe.model.set_value(cdt, cdn, "t_warehouse", "");
        }
    }
})



// Change the timeline specification, from "X days ago" to the exact date and time
function set_timestamps(frm){
    setTimeout(function() {
        // mark navbar
        var timestamps = document.getElementsByClassName("frappe-timestamp");
        for (var i = 0; i < timestamps.length; i++) {
            timestamps[i].innerHTML = timestamps[i].title
        }
    }, 1000);
}
