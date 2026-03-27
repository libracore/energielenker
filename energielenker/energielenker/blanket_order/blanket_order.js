// Copyright (c) 2026, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Blanket Order', {
    validate: function(frm) {
        check_uom(frm);
    },
    change_to_date: function(frm) {
        update_to_date(frm);
    }
})

function update_to_date(frm) {
    frappe.prompt([
        {'fieldname': 'new_to_date', 'fieldtype': 'Date', 'label': 'New Date', 'reqd': 1}  
    ],
    function(values){
        frappe.call({
            'method': 'energielenker.energielenker.blanket_order.blanket_order.update_to_date',
            'args': {
                'blanket_order': frm.doc.name,
                'new_date': values['new_to_date']
            },
            'callback': function(response) {
                cur_frm.reload_doc();
            }
        });
    },
    'Neues Bis-Datum setzten',
    'Los'
    );
}

function check_uom(frm) {
    if (frm.doc.additional_discount && frm.doc.additional_discount.length > 0) {
        for (let i = 0; i < frm.doc.additional_discount.length; i++) {
            if (!frm.doc.additional_discount[i].uom && frm.doc.additional_discount[i].item_code == "A-0001701") {
                frappe.validated = false;
                frappe.msgprint("Bitte Einheit für Ladepunktkeys angeben!");
            }
        }
    }
}
