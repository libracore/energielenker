// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lizenzgutschein', {
    refresh: function(frm) {
        set_timestamps(frm);
        frm.add_custom_button(__("Beziehe Lizenzfile von cFos"), function() {
            get_license_items(frm);
        });
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

function get_license_items(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Purchase Order Item',
            filters: [
                ['parent', '=', cur_frm.doc.purchase_order]
            ],
            fields: ['idx', 'item_code', 'item_name', 'qty'],
            parent: 'Purchase Order'
        },
        callback: function(response) {
            get_cfos_lizenz(frm, response.message)
        }
    });
}

function get_cfos_lizenz(frm, po_items) {
    var items = []
    po_items.forEach(function(entry) {
        items.push({
           'idx': entry.idx,
            'item_code': entry.item_code,
            'activation': 1,
            'item_name': entry.item_name,
            'evse_count': entry.qty
        });
    });
    var d = new frappe.ui.Dialog({
        'fields': [
            {'fieldname': 'section_allgemein', 'label': 'Allgemein', 'fieldtype': 'Section Break'},
            {'fieldname': 'order', 'label': 'Bestellreferenz', 'fieldtype': 'Data', 'default': cur_frm.doc.purchase_order, 'read_only': 1},
            {'fieldname': 'test', 'label': 'Teststufe', 'fieldtype': 'Select', 'default': '0', 'options': '0\n1\n2\n3\n4', 'reqd': 1, 'description': '1: Der Benutzer wird authentisiert und der JSON-String der Anfrage wird gelesen.<br>2: Wie 1, zusätzlich werden alle Felder des Requests überprüft und in die Lizenz übernommen.<br>3: Wie 2, zusätzlich wird der Schlüssel zum Signieren mittels des Passworts in keyphrase gelesen.<br>4: Wie 3, zusätzlich wird die Bestellung gespeichert, aber nicht signiert. Diesen Aufruf bitte selten ausführen, da jeweils eine Seriennummer verbraucht wird.<br><b>0: Der Prozess wird vollständig durchlaufen. Die Bestellung wird gespeichert und es wird eine signierte Lizenz zurückgegeben.</b>'},
            {'fieldname': 'section_lizenzen', 'label': 'Lizenzen', 'fieldtype': 'Section Break'},
            {
                label: "Lizenz Details",
                fieldname: "lizenz_items", 
                fieldtype: "Table", 
                cannot_add_rows: true,
                in_place_edit: false, 
                data: items,
                get_data: () => {
                    return items;
                },
                fields: [
                {
                    label: 'Position',
                    fieldtype:'Data',
                    fieldname:"idx",
                    in_list_view: 1,
                    read_only: 1,
                },
                {
                    label: 'Aktivierung',
                    fieldtype:'Check',
                    fieldname:"activation",
                    in_list_view: 1,
                    description: 'Der Wert von Aktivierung kann True oder False sein und entscheidet darüber, ob die Lizenz vor der Benutzung auf dem Kundenrechner aktiviert werden muss.'
                },
                {
                    label: 'Evse Count',
                    fieldtype:'Int',
                    fieldname:"evse_count",
                    in_list_view: 1,
                    description: 'Das Feld Evse Count gibt die Anzahl der Ladepunkte (resp. OCPP-Gateways) an, welche vom Charging Manager unterstützt werden können.'
                },
                {
                    fieldtype:'Link',
                    fieldname:"item_code",
                    options: 'Item',
                    in_list_view: 0,
                    read_only: 1,
                    label: __('Item Code')
                },
                {
                    fieldtype:'Data',
                    fieldname:"item_name",
                    in_list_view: 1,
                    read_only: 1,
                    label: __('Item Name')
                }]
            }
        ],
        primary_action: function(){
            d.hide();
            var values = d.get_values();
            var loop = 1;
            values.lizenz_items.forEach(function(lizenz_item) {
               frappe.call({
                    'method': "energielenker.energielenker.utils.c_fos_schnittstelle.get_license",
                    'args': {
                        'order': values.order,
                        'position': lizenz_item.idx,
                        'test': values.test,
                        'activation': lizenz_item.activation,
                        'evse_count': lizenz_item.evse_count,
                        'voucher': cur_frm.doc.name
                    },
                    'async': true,
                    freeze: true,
                    freeze_message: "Bitte warten, Lizenzen werden bestellt...",
                    'callback': function(response) {
                        if (loop == values.lizenz_items.length) {
                            cur_frm.reload_doc();
                        } else {
                            loop += 1;
                        }
                    }
                });
            });
        },
        primary_action_label: __('Bestellen'),
        title: "Bestellung cFos Lizenzen"
    });
    d.show();
}
