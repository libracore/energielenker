// Copyright (c) 2025, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse', {
    refresh: function(frm) {
        frm.add_custom_button(__("Stock transfer"),  function(){
          open_stock_transfer(frm);
        });
    }
});

function open_stock_transfer(frm) {
    var stock_transfer_dialog = new frappe.ui.Dialog({
        'fields': [
            {'fieldname': 'from_warehouse', 'label': "Ausgangslager", 'fieldtype': 'Data', 'read_only': 1, 'default': frm.doc.name },
            {'fieldname': 'to_warehouse', 'label': "Eingangslager", 'fieldtype': 'Link', 'options': 'Warehouse', 'reqd': 1 },
            {'fieldname': 'description', 'label': "Beschreibung", 'fieldtype': 'Data' },
            {'fieldname': 'update_items', 'label': "Standardlager in Artikel anpassen", 'fieldtype': 'Check' }
        ],
        primary_action: function(){
            stock_transfer_dialog.hide();
            var dialog_values = stock_transfer_dialog.get_values()
            if (dialog_values.update_items) {
                var confirm_message = 'Mit dieser Aktion werden alle Artikel von Lager "' + dialog_values.from_warehouse + '" nach "' + dialog_values.to_warehouse + '" umgelagert und bei allen Artikel mit Standardlager "' + dialog_values.from_warehouse + '" wird das neue Standardlager gesetzt, sind Sie sicher?'
            } else {
                var confirm_message = 'Mit dieser Aktion werden alle Artikel von Lager "' + dialog_values.from_warehouse + '" nach "' + dialog_values.to_warehouse + '" umgelagert, sind Sie sicher?'
            }
            frappe.confirm(
                confirm_message,
                function(){
                    // on yes
                    transfer_stock(dialog_values.from_warehouse, dialog_values.to_warehouse, dialog_values.update_items);
                },
                function(){
                    // on no, do nothing
                }
            );
        },
        primary_action_label: __('Relocate')
    });
    stock_transfer_dialog.show();
}

function transfer_stock(from_warehouse, to_warehouse, update_items) {
    frappe.call({
        'method': 'energielenker.energielenker.warehouse.warehouse.transfer_stock',
        'args': {
            'from_warehouse': from_warehouse,
            'to_warehouse': to_warehouse,
            'update_items': update_items
        },
        'callback': function(response) {
            frappe.msgprint("Der Prozess wurde abgeschlossen")
        }
    });
}
