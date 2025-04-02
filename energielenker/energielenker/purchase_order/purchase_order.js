// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

cur_frm.dashboard.add_transactions([
    {
        'label': 'Lizenzen',
        'items': [
            'Lizenzgutschein'
        ]
    }
]);

frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        set_timestamps(frm)
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {'is_purchase_item': 1}
                }
            }
        }, 1000);
        
        if ((cur_frm.doc.supplier == 'cFos Software GmbH')&&(cur_frm.doc.docstatus==1)) {
            frm.add_custom_button(__("Erzeuge Lizenzgutschein"), function() {
                erzeuge_lizenzgutschein(frm);
            });
        }
        
    },
    drop_ship_check: function(frm) {
        cur_frm.add_fetch('customer_shipping','customer_name','customer_shipping_name');
    },
    supplier_ship_check: function(frm) {
        cur_frm.add_fetch('supplier_to_supplier','supplier_name','supplier_to_supplier_name');
    },
    customer_address: function(frm) {
        if (cur_frm.doc.customer_address) {
            cur_frm.set_value('shipping_address', cur_frm.doc.customer_address);
        } else {
            cur_frm.set_value('shipping_address', '');
        }
    },
    /*fill in address in field shipping_address*/
    supplier_to_supplier_address: function(frm) {
        if (cur_frm.doc.supplier_to_supplier_address) {
            cur_frm.set_value('shipping_address', cur_frm.doc.supplier_to_supplier_address);
        } else {
            cur_frm.set_value('shipping_address', '');
        }
    },
    /*show only address of that supplier*/
    supplier_to_supplier: function(frm) {
        filter_additional_contact(frm, "supplier_to_supplier_contact", cur_frm.doc.supplier_to_supplier);
        cur_frm.fields_dict['supplier_to_supplier_address'].get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];          
            return {
                filters: {
                    "link_name": frm.doc.supplier_to_supplier
                }
            }
        }
    },
    customer_shipping: function(frm) {
        filter_additional_contact(frm, "customer_contact", cur_frm.doc.customer_shipping);
        cur_frm.fields_dict['customer_address'].get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];          
            return {
                filters: {
                    "link_name": frm.doc.customer_shipping
                }
            }
        }
    },
    validate: function(frm) {
        if (!frm.doc.drop_ship_check) {
            check_vielfaches(frm);
        }
        check_deactivated_items(frm);
        if (cur_frm.doc.project) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    copy_project_und_cost_center(frm, project.name, project.cost_center);
                }
            });
        } else {
            copy_project_und_cost_center(frm, null, null);
        }
        // if items come from a SO then display the so_name in the doc and viceversa
        if ( cur_frm.doc.items[0].sales_order ) {
            var so_ref = cur_frm.doc.items[0].sales_order;
            set_po_reference(frm, so_ref);
        }
    }
})

frappe.ui.form.on('Purchase Order Item', {
    item_code(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            check_deactivation(row.item_code);
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

function filter_additional_contact(frm, field, filter) {
    frm.set_query(field, function() {
        return {
            filters: {
                link_name: filter
            }
        }
    }) 
}

function check_vielfaches(frm) {
    var items = cur_frm.doc.items;
    // check if vielfaches is defined
    items.forEach(function(entry) {
        if (!entry.vielfaches) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Item",
                    'name': entry.item_code
                },
                'async': false,
                'callback': function(response) {
                    var item = response.message;
                    entry.vielfaches = item.einkauf_vielfaches;
                }
            });
        } 
    });
    cur_frm.refresh_field('items');
    validate_vielfaches(frm);
}

function validate_vielfaches(frm) {
    var items = cur_frm.doc.items;
    // validate vielfaches
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

function copy_project_und_cost_center(frm, project, cost_center) {
    var items = cur_frm.doc.items;
    if (!cost_center) {
        frappe.call({
            'method': "energielenker.energielenker.purchase_order.purchase_order.get_default_cost_center",
            'args': {
                'user': frappe.session.user
            },
            'async': true,
            'callback': function(r) {
                console.log(r.message)
                items.forEach(function(entry) {
                    entry.project = project;
                    if ((!entry.cost_center)||(entry.cost_center == 'Main - S')) {
                        entry.cost_center = r.message;
                    }
                });
                cur_frm.refresh_field('items');
            }
        });
    } else {
        items.forEach(function(entry) {
            entry.project = project;
            entry.cost_center = cost_center
        });
        cur_frm.refresh_field('items');
    }
}

function erzeuge_lizenzgutschein(frm) {
    var items = []
    frappe.call({
        'method': "energielenker.energielenker.doctype.lizenzgutschein.lizenzgutschein.get_evse_count_qty",
        'callback': function(response) {
            var uom_evse_count = response.message;
            cur_frm.doc.items.forEach(function(entry) {
                for (var i = 1; i <= entry.qty; i++) {
                    if (i > 1) {
                        var idx_string = String(entry.idx) + "." + String(i - 1);
                    } else {
                        var idx_string = String(entry.idx);
                    }
                    items.push({
                       'idx': idx_string,
                        'item_code': entry.item_code,
                        'activation': 1,
                        'item_name': entry.item_name,
                        'evse_count': uom_evse_count[entry.uom],
                        'positions_id': entry.name
                    });
                }
            });
            var d = new frappe.ui.Dialog({
                'fields': [
                    {'fieldname': 'section_allgemein', 'label': 'Allgemein', 'fieldtype': 'Section Break'},
                    {'fieldname': 'order', 'label': 'Bestellreferenz', 'fieldtype': 'Data', 'default': cur_frm.doc.name, 'read_only': 1},
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
                        },
                        {
                            fieldtype:'Data',
                            fieldname:"positions_id",
                            in_list_view: 0,
                            read_only: 1,
                            label: __('Positions ID')
                        }]
                    }
                ],
                primary_action: function(){
                    d.hide();
                    var values = d.get_values();
                    var loop = 1;
                    values.lizenz_items.forEach(function(lizenz_item) {
                       frappe.call({
                            'method': "energielenker.energielenker.utils.c_fos_schnittstelle.create_lizenzgutschein",
                            'args': {
                                'purchase_order': values.order,
                                'positions_nummer': lizenz_item.idx,
                                'test': values.test,
                                'aktivierung': lizenz_item.activation,
                                'evse_count': lizenz_item.evse_count,
                                'position_id': lizenz_item.positions_id
                            },
                            'async': true,
                            freeze: true,
                            freeze_message: "Bitte warten, Lizenzgutscheine werden erzeugt...",
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
                primary_action_label: __('Erzeugen'),
                title: "Erzeugung Lizenzgutscheine"
            });
            d.show();
        }
    });
}

function set_po_reference(frm, so_ref) {
    setTimeout(function(){
        console.log("po_ref two", cur_frm.doc.name)
        frappe.call({
            'method': "frappe.client.set_value",
            'args':{
             'doctype': "Sales Order",
              'name': so_ref,
              "fieldname": {
                    "lieferantenauftrag": cur_frm.doc.name
                },
            },
        });
    }, 1000);
    cur_frm.set_value("sales_order", so_ref);
}
