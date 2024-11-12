// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

var so_return;

frappe.ui.form.on("Delivery Note", {
    onload: function(frm) {
        var last_route = frappe.route_history.slice(-2, -1)[0];
        if (last_route) {
            // If you create an DN from the project, it will make sure to take the address set on the project than the customer primary address.
            if (last_route[1] == "Project") {
                frappe.call({
                    'method': "frappe.client.get",
                    'args': {
                        'doctype': "Project",
                        'name': last_route[2]
                    },
                    'callback': function(response) {
                        var project_address = response.message.shipping_address;
                        if (project_address) {
                            setTimeout(() => {
                                cur_frm.set_value('shipping_address_name', project_address);
                            }, 1500);
                        }
                    }
                });
            // If you create an DN from Sales Order, it will make sure to take the address set on the sales order
            } else if (last_route[1] == "Sales Order") {
                if (!cur_frm.doc.shipping_address_name) {
                    frappe.call({
                        'method': "frappe.client.get",
                        'args': {
                            'doctype': "Sales Order",
                            'name': last_route[2]
                        },
                        'callback': function(response) {
                            var shipping_adress = response.message.shipping_address_name;
                            if (shipping_adress) {
                                setTimeout(() => {
                                    cur_frm.set_value('shipping_address_name', shipping_adress);
                                }, 1500);
                            } else {
                                var shipping_adress = response.message.customer_address;
                                if (shipping_adress) {
                                    setTimeout(() => {
                                        cur_frm.set_value('shipping_address_name', shipping_adress);
                                    }, 1500);
                                }
                            }
                        }
                    });
                }
            }
        }
        
        //set "VK-Wert it. Kundenauftrag" before the amount/rate is change 
        if (cur_frm.doc.docstatus == 0) {
            if (cur_frm.doc.items.length > 0 ) {
                var items = cur_frm.doc.items;
                items.forEach(function(entry){
                    if (entry.against_sales_order) {
                        frappe.model.set_value(entry.doctype, entry.name, 'vk_wert', entry.amount);
                    }
                });
            }
        }
        
    },

    refresh: function(frm) {
        mark_depot_items(frm);
        set_timestamps(frm);
        setTimeout(() => {
            frm.remove_custom_button('Sales Return', 'Create');
            frm.page.add_inner_button('Sales Return', function() { 
                cur_frm.cscript.make_sales_return()
                so_return = "Return";
                }, 'Create')
            
        }, 10);
        
        setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {}
                }
            }
        }, 1000);
        
        if (frm.doc.freigabe_berechnung_ab) {
            var nowdate = frappe.datetime.get_today();
            if (frm.doc.freigabe_berechnung_ab == nowdate) {
                cur_frm.set_value('zur_berechnung_freigegeben', 1);
            } 
            
        }
        
        // get cost_center for item from SO if no project avaible
        if (!cur_frm.doc.project) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry){
                if (entry.against_sales_order) {
                    frappe.db.get_value("Sales Order", entry.against_sales_order, "cost_center").then(function(res){
                        entry.cost_center = res.message.cost_center;
                    });
                }
            });
        }
        if (cur_frm.doc.docstatus < 1) {
            frm.add_custom_button(__("Get Depot Items"),  function(){
              get_depot_items(frm);
            });

            if (!frm.doc.__islocal) {
                if (frm.doc.skip_check_against_sales_order != 1) {
                    frm.add_custom_button(__("Kundenauftrag Prüfung deaktivieren"),  function(){
                        toggle_check_against_sales_order(frm, 1);
                    });
                } else {
                    frm.add_custom_button(__("Kundenauftrag Prüfung aktivieren"),  function(){
                        toggle_check_against_sales_order(frm, 0);
                    });
                }
            }
        }
        if (frm.doc.__islocal) {
            validate_depot(frm);
            check_product_bundle(frm);
            check_foreign_customers(frm.doc.customer);
        }
    },
    before_save(frm) {
        if (so_return == "Return"){
            frappe.confirm('<strong> Der entsprechende Kundenauftrag wurde wiedereröffnet.</strong> <br> Möchten Sie, dass der Auftrag geschlossen bleibt? ',
                () => {
                    // action to perform if Continue is selected
                    cur_frm.set_value('so_return', 1);
                    so_return = "Leave SO Close";
                },() => {
                    // action to perform if No is selected
                    console.log("leave open")
                    so_return = "Leave SO Open";
                }
            )
        }
        
        check_so_quantities(frm);
        
        // function deactivated because of conflict with new process -> should not be needed anymore (2024-10-04)
        //~ if (frm.doc.__islocal) {
           //~ cur_frm.doc.items.forEach(function(entry){
               //~ frappe.call({
                    //~ "method": "frappe.client.get",
                    //~ "args": {
                        //~ "doctype": "Item",
                        //~ "name": entry.item_code
                    //~ },
                    //~ "callback": function(r) {
                        //~ if (r.message.item_defaults[0].default_warehouse) {
                            //~ entry.warehouse = r.message.item_defaults[0].default_warehouse;
                        //~ }
                    //~ }
                //~ })
           //~ });
        //~ }
        
    },
    on_submit: function(frm) {
        if (cur_frm.doc.so_return){
            update_so_status(frm);
        }
    },
    customer: function(frm) {
        shipping_address_query(frm);
        check_foreign_customers(frm.doc.customer);
    },
    project: function(frm) {
       if (frm.doc.__islocal && cur_frm.doc.project) {
           frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    cur_frm.set_value('customer', project.customer);
                }
            });
        }
    },
    shipping_address_name: function(frm) {
        if (cur_frm.doc.shipping_address_name) {
            fetch_kontakt_aus_lieferadresse(frm);
        } else {
            cur_frm.set_value("kontakt_aus_lieferadresse", '');
            cur_frm.set_value("kontaktname_aus_lieferadresse", '');
        }
    },
    validate: function(frm) {
        if (cur_frm.doc.shipping_address_name) {
            fetch_kontakt_aus_lieferadresse(frm);
        } else {
            cur_frm.set_value("kontakt_aus_lieferadresse", '');
            cur_frm.set_value("kontaktname_aus_lieferadresse", '');
        }
        
        if (cur_frm.doc.ignore_pricing_rule) {
            var items = cur_frm.doc.items;
            items.forEach(function(entry){
                entry.pricing_rules = null;
            });
        }
        
        if ((!cur_frm.doc.shipping_address_name)&&(!cur_frm.doc.new_address_name)) {
            frappe.msgprint( __("Es muss eine Lieferadresse hinterlegt werden"), __("Validation") );
            frappe.validated=false;
        }
        validate_warehouse(frm);
    },
    deliver_to(frm) {
        //set default customer and clearing the fields when re-selecting
        cur_frm.set_value('customer', "Dummy-Kunde (nicht deaktivieren!)");
        
        if (frm.doc.deliver_to == "Customer") {
            cur_frm.set_value('customer', "");
            cur_frm.set_value('supplier', "");
            cur_frm.set_value('lead', "");
        } else if (frm.doc.deliver_to == "Lead") {
            cur_frm.set_value('supplier', "");
            cur_frm.set_value('tax_id', "");
        } else if (frm.doc.deliver_to == "Supplier") {
            cur_frm.set_value('lead', "");
            cur_frm.set_value('tax_id', "");
        }
        
        // Saving without customer address must not be possible.
        if (frm.doc.deliver_to == "Customer") {
            frm.set_df_property("customer_address", "reqd", 1);
            frm.set_df_property("new_customer_address", "reqd", 0);
        } else {
            frm.set_df_property("customer_address", "reqd", 0);
            frm.set_df_property("new_customer_address", "reqd", 1);
        } 
        
        cur_frm.set_value('new_address_name', "");
        cur_frm.set_value('new_contact_name', "");
        cur_frm.set_value('new_customer_address', "");
        cur_frm.set_value('shipping_address_name', "");
        cur_frm.set_value('contact_person', "");
        cur_frm.set_value('customer_address', "");
        
        //Set new tax_id if exist for the supplier
        cur_frm.add_fetch('supplier','tax_id','tax_id');
    },
    lead(frm) {
        set_new_address_and_contact_filter(frm, "Lead");
        if (frm.doc.lead) {
            frappe.call({
                'method': "frappe.client.get_list",
                'args':{
                    'doctype': "Lead",
                    'filters': [
                        ["name","IN", [cur_frm.doc.lead]]
                    ],
                    'fields': ["company_name"]
                },
                'callback': function (response) {
                    var lead_name = response.message;
                    cur_frm.set_value('title', lead_name[0].company_name);
                }
            });
        }    

    },
    supplier(frm) {
        set_new_address_and_contact_filter(frm, "Supplier");
        if (frm.doc.supplier) {
            cur_frm.set_value('title', cur_frm.doc.supplier);
        }
    },
    //Setting the new values into the original fields to be displayed and fetch in the print-format
    new_address_name(frm) {
        if (frm.doc.new_address_name) {
            cur_frm.set_value('shipping_address_name', frm.doc.new_address_name);
        }
    },
    new_contact_name (frm) {
        if (frm.doc.new_contact_name) {
            cur_frm.set_value('contact_person', frm.doc.new_contact_name);
        }
    },
    new_customer_address (frm) {
        if (frm.doc.new_customer_address) {
            cur_frm.set_value('customer_address', frm.doc.new_customer_address);
        }
    },
    before_submit: function(frm) {
        check_for_webshop_points(frm);
        check_for_overdelivery(frm);
        //~ check_for_depot(frm);
    },
    after_cancel: function(frm) {
        remove_webshop_points(frm);
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

frappe.ui.form.on("Delivery Note Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Delivery Note Item", "with_bom", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on('Delivery Note Item', {
    source_depot: function(frm, cdt, cdn) {
        mark_depot_items(frm)
    },
    items_remove: function(frm, cdt, cdn) {
        mark_depot_items(frm);
    },
    items_add: function(frm, cdt, cdn) {
        set_cost_center(frm, cdt, cdn);
    },
    fetch_serial_no: function(frm, cdt, cdn) {
        fetch_serial_no(frm, cdt, cdn);
    },
    form_render: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        cur_frm.get_field("items").grid.grid_rows[row.idx - 1].grid_form.fields_dict.serial_no.$wrapper.find(".btn").remove()
    }
})

function check_text_and_or_alternativ(item) {
    if (item.textposition == 1 || item.alternative_position == 1) {
        item.discount_percentage = 100.00;
        item.discount_amount = item.price_list_rate;
        item.rate = 0.00;
        cur_frm.refresh_field('items');
    } else {
        item.discount_percentage = 0.00;
        item.discount_amount = 0.00;
        item.rate = item.price_list_rate;
        cur_frm.refresh_field('items');
    }
}

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
                if (item.with_bom == 1) {
                    item.typ = 'St.';
                } else {
                    if (item.kalkulationssumme_interner_positionen == 1) {
                        item.typ = 'KS';
                    } else {
                        item.typ = 'Norm.';
                    }
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

function fetch_kontakt_aus_lieferadresse(frm) {
    frappe.call({
        'method': "energielenker.energielenker.delivery_note.delivery_note.fetch_kontakt_aus_lieferadresse",
        'args': {
            'lieferadresse': cur_frm.doc.shipping_address_name
        },
        'callback': function(response) {
            if (response.message) {
                var kontakt = response.message;
                if (kontakt != 'keiner') {
                    cur_frm.set_value("kontakt_aus_lieferadresse", kontakt.link);
                    cur_frm.set_value("kontaktname_aus_lieferadresse", kontakt.name);
                }
            }
        }
    });
}

function update_so_status(frm) {
    cur_frm.doc.items.forEach(function(entry) { 
        if (entry.against_sales_order) {
            frappe.call({
                method: "erpnext.selling.doctype.sales_order.sales_order.update_status",
                args: {status: 'Closed', name: entry.against_sales_order}
            });
        }
    });
}

function set_new_address_and_contact_filter(frm, filter) {
    var deliver_to = "";
    
    if (filter == "Supplier") {
        deliver_to = frm.doc.supplier;
    } else {
        deliver_to = frm.doc.lead;
    }
    
    frm.set_query("new_address_name", function() {
        return {
            filters: {
                link_name: deliver_to
            }                       
        }
    });

    frm.set_query("new_contact_name", function() {
        return {
            filters: {
                link_name: deliver_to
            }                       
        }
    });
}

function get_depot_items() {
    frappe.prompt([
        {'fieldname': 'depot', 'fieldtype': 'Link', 'label': 'Depot', 'options': 'Depot', 'reqd': 1, 'get_query': function() {
                                                                                                        var sales_orders = get_depot_sales_order();
                                                                                                        if (sales_orders[0]) {
                                                                                                            return {
                                                                                                                filters: [
                                                                                                                    ['sales_order', "in", sales_orders]
                                                                                                                ]
                                                                                                            };
                                                                                                        }
                                                                                                    }
        }
    ],
    function(values){
        frappe.call({
            'method': 'energielenker.energielenker.doctype.depot.depot.get_items_html',
            'args': {
                'depot': values.depot,
                'event': "delivery_note"
            },
            'async': false,
            'callback': function(response) {
                var items = response.message[0]
                var depot = response.message[1]
                var sales_order = response.message[2]
                var warehouse = response.message[3]
                if (items.length > 0) {
                    for (let i = 0; i < items.length; i++) {
                        if (items[i].balance_qty > 0) {
                            var child = cur_frm.add_child('items');
                            frappe.model.set_value(child.doctype, child.name, 'item_code', items[i].item_code);
                            frappe.model.set_value(child.doctype, child.name, 'qty', items[i].balance_qty);
                            frappe.model.set_value(child.doctype, child.name, 'source_depot', depot);
                            frappe.model.set_value(child.doctype, child.name, 'against_sales_order', sales_order);
                            frappe.model.set_value(child.doctype, child.name, 'typ', "Int.");
                            frappe.model.set_value(child.doctype, child.name, 'interne_position', 1);
                            frappe.model.set_value(child.doctype, child.name, 'warehouse', warehouse);
                            cur_frm.refresh_field("items");
                        }
                    }
                    frappe.show_alert('Alle Artikel wurden erfolgreich importiert', 5);
                } else {
                    frappe.show_alert('Keine Artikel vorhanden', 5);
                }
            }
        });
    },
    'Please select Depot',
    'Get Items'
    )
}

function validate_warehouse(frm) {
    for (let i = 0; i < cur_frm.doc.items.length; i++) {
        if (cur_frm.doc.items[i].source_depot) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Depot",
                    'name': cur_frm.doc.items[i].source_depot
                },
                'callback': function(response) {
                    var warehouse = response.message.to_warehouse;
                    if (warehouse) {
                            frappe.model.set_value(cur_frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "warehouse", warehouse);
                    }
                }
            });
        }
    }
}

