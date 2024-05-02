// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

cur_frm.dashboard.add_transactions([
    {
        'label': 'Reklamationen',
        'items': [
            'Issue'
        ]
    }
]);

frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
	   overwrite_before_update_after_submit(frm);
       set_timestamps(frm);
       
       frm.page.add_inner_button('Reklamation', (frm) => make_reklamation(), 'Make')
       
       setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
                    filters: {'is_sales_item': 1}
                }
            }
        }, 1000);
        if (cur_frm.doc.customer) {
            filter_contact(frm, "contact_person_two" , cur_frm.doc.customer);
            filter_contact(frm, "shipping_contact", cur_frm.doc.customer);

            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Customer",
                    'name': cur_frm.doc.customer
                },
                'async': false,
                'callback': function(response) {
                    var customer = response.message;
                    cur_frm.fields_dict['navision_konto'].get_query = function(doc) {
                         return {
                             filters: {
                                 "ic": customer.navision_internal_ic,
                                 "deaktiviert": 0
                             }
                         }
                    }
                }
            });
        }
        
        cost_center_query(frm);
        
        if (!cur_frm.doc.vertriebsgruppe) {
            frappe.call({
                method: "energielenker.energielenker.sales_order.sales_order.get_employee",
                args: {},
                callback: function (r) {cur_frm.set_value("vertriebsgruppe", r.message);}
            });
        }
        
        //Allow Lead to be use to create an Order
        setTimeout(function() {
            if (cur_frm.doc.docstatus===0) {
                cur_frm.remove_custom_button('Quotation', 'Get items from');
                cur_frm.add_custom_button(__('Quotations'),
                    function() {
                        erpnext.utils.map_current_doc({
                            method: "erpnext.selling.doctype.quotation.quotation.make_sales_order",
                            source_doctype: "Quotation",
                            target: me.frm,
                            setters: [
                                {
                                    label: "Customer",
                                    fieldname: "customer_name",
                                    fieldtype: "Link",
                                    options: "Customer",
                                    default: cur_frm.doc.customer || undefined
                                }
                            ],
                            get_query_filters: {
                                company: me.frm.doc.company,
                                docstatus: 1,
                                status: ["!=", "Lost"]
                            }
                        })
                    }, __("Get items from"));
            }
        }, 1000);
        
        if (['WAGO GmbH & Co. KG', 'WAGO Kontakttechnik GmbH & Co. KG'].includes(cur_frm.doc.customer)) {
            frm.add_custom_button(__("Hinterlege cFos als Lieferant"), function() {
                hinterlege_cfos_als_lieferant(frm);
            });
        }
        
        // hack to remove "+" in dashboard
        $(":button[data-doctype='Issue']").remove();
    },
    after_cancel: function(frm) {
        if (cur_frm.doc.project) {
            // clear fetched payment forecast
            frappe.call({
                method: "energielenker.energielenker.project.project.clear_payment_schedule",
                args: {
                    "project": cur_frm.doc.project,
                    "sales_order": cur_frm.doc.name
                },
                callback: function (r) {}
            });
        }
        remove_webshop_points(frm);
    },
    customer: function(frm) {
        shipping_address_query(frm);
        if (cur_frm.doc.customer == 'WAGO Kontakttechnik GmbH & Co. KG') {
            frm.add_custom_button(__("Hinterlege cFos als Lieferant"), function() {
                hinterlege_cfos_als_lieferant(frm);
            });
        }
        if (cur_frm.doc.customer) {
            validate_customer(frm, "customer");
			frappe.call({
				method: 'frappe.client.get_value',
                args: {
					doctype: 'Customer',
						filters: { name: cur_frm.doc.customer },
                        fieldname: 'ansprechpartner'
                    },
                    callback: function(response) {
						var kundenbetreuung = response.message.ansprechpartner;
						if (kundenbetreuung){
							cur_frm.set_value('ansprechpartner', kundenbetreuung);
						}
                    }
            })
        }
    },
    validate: function(frm) {
        check_navision(frm);
        validate_customer(frm, "validate");
        if (cur_frm.doc.project_clone) {
            cur_frm.set_value('project', cur_frm.doc.project_clone);
        } else {
            cur_frm.set_value('project_clone', cur_frm.doc.project);
        }
        check_vielfaches(frm);
        add_item_supplier(frm);
        
        if (cur_frm.doc.amended_from && cur_frm.doc.__islocal) {
			setTimeout(function() {
				amend_so_issue(frm);
			}, 1500);
		}
    },
    project: function(frm) {
        cur_frm.set_value('project_clone', cur_frm.doc.project);
        fetch_customer_from_project(frm);
    },
    onload: function(frm) {
        if (cur_frm.doc.project) {
            cur_frm.set_value('project_clone', cur_frm.doc.project);
        }        
    },
    navision_konto: function(frm) {
        if (!cur_frm.doc.navision_konto||cur_frm.doc.navision_konto == '') {
            cur_frm.set_value('navision_kontonummer', '');
        }
    },
    zahlungsplan_anpassen: function(frm) {
        var data = [];
        cur_frm.doc.payment_schedule.forEach(function(entry) {
            var row_data = {
                name: entry.name,
                due_date: entry.due_date,
                invoice_portion: entry.invoice_portion,
                original_invoice_portion: entry.invoice_portion,
                payment_amount: entry.payment_amount,
                original_payment_amount: entry.payment_amount,
                description: entry.description
            }
            data.push(row_data)
        });
        var d = new frappe.ui.Dialog({
            title: 'Anpassungen Zahlungsplan',
            fields: [
                {'fieldname': 'ht', 'fieldtype': 'HTML'},
                {
                    fieldname: 'payment_schedule_table',
                    fieldtype: 'Table',
                    data: cur_frm.doc.payment_schedule,
                    label: "Zahlungsplan",
                    cannot_add_rows: false,
                    in_place_edit: true,
                    reqd: 1,
                    data: data,
                    fields: [
                        {
                            fieldtype:'Data',
                            fieldname:"name",
                            hidden: 1
                        },
                        {
                            fieldtype:'Small Text',
                            fieldname:"description",
                            in_list_view: 1
                        },
                        {
                            fieldtype:'Date',
                            fieldname:"due_date",
                            in_list_view: 1,
                            read_only: 0,
                            reqd: 1,
                            label: __('Due Date')
                        },
                        {
                            fieldtype:'Percent',
                            fieldname:"invoice_portion",
                            read_only: 0,
                            in_list_view: 1,
                            reqd: 1,
                            label: __('Invoice Portion'),
                            change: function() {
                                if (this.doc.original_invoice_portion) {
                                    var old_value = this.doc.original_invoice_portion;
                                    var new_value = this.doc.invoice_portion;
                                    var old_currency = this.doc.payment_amount;
                                    var new_currency = (old_currency / old_value) * new_value;
                                    this.doc.payment_amount = new_currency;
                                    this.doc.original_invoice_portion = new_value;
                                    this.doc.original_payment_amount = new_currency;
                                    cur_dialog.fields_dict.payment_schedule_table.grid.refresh();
                                } else {
                                    var old_value = 100;
                                    var new_value = this.doc.invoice_portion;
                                    var old_currency = cur_frm.doc.rounded_total;
                                    var new_currency = (old_currency / old_value) * new_value;
                                    this.doc.payment_amount = new_currency;
                                    this.doc.original_invoice_portion = new_value;
                                    this.doc.original_payment_amount = new_currency;
                                    cur_dialog.fields_dict.payment_schedule_table.grid.refresh();
                                }
                            }
                        },
                        {
                            fieldtype:'Currency',
                            fieldname:"payment_amount",
                            read_only: 0,
                            in_list_view: 1,
                            reqd: 1,
                            label: __('Payment Amount'),
                            change: function() {
                                if (this.doc.original_payment_amount) {
                                    var old_value = this.doc.original_payment_amount;
                                    var new_value = this.doc.payment_amount;
                                    var old_percent = this.doc.invoice_portion;
                                    var new_percent = (old_percent / old_value) * new_value;
                                    this.doc.invoice_portion = new_percent;
                                    this.doc.original_payment_amount = new_value;
                                    this.doc.original_invoice_portion = new_percent;
                                    cur_dialog.fields_dict.payment_schedule_table.grid.refresh();
                                } else {
                                    var old_value = cur_frm.doc.rounded_total;
                                    var new_value = this.doc.payment_amount;
                                    var old_percent = 100;
                                    var new_percent = (old_percent / old_value) * new_value;
                                    this.doc.invoice_portion = new_percent;
                                    this.doc.original_payment_amount = new_value;
                                    this.doc.original_invoice_portion = new_percent;
                                    cur_dialog.fields_dict.payment_schedule_table.grid.refresh();
                                }
                            }
                        },
                        {
                            fieldtype:'Percent',
                            fieldname:"original_invoice_portion",
                            hidden: 1,
                            label: __('Invoice Portion')
                        },
                        {
                            fieldtype:'Currency',
                            fieldname:"original_payment_amount",
                            hidden: 1,
                            label: __('Payment Amount')
                        },
                        {
                            fieldtype:'Check',
                            fieldname:"to_delete",
                            in_list_view: 1,
                            label: 'Löschen'
                        }
                    ]
                }
            ],
            primary_action: function(){
                var betrag = 0;
                var warning = false;
                d.get_values().payment_schedule_table.forEach(function(entry){
                    if(!entry.due_date||!entry.invoice_portion||!entry.payment_amount) {
                        warning = true;
                    } else {
                        betrag += entry.invoice_portion;
                    }
                });
                if (!warning) {
                    if (betrag >= 99.998) {
                        d.hide();
                        frappe.call({
                            "method": "energielenker.energielenker.zahlungsplan.zahlungsplan.change_in_so",
                            "args": {
                                "payment_schedule": d.get_values().payment_schedule_table,
                                "so": cur_frm.doc.name
                            },
                            "callback": function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    } else {
                        frappe.msgprint("Bitte prüfen Sie die Einträge<br>Aktueller Prozentsatz gem. Zahlungsplan: " + String(betrag) + "%");
                    }
                } else {
                    frappe.msgprint("Bitte alle Pflichtfelder befüllen");
                }
            },
            primary_action_label: __('Übernehmen')
        });
        d.fields_dict.ht.$wrapper.html('Hier können Sie Änderungen am Zahlungsplan vornehmen.<br>Die Änderungen werden an das, insofern vorhanden, verknüpfte Projekt übertragen.');
        d.show();
    },
    contact_person_two: function(frm) {
        contact_info_display(frm, cur_frm.doc.contact_person_two, "contact_display_two") 
    },
    shipping_contact: function(frm) {
        contact_info_display(frm, cur_frm.doc.shipping_contact, "shipping_contact_display") 
    },
    delivery_date (frm) {
        if ( frm.doc.delivery_date != frm.doc.items[0].delivery_date ) {
            var items = frm.doc.items || [];
            for (var i = 0; i < items.length; i++) {
                frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, 'delivery_date', frm.doc.delivery_date);
            }
        } 
    },
    zusatzgeschaft: function(frm) {
		updateSalesInvoices(frm.doc.name, frm.doc.zusatzgeschaft);
    },
    before_submit: function(frm) {
        check_for_webshop_points(frm);
    },
    on_submit: function(frm) {
        create_dn_for_webshop_points(frm);
    }
});

