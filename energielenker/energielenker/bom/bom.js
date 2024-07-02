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
            cur_frm.set_value("transfer_material_against", "Work Order");
        }
        if (frm.doc.sales_order) {
            cur_frm.fields_dict['item'].get_query = function(doc) {
                 return {
                    query: "energielenker.energielenker.bom.bom.sales_order_query",
                    filters: {
                        'sales_order': doc.sales_order
                        }
                 }
            }
        }
    },
    sales_order: function(frm) {
        if (frm.doc.sales_order) {
            autofill_project(frm);
        } else {
            cur_frm.set_value("project", "");
        }
    },
    on_submit: function () {
        cur_frm.set_df_property('sales_order', 'read_only', 1);
    },
    item: function(frm) {
        if (frm.doc.item && frm.doc.sales_order) {
            fetch_items_from_so(frm.doc.item, frm.doc.sales_order);
        }
        check_default_bom(frm);
    },
    is_default: function(frm) {
        check_default_bom(frm);
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

function fetch_items_from_so(bom_item, sales_order) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Sales Order",
            'name': sales_order
        },
        'callback': function(response) {
            var items = response.message.items;
            var part_list_items = response.message.part_list_items;
            var affected_items = []
            for (let i = 0; i < items.length; i++) {
                if (items[i].item_code == bom_item && items[i].with_bom == 1) {
                    affected_items.push(items[i].idx)
                }
            }
            if (affected_items.length > 1) {
                var options = affected_items.join("\n");
                frappe.prompt([
                    {'fieldname': 'item_row', 'fieldtype': 'Select', 'options': options, 'label': 'Item Row', 'reqd': 1}  
                ],
                function(values){
                    set_part_list_items(part_list_items, values.item_row);
                },
                'Select Item Row of in Sales Order',
                'Get Items'
                )
            } else {
                set_part_list_items(part_list_items, affected_items[0]);
            }
        }
    });
}

function set_part_list_items(part_list_items, row) {
    if (part_list_items) {
        for (let i = 0; i < part_list_items.length; i++) {
            if (part_list_items[i].belongs_to == row) {
                var child = cur_frm.add_child('items');
                frappe.model.set_value(child.doctype, child.name, 'item_code', part_list_items[i].item_code);
                frappe.model.set_value(child.doctype, child.name, 'qty', part_list_items[i].qty);
                frappe.model.set_value(child.doctype, child.name, 'uom', part_list_items[i].uom);
                cur_frm.refresh_field("items");
            }
        }
    }
}

function check_default_bom(frm) {
    if (!frm.doc.item) {
        return
    } else {
        if (frm.doc.is_default) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Item",
                    'name': frm.doc.item
                },
                'callback': function(response) {
                    var no_standard_bom = response.message.no_standard_bom;
                    if (no_standard_bom == 1) {
                        frappe.msgprint("Für Artikel " + frm.doc.item + " darf keine Standardstückliste erstellt werden!", "Achtung")
                        cur_frm.set_value("is_default", 0);
                    } else {
                        return
                    }
                }
            });
        }
    }
}