function get_depot_sales_order(frm) {
    var sales_orders = [];
    cur_frm.doc.items.forEach(function(item) {
        if (!sales_orders.includes(item.against_sales_order)) {
            sales_orders.push(item.against_sales_order);
        }
    });
    return sales_orders
}

function check_for_depot(frm) {
    var lines_with_depot = []
    for (i=0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].source_depot) {
            lines_with_depot.push(i+1);
        }
    }
    if (lines_with_depot.length > 0 && !locals.do_submit) {
        frappe.validated=false;
        frappe.confirm(
            "Achtung, Zeilen " + lines_with_depot + " gehören zu einer Kommission - trotzdem Fortfahren?",
            function(){
                locals.do_submit=true;
                cur_frm.savesubmit();
            }
        )
    }
    locals.do_submit=false;
}

function validate_depot(frm) {
    var items_with_so = []
    for (let i=0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].against_sales_order && !frm.doc.items[i].source_depot) {
            items_with_so.push({'sales_order': frm.doc.items[i].against_sales_order, 'item': frm.doc.items[i].item_code});
        }
    }
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.validate_depot',
        'args': {
            'items_string': items_with_so
        }
    });
}

function mark_depot_items(frm) {
    for (i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].source_depot) {
            var $row = $(frm.fields_dict["items"].grid.grid_rows[i].wrapper);
            $row.css({
                'background-color': '#F5F5F5'
            });
        } else {
            var $row = $(frm.fields_dict["items"].grid.grid_rows[i].wrapper);
            $row.css({
                'background-color': 'transparent'
            });
        }
    }
}

