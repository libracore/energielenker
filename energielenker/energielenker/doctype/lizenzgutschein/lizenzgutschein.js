// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lizenzgutschein', {
    refresh: function(frm) {
        set_timestamps(frm);
        if (cur_frm.doc.lizenzen.length < 1) {
            frm.add_custom_button(__("Beziehe Lizenzfile manuell"), function() {
                beziehe_lizenz_manuell(frm);
            });
        }
        if (cur_frm.doc.purchase_order){              
			frappe.call({
				method: 'frappe.client.get_value',
                args: {
					doctype: 'Purchase Order',
                    filters: { name: cur_frm.doc.purchase_order },
                    fieldname: 'sales_order'
                },
                callback: function(response) {
					var sales_order = response.message.sales_order;
                    if (sales_order) {
						cur_frm.set_value("kundenauftrag", sales_order);
					}
				}
			})
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

function beziehe_lizenz_manuell(frm) {
    frappe.call({
        'method': "energielenker.energielenker.utils.c_fos_schnittstelle.get_license",
        'args': {
            'order': cur_frm.doc.purchase_order,
            'position': cur_frm.doc.positions_nummer,
            'test': cur_frm.doc.test,
            'activation': cur_frm.doc.aktivierung,
            'evse_count': cur_frm.doc.evse_count,
            'voucher': cur_frm.doc.name,
            'position_id': cur_frm.doc.positions_nummer
        },
        'async': true,
        freeze: true,
        freeze_message: "Bitte warten, Lizenz wird bestellt...",
        'callback': function(response) {
            cur_frm.reload_doc();
        }
    });
}
