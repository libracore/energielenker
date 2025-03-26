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
        console.log("hallo");
        frm.get_field("items").grid.get_docfield("serial_no").read_only = 1;
        frm.fields_dict["items"].grid.get_field("fetch_serial_no").hidden = 0;
        frm.get_field("items").grid.refresh();
    }
}
