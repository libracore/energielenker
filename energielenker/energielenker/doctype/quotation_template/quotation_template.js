// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quotation Template', {
    refresh: function(frm) {
        set_timestamps(frm);
    },
    tc_name: function(frm) {
        cur_frm.add_fetch('tc_name', 'terms', 'terms');
        //cur_frm.set_value('terms', r.message.terms);
        if (cur_frm.doc.tc_name) {
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    doctype: "Terms and Conditions",
                    name: cur_frm.doc.tc_name
                },
                callback: function (r) {
                    if (r.message) {
                        cur_frm.set_value('terms', r.message.terms);
                    }
                }
            });
        }
    }
});

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

frappe.ui.form.on('Quotation Template Item', {
    item_code: function(frm, dt, dn) {
        var item_code = frappe.model.get_value(dt, dn, 'item_code');
        if (item_code) {
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    doctype: "Item",
                    name: item_code
                },
                callback: function (r) {
                    if (r.message) {
                        var item = r.message;
                        frappe.model.set_value(dt, dn, 'item_name', item.item_name);
                        frappe.model.set_value(dt, dn, 'description', item.description);
                        frappe.model.set_value(dt, dn, 'qty', 1);
                        frappe.model.set_value(dt, dn, 'uom', item.stock_uom);
                    }
                }
            });
            
        } else {
            frappe.model.set_value(dt, dn, 'item_name', '');
            frappe.model.set_value(dt, dn, 'description', '');
            frappe.model.set_value(dt, dn, 'qty', 1);
            frappe.model.set_value(dt, dn, 'uom', '');
        }
    },
    textposition: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        set_item_typ(item);
    },
    alternative_position: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        set_item_typ(item);
    },
    interne_position: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        set_item_typ(item);
    },
    kalkulationssumme_interner_positionen: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        set_item_typ(item);
    }
});

function set_item_typ(item) {
    if (item.textposition == 1) {
        item.typ = 'Txt';
    } else {
        if (item.alternative_position == 1) {
            item.typ = 'Alt.';
        } else {
            if (item.interne_position == 1) {
                item.typ = 'Int. ';
            } else {
                if (item.kalkulationssumme_interner_positionen == 1) {
                    item.typ = 'KS';
                } else {
                    item.typ = 'Norm.';
                }
            }
        }
    }
    cur_frm.refresh_field('items');
}