async function check_product_bundle(frm) {
    for (i = 0; i < frm.doc.items.length; i++) {
        let product_bundle = await frappe.db.get_value("Item", frm.doc.items[i].item_code, "is_product_bundle");
        if (product_bundle.message.is_product_bundle == 1) {
            frappe.msgprint("<p>Produkt-Bundle-Artikel vorhanden.</p>", "Achtung!");
            break;
        }
    }
}

function check_for_webshop_points(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.check_for_webshop_points',
        'args': {
            'doc': cur_frm.doc
        },
        'async': false,
        'callback': function(response) {
            var validation = response.message;
            if (!validation) {
                frappe.validated=false;
                //~ frappe.msgprint( __("Dieser Kunde hat kein Konto!"), __("Validation") );
            }
        }
    });
}

function remove_webshop_points(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.check_for_webshop_points',
        'args': {
            'doc': cur_frm.doc,
            'event': "cancel"
        },
        'async': false,
        'callback': function(response) {
            var validation = response.message;
            if (!validation) {
                frappe.validated=false;
            }
        }
    });
}

function check_for_overdelivery(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.check_for_overdelivery',
        'args': {
            'doc': cur_frm.doc
        },
        'async': false,
        'callback': function(response) {
            var validation = response.message;
            if (!validation) {
                frappe.validated=false;
            }
        }
    });
}

