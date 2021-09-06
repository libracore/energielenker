// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
       setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
					filters: {'is_sales_item': 1}
                }
            }
        }, 1000);
    },
    customer: function(frm) {
        shipping_address_query(frm);
    },
    validate: function(frm) {
        check_navision(frm);
    }
});

frappe.ui.form.on("Sales Invoice Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
});

frappe.ui.form.on("Sales Invoice Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
});

function check_text_and_or_alternativ(item) {
    if (item.textposition == 1 || item.alternative_position == 1) {
        item.discount_percentage = 100.00;
        cur_frm.refresh_field('items');
    } else {
        item.discount_percentage = 0.00;
        item.discount_amount = 0.00;
        cur_frm.refresh_field('items');
    }
}

function shipping_address_query(frm) {
    cur_frm.fields_dict['shipping_address_name'].get_query = function(doc) {
        return {
            query: 'frappe.contacts.doctype.address.address.address_query',
            filters: {
                'link_doctype': 'Customer',
                'link_name': cur_frm.doc.customer,
                'produktionsstandort': 1
            }
        }
    };
}

function check_navision(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Customer",
            "name": cur_frm.doc.customer
        },
        "callback": function(r) {
            var customer = r.message;
            if (!customer.navision_nr) {
                frappe.msgprint( "Der Kunde besitzt noch keine Navision Nr.", __("Validation") );
                frappe.validated=false;
            }
        }
    });
}