// overwrite_before_update_after_submit to update projektbewertung_ignorieren in project
function overwrite_before_update_after_submit(frm){
	frappe.call({
	      "method": "energielenker.energielenker.sales_order.sales_order.overwrite_before_update_after_submit",
	   });
}


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


function updateSalesInvoices(salesOrderName, zusatzgeschaft) {
	console.log("sales order", salesOrderName, zusatzgeschaft)
    frappe.call({
        method: "energielenker.energielenker.sales_order.sales_order.update_zusatzgeschaft_in_sales_invoices",
        args: {
            "sales_order_name": salesOrderName,
            "zusatzgeschaft": zusatzgeschaft
        },
        callback: function(response) {
			console.log(response.message);
        }
    });
}


function filter_contact(frm, field, filter) {

    frm.set_query(field , function() {
        return {
            filters: {
                link_name: filter
            }
        }
    }) 
}

function contact_info_display(frm, name, field) {
    frappe.call({
        'method': "frappe.client.get_list",
        'args':{
            'doctype': "Contact",
            'filters': [
                ["name","IN", [name]]
            ],
            'fields': ["salutation", "first_name", "last_name", "email_id" ,"phone"]
        },
        'callback': function (response) {
            var res = response.message;
            var info;
            var full_name = res[0].first_name + " " + res[0].last_name;

            if ( res[0].salutation ) {
                full_name = `${res[0].salutation} ${full_name}`;
            }

            if ( res[0].email_id && res[0].phone) {
                info = `${full_name} <br> Email: ${res[0].email_id} <br> Phone: ${res[0].phone}`;
                cur_frm.set_value(field, info);
            } else if ( res[0].email_id ) {
                info = `${full_name} <br> Email: ${res[0].email_id}`;
                cur_frm.set_value(field, info);
            } else if ( res[0].phone ) {
                info = `${full_name} <br> Phone: ${res[0].phone}`;
                cur_frm.set_value(field, info);
            } else {
                cur_frm.set_value(field, full_name);
            }
        }
    });
}