function toggle_check_against_sales_order(frm, flag) {
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.toggle_check_against_sales_order',
        'args': {
            'dn': cur_frm.doc.name,
            'flag': parseInt(flag)||0
        },
        'async': false,
        'callback': function(response) {
            cur_frm.reload_doc();
        }
    });
}

function set_cost_center(frm, cdt, cdn) {
    if (!frm.doc.project) {
        let cost_center = false
        for (let i = 0; i < frm.doc.items.length; i++) {
            if (!cost_center) {
                if (frm.doc.items[i].against_sales_order) {
                    cost_center = frm.doc.items[i].cost_center
                }
            } else {
                break;
            }
        }
        if (cost_center) {
            frappe.model.set_value(cdt, cdn, "cost_center", cost_center)
        }
    }
}

function check_so_quantities(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.delivery_note.delivery_note.check_so_quantities',
        'args': {
            'doc': frm.doc
        },
        'callback': function(response) {
            let overdelivery = response.message.overdelivery;
            if (overdelivery) {
                let affected_items = response.message.affected_items;
                let message = response.message.message;
                for (let i = 0; i < affected_items.length; i++) {
                    frappe.model.set_value("Delivery Note Item", affected_items[i].item_line_name, 'qty', affected_items[i].undelivered_qty);
                }
                frappe.msgprint({
                    title: __('Überlieferung aus Kundenauftrag unzulässig'),
                    indicator: 'red',
                    message: __(`Die Menge der folgenden Artikel wurde entsprechend der Bestellmenge korrigiert: <br><br> ${ message }`),
                });
            }
        }
    });
}

