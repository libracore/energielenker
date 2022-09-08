// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Order', {
	refresh: function(frm) {
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
            frm.add_custom_button(__("Beziehe Lizenzfile von cFos"), function() {
                get_cfos_lizenz(frm);
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
		filter_additional_contact(frm, "supplier");
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
		filter_additional_contact(frm, "customer");
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
        check_vielfaches(frm);
        if (cur_frm.doc.project) {
            copy_project(frm);
        }
    }
})

function filter_additional_contact(frm, filter) {
    var contact_filter = "";
    
	if (filter == "customer") {
	   contact_filter = cur_frm.doc.customer_shipping;
	} else {
		
		contact_filter = cur_frm.doc.supplier_to_supplier;
	}
	console.log("filter", contact_filter);
	frm.set_query("zusaetzlicher_kontakt", function() {
		return {
			filters: {
				link_name: contact_filter
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

function copy_project(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.project = cur_frm.doc.project
    });
    cur_frm.refresh_field('items');
}

function get_cfos_lizenz(frm) {
    var items = []
    cur_frm.doc.items.forEach(function(entry) {
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
                        'evse_count': lizenz_item.evse_count
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
