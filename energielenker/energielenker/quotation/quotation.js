frappe.ui.form.on('Quotation', {
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
        
        if (frm.doc.__islocal && cur_frm.doc.project) {
           frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    cur_frm.set_value('party_name', project.customer);
                }
            });
        }
    },
    party_name: function(frm) {
        if (cur_frm.doc.quotation_to == 'Customer') {
            setTimeout(function(){ shipping_address_query(frm); }, 500);
        }
    },
    validate: function(frm) {
        check_vielfaches(frm);
    }
})

frappe.ui.form.on("Quotation Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Quotation Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
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
                'link_doctype': cur_frm.doc.quotation_to,
                'link_name': cur_frm.doc.party_name,
                'produktionsstandort': 1
            }
        }
    };
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