function fetch_serial_no(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (!row.warehouse) {
        frappe.msgprint("Bitte zuerst das Lager angeben.")
    } else {
        let by_pos_filters = {'so_detail': row.so_detail, 'warehouse': row.warehouse}
        let by_item_filters = {'item_code': row.item_code, 'delivery_document_no': null, 'warehouse': row.warehouse }
        if (row.batch_no) {
            by_item_filters['batch_no'] = row.batch_no;
            by_pos_filters['batch_no'] = row.batch_no;
        }
        let serial_dialog = new frappe.ui.Dialog({
            title: "Select Serial Numbers",
            fields: [
                { fieldtype: 'Section Break', label: 'Allgemeine Informationen' },

                {
                    fieldname: 'item_code',
                    label: 'Item Code',
                    fieldtype: 'Data',
                    read_only: 1,
                    options: 'Customer'
                },
                
                { fieldtype: 'Column Break' },
                
                {
                    fieldname: 'warehouse',
                    label: 'Warehouse',
                    fieldtype: 'Link',
                    options: 'Warehouse',
                    read_only: 1
                },

                { fieldtype: 'Section Break', label: 'Serial Numbers' },

                {
                    fieldname: 'serial_no_by_pos',
                    label: 'Add Serial Number by Line',
                    fieldtype: 'Link',
                    options: 'Serial No',
                    description: 'With reference to Batch and Warehouse',
                    'onchange' : function() { set_new_serial_no(serial_dialog, "serial_no_by_pos") },
                    'get_query': function() { return { query: "energielenker.energielenker.delivery_note.delivery_note.serial_no_by_pos_query", filters: by_pos_filters } }
                },
                
                {
                    fieldname: 'serial_no_by_item',
                    label: 'Add Serial Number by Item',
                    fieldtype: 'Link',
                    options: 'Serial No',
                    description: 'With reference to Batch and Warehouse',
                    'onchange' : function() { set_new_serial_no(serial_dialog, "serial_no_by_item") },
                    'get_query': function() { return { filters: by_item_filters } }
                },

                { fieldtype: 'Column Break' },

                {
                    fieldname: 'selected_serial_no',
                    label: 'Selected Serial Numbers',
                    fieldtype: 'Small Text',
                }
            ],
            primary_action: function(){
                serial_dialog.hide();
                set_serial_values(serial_dialog, cdt, cdn);
            },
        primary_action_label: __('Insert')
        });
        serial_dialog.set_value("item_code", row.item_code);
        serial_dialog.set_value("warehouse", row.warehouse);
        serial_dialog.show();
    }
}

function set_serial_values(serial_dialog, cdt, cdn) {
    let selected_serial_no = serial_dialog.get_value('selected_serial_no');
    frappe.model.set_value(cdt, cdn, "serial_no", selected_serial_no);
}

function set_new_serial_no(serial_dialog, trigger_field) {
    let value = serial_dialog.get_value(trigger_field)
    if (value) {
        let actual_serial_nos = serial_dialog.get_value('selected_serial_no')
        if (actual_serial_nos && !actual_serial_nos.includes(value)) {
            actual_serial_nos += "\n" + value
            serial_dialog.set_value("selected_serial_no", actual_serial_nos)
        } else if (!actual_serial_nos && !actual_serial_nos.includes(value)) {
            serial_dialog.set_value("selected_serial_no", value)
        }
    serial_dialog.set_value(trigger_field, null)
    }
}