function fetch_customer_from_project(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Project",
            "name": cur_frm.doc.project
        },
        "callback": function(r) {
            var project = r.message;
            cur_frm.set_value('customer', project.customer);
        }
    });
}

frappe.ui.form.on("Sales Order Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "interne_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

frappe.ui.form.on("Sales Order Item", "kalkulationssumme_interner_positionen", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    set_item_typ(item);
});

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

function check_navision(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Customer",
            "name": cur_frm.doc.customer
        },
        "callback": function(r) {
            var customer = r.message;
            if (!customer.navision_nr) {
                frappe.msgprint( "Der Kunde besitzt noch keine Navision Nr.", __("Validation") );
                frappe.validated=false;
            }
        }
    });
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
                    entry.vielfaches = item.verkauf_vielfaches;
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

function cost_center_query(frm) {
    cur_frm.fields_dict['cost_center'].get_query = function(doc) {
        return {
            filters: {
                'auswahl_unterbinden': 0
            }
        }
    };
}

function hinterlege_cfos_als_lieferant(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.supplier = 'cFos Software GmbH';
    });
    cur_frm.refresh_field('items');
}

function make_reklamation(frm){
    frappe.prompt([
        {
            label: 'Betreff',
            fieldname: 'subject',
            fieldtype: 'Data',
            reqd: 1
        },
        {
            label: 'Priorität',
            fieldname: 'priority',
            fieldtype: 'Link',
            options: 'Issue Priority',
            reqd: 1
        },
        {
            label: 'Beschreibung',
            fieldname: 'details',
            fieldtype: 'Text Editor',
            reqd: 1
        },
    ], (values) => {
        frappe.call({
            "method": "energielenker.energielenker.sales_order.sales_order.make_issue_from_sales_order",
            "args": {
                "sales_order": cur_frm.doc.name,
                "subject": values.subject,
                "priority": values.priority,
                "details": values.details,
            },
            "callback": function(r) {
                var issue_name = r.message
                if (issue_name) {
                    frappe.msgprint(`Die Reklamation <a href="https://erp.energielenker.de/desk#Form/Issue/${issue_name}" target="_blank"> <b>${issue_name}</b></a> wurde erfolgreich angelegt.`)
                    cur_frm.reload_doc();
                }
            }
        }); 
    })
}

