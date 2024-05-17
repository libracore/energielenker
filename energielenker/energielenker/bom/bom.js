frappe.ui.form.on('BOM', {
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
        
        if (frm.doc.__islocal) {
            cur_frm.set_value("with_operations", 1);
            cur_frm.set_value("transfer_material_against", "Work Order");
            var child = cur_frm.add_child('operations');
        }
    },
    sales_order: function(frm) {
        if (frm.doc.sales_order) {
            autofill_project(frm);
        } else {
            cur_frm.set_value("project", "");
        }
    },
    setup: function(frm) {
        if (frm.doc.sales_order) {
            fetch_items_from_so(frm.doc.sales_order);
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

function autofill_project(frm) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Sales Order",
            'name': frm.doc.sales_order
        },
        'callback': function(response) {
            var project = response.message.project;
            if (project) {
                cur_frm.set_value("project", project);
            } else {
                cur_frm.set_value("project", "");
            }
        }
    });
}

function fetch_items_from_so(sales_order) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Sales Order",
            'name': sales_order
        },
        'callback': function(response) {
            var items = response.message.part_list_items;
            if (items) {
                for (let i = 0; i < items.length; i++) {
                    var child = cur_frm.add_child('items');
                    frappe.model.set_value(child.doctype, child.name, 'item_code', items[i].item_code);
                    //~ frappe.model.set_value(child.doctype, child.name, 'qty', items[i].qty);
                    //~ frappe.model.set_value(child.doctype, child.name, 'uom', items[i].uom);
                    //~ setTimeout(function(child, rate) {
                        //~ frappe.model.set_value(child.doctype, child.name, 'rate', rate);
                    //~ }, 1000, child, items[i].rate);
                }
            }
        }
    });
}
