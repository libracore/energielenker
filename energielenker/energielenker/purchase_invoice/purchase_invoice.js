// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        set_timestamps(frm);
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {'is_purchase_item': 1}
                }
            }
        }, 1000);
        
        if (frm.doc.__islocal) {
			set_update_stock(frm);
		}
    },
    validate: function(frm) {
        if (cur_frm.doc.project) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry) {
                if (!entry.project) {
                    entry.project = cur_frm.doc.project;
                } 
            });
        }
        check_vielfaches(frm);
        return
    },
    before_submit: function(frm) {
		validate_streckengeschäft(frm);
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

function set_update_stock(frm) {
	frappe.call({
		'method': 'energielenker.energielenker.purchase_invoice.purchase_invoice.check_for_streckengeschaeft',
		'args': {
			'doc_': cur_frm.doc
		},
		'async': false,
		'callback': function(response) {
			setTimeout(function() {
				cur_frm.set_value('update_stock', response.message);
			}, 1000);
		}
	});
}

function validate_streckengeschäft(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.purchase_invoice.purchase_invoice.check_for_streckengeschaeft',
        'args': {
            'doc_': cur_frm.doc
        },
        'async': false,
        'callback': function(response) {
			console.log(cur_frm.doc.update_stock)
			if (response.message == 1 && cur_frm.doc.update_stock == 0) {
				frappe.validated=false;
				frappe.confirm(
					'Achtung, Lager wird nicht aktualisiert, trotzdem Fortfahren?',
					function(){
						frappe.validated=true;
						window.close();
					},
					function(){
						window.close();
					}
				)
			} else if (response.message == 0 && cur_frm.doc.update_stock == 1) {
				frappe.validated=false;
				frappe.confirm(
					'Achtung, Lager wird aktualisiert obwohl dies ein Streckengeschäft ist, trotzdem Fortfahren?',
					function(){
						frappe.validated=true;
						window.close();
					},
					function(){
						window.close();
					}
				)
			} else {
				frappe.validated=true;
			}
        }
    });
}