function add_item_supplier(frm) {
    frm.doc.items.forEach(function(item) {
        frappe.call({
                "method": "energielenker.energielenker.sales_order.sales_order.fetch_supplier",
                "args": {
                    "item": item.item_code
                },
                "async": true,
                "callback": function(r) {
                    var supplier = r.message;
                    item.supplier = supplier;
                    cur_frm.refresh_field('items');
                }
        });
    });
}

//amend sales_order field in issue if sales order got ammended
function amend_so_issue(frm) {
	frappe.call({
		"method": "energielenker.energielenker.sales_order.sales_order.amend_so_issue",
		"args": {
			"sales_order": frm.doc.name,
			"amended_from": frm.doc.amended_from, 
		},
   });
}

function check_for_webshop_points(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.check_for_webshop_points',
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

function remove_webshop_points(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.check_for_webshop_points',
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

function create_dn_for_webshop_points(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.create_delivery_note',
        'args': {
            'sales_order_name': cur_frm.doc.name
        }
    });
}

function validate_customer(frm, event) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.validate_customer',
        'args': {
            'customer': frm.doc.customer
        },
        "async": false,
        'callback': function(response) {
            var validation = response.message
            if (validation) {
                frappe.msgprint( __("Kunde ist gesperrt!"), __("Sperrkunde") );
                if (event == "customer") {
                    cur_frm.set_value("customer", "");
                } else {
                    frappe.validated=false;
                }
            }
        }
    });
}
