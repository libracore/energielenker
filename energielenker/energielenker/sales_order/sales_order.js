// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
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
    on_submit: function (frm) {
        if (cur_frm.doc.project) {
            // add fetch payment forecast
            frappe.call({
                method: "energielenker.energielenker.project.project.fetch_payment_schedule",
                args: {
                    "project": cur_frm.doc.project,
                    "sales_order": cur_frm.doc.name,
                    "payment_schedule": cur_frm.doc.payment_schedule
                },
                callback: function (r) {}
            });
        }
    },
    after_cancel: function(frm) {
        if (cur_frm.doc.project) {
            // clear fetched payment forecast
            frappe.call({
                method: "energielenker.energielenker.project.project.clear_payment_schedule",
                args: {
                    "project": cur_frm.doc.project,
                    "sales_order": cur_frm.doc.name
                },
                callback: function (r) {}
            });
        }
    },
    customer: function(frm) {
        shipping_address_query(frm);
    },
    validate: function(frm) {
        check_navision(frm);
        cur_frm.set_value(cur_frm.doc.project, cur_frm.doc.project_clone);
        check_vielfaches(frm);
    },
    project: function(frm) {
        cur_frm.set_value('project_clone', cur_frm.doc.project);
    }
});

frappe.ui.form.on("Sales Order Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
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

function set_item_typ(item) {
    if (item.textposition == 1) {
        item.typ = 'T';
    } else {
        if (item.alternative_position == 1) {
            item.typ = 'A';
        } else {
            if (item.interne_position == 1) {
                item.typ = 'I';
            } else {
                if (item.kalkulationssumme_interner_positionen == 1) {
                    item.typ = 'K';
                } else {
                    item.typ = 'N';
                }
            }
        }
    }
    cur_frm.refresh_field('items');
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

function check_vielfaches(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        if (entry.vielfaches != 0) {
            var rest = entry.qty % entry.vielfaches;
            if (rest != 0) {
                frappe.msgprint( "Die Menge (" + entry.qty + ") der Postition " + entry.idx + " ist kein Vielfaches von " + entry.vielfaches, __("Validation") );
                frappe.validated=false;
            }
        } 
    });
}
