// Copyright (c) 2024, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        //If Stock Entry Type is Manufacture -> Set Serial no to read only and display Button to set Serial no
        display_serial_no_button(frm);
        set_timestamps(frm);
        setTimeout(function(){
        
        if (frm.doc.__islocal) {
            set_sales_order(frm);
        }
        
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {}
                }
            }
        }, 1000);
    },
    work_order: function(frm) {
        set_sales_order(frm);
    },
    before_submit: function(frm) {
        if (frm.doc.work_order && frm.doc.stock_entry_type == "Manufacture") {
            set_item_so_detail(frm);
        }
        check_closed_depot(frm);
    },
    stock_entry_type: function(frm) {
        display_serial_no_button(frm);
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
    },
    fetch_serial_no: function(frm, cdt, cdn) {
        fetch_serial_no(frm, cdt, cdn);
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

function set_sales_order(frm) {
    if (frm.doc.work_order) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Work Order",
                'name': frm.doc.work_order
            },
            'callback': function(response) {
                var sales_order = response.message.sales_order;
                if (sales_order) {
                    cur_frm.set_value("sales_order", sales_order);
                } else {
                    cur_frm.set_value("sales_order", "");
                }
            }
        });
    } else {
        cur_frm.set_value("sales_order", "");
    }
}

function set_item_so_detail(frm) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Work Order",
            'name': frm.doc.work_order
        },
        'callback': function(response) {
            let so_detail = response.message.item_so_detail;
            if (so_detail) {
                for (let i = 0; i < frm.doc.items.length; i++) {
                    if (frm.doc.items[i].t_warehouse) {
                        frappe.model.set_value(frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "item_so_detail", so_detail);
                    }
                }
            }
        }
    });
}

function check_closed_depot(frm) {
    if (frm.doc.source_depot) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Depot",
                filters: { name: frm.doc.source_depot },
                fieldname: "status"
            },
            callback: function(response) {
                if (response.message.status === "Closed") {
                    frappe.msgprint("Kommissionierung ist geschlossen. Bitte vor dem Buchen die Kommissionierung wieder öffnen.", "Achtung");
                    frappe.validated=false;
                }
            }
        });
    }
}

function display_serial_no_button(frm) {
    if (frm.doc.stock_entry_type == "Manufacture") {
        frm.get_field("items").grid.get_docfield("serial_no").read_only = 1;
        frm.get_field("items").grid.get_docfield("fetch_serial_no").hidden = 0;
        frm.get_field("items").grid.refresh();
    } else {
        frm.get_field("items").grid.get_docfield("serial_no").read_only = 0;
        frm.get_field("items").grid.get_docfield("fetch_serial_no").hidden = 1;
        frm.get_field("items").grid.refresh();
    }
}

function fetch_serial_no(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let filters = {'item_code': row.item_code}
    //~ if (row.batch_no) {
        //~ by_item_filters['batch_no'] = row.batch_no;
        //~ by_pos_filters['batch_no'] = row.batch_no;
    //~ }
    let serial_dialog = new frappe.ui.Dialog({
        title: __("Select Serial Numbers"),
        fields: [
            { fieldtype: 'Section Break', label: 'Allgemeine Informationen' },

            {
                fieldname: 'item_code',
                label: 'Item Code',
                fieldtype: 'Data',
                read_only: 1,
                options: 'Customer'
            },
            
            { fieldtype: 'Column Break' },
            
            {
                fieldname: 'warehouse',
                label: 'Warehouse',
                fieldtype: 'Link',
                options: 'Warehouse',
                read_only: 1
            },

            { fieldtype: 'Section Break', label: __('Serial Numbers') },
    
            {
                fieldname: 'add_serial_no',
                label: __('Search Serial Number'),
                fieldtype: 'Link',
                options: 'Serial No',
                'onchange' : function() { set_new_serial_no(serial_dialog, "add_serial_no") },
                'get_query': function() { return { query: "energielenker.energielenker.stock_entry.stock_entry.serial_no_query", filters: filters } }
            },

            { fieldtype: 'Column Break' },

            {
                fieldname: 'selected_serial_no',
                label: __('Selected Serial Numbers'),
                fieldtype: 'Small Text',
            }
        ],
        primary_action: function(){
            serial_dialog.hide();
            set_serial_values(serial_dialog, cdt, cdn);
        },
    primary_action_label: __('Insert')
    });
    serial_dialog.set_value("item_code", row.item_code);
    serial_dialog.set_value("warehouse", row.t_warehouse);
    serial_dialog.show();
}

function set_serial_values(serial_dialog, cdt, cdn) {
    let selected_serial_no = serial_dialog.get_value('selected_serial_no');
    frappe.model.set_value(cdt, cdn, "serial_no", selected_serial_no);
}

function set_new_serial_no(serial_dialog, trigger_field) {
    let value = serial_dialog.get_value(trigger_field)
    if (value) {
        let actual_serial_nos = serial_dialog.get_value('selected_serial_no')
        if (actual_serial_nos && !actual_serial_nos.includes(value)) {
            actual_serial_nos += "\n" + value
            serial_dialog.set_value("selected_serial_no", actual_serial_nos)
        } else if (!actual_serial_nos && !actual_serial_nos.includes(value)) {
            serial_dialog.set_value("selected_serial_no", value)
        }
    serial_dialog.set_value(trigger_field, null)
    }
}
