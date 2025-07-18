// Copyright (c) 2025, libracore AG and contributors
// For license information, please see license.txt

cur_frm.dashboard.add_transactions([
    {
        'label': 'Reklamationen',
        'items': [
            'Issue'
        ]
    },
    {
        'label': 'Material',
        'items': [
            'Depot',
        ]
    },
    {
        'label': 'Manufacturing',
        'items': [
            'BOM',
        ]
    }
]);

frappe.ui.form.on("Sales Order", {
    setup: function(frm) {
		// formatter for material request item
		frm.set_indicator_formatter('item_code',
			function(doc) { return (doc.delivered_position || doc.delivered_position || doc.stock_qty<=doc.delivered_qty) ? "green" : "orange" })
    },
    
    refresh: function(frm) {
	   overwrite_before_update_after_submit(frm);
       set_timestamps(frm);
       set_row_options(frm);
       display_closed_positions(frm);
       
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
        
        if (cur_frm.doc.__islocal) {
            check_for_part_list_items(frm);
            check_foreign_customers(frm.doc.customer);
            //Remove information for Manually Delivered or Closed Position
            remove_delivered_and_closed(frm);
        }
        
        // hack to remove "+" in dashboard
        $(":button[data-doctype='Issue']").remove();
        
        frm.set_query('billing_address_name', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.customer
                }
            };
        });
        
        frm.set_query('billing_contact', function() {
            return {
                filters: {
                    'link_doctype': 'Customer',
                    'link_name': frm.doc.customer
                }
            };
        });
        
        //Filter Tasks for Service Projects
        if (frm.doc.is_service_project) {
            cur_frm.fields_dict.items.grid.get_field('task').get_query = function(doc) {                                                                      
                    return {
                        filters: {'project': frm.doc.project}
                    }
            }
        }
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
    },
    customer: function(frm) {
        set_lead_source(frm.doc.customer);
        check_foreign_customers(frm.doc.customer);
        shipping_address_query(frm);
        remove_billing_address(frm);
        if (cur_frm.doc.customer == 'WAGO Kontakttechnik GmbH & Co. KG') {
            frm.add_custom_button(__("Hinterlege Lieferant"), function() {
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
        part_list_items_check(frm);
        check_navision(frm);
        calculate_part_list_prices(frm);
        validate_customer(frm, "validate");
        check_deactivated_items(frm);
        //Check Tasks for Service Projects
        check_service_project_tasks(frm);
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
        
        if (cur_frm.doc.part_list_items) {
            for (i=0; i < cur_frm.doc.part_list_items.length; i++) {
                if (cur_frm.doc.part_list_items[i].qty && cur_frm.doc.part_list_items[i].rate) {
                    frappe.model.set_value(cur_frm.doc.part_list_items[i].doctype, cur_frm.doc.part_list_items[i].name, "amount", cur_frm.doc.part_list_items[i].qty * cur_frm.doc.part_list_items[i].rate);
                } else {
                    frappe.model.set_value(cur_frm.doc.part_list_items[i].doctype, cur_frm.doc.part_list_items[i].name, "amount", 0);
                }
            }
        }
        
        if (frm.doc.project_clone && !frm.doc.project_manager_name) {
            set_project_manager(frm.doc.project_clone)
        }
        
        if (cur_frm.doc.__islocal) {
            //check if default warehouse ist set in all items, otherwise give information.
            check_default_warehouses(frm);
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
        if (frm.doc.contact_person_two) {
            contact_info_display(frm, cur_frm.doc.contact_person_two, "contact_display_two")
        } else {
            cur_frm.set_value("contact_display_two", null);
            cur_frm.set_value("contact_salutation", null);
            cur_frm.set_value("contact_last_name", null);
            cur_frm.set_value("contact_email_two", null);
        }
    },
    shipping_contact: function(frm) {
        if (frm.doc.contact_person_two) {
            contact_info_display(frm, cur_frm.doc.shipping_contact, "shipping_contact_display") 
        } else {
            cur_frm.set_value("shipping_contact_display", null);
        }
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
        //~ deliver_int_positions(frm);
        check_for_charged_at_cost(frm);
        cur_frm.set_value("original_total", cur_frm.doc.total);
    },
    before_save(frm) {
        get_customer_sales_order_note(frm);
        if (cur_frm.doc.__islocal && !frm.doc.source) {
            set_lead_source(frm.doc.customer);
        }
    },
    billing_address_name: function(frm) {
        if (frm.doc.billing_address_name) {
            frappe.call({
                method: 'frappe.contacts.doctype.address.address.get_address_display',
                args: {
                    address_dict: frm.doc.billing_address_name
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('billing_address', r.message);
                    }
                }
            });
        } else {
            frm.set_value('billing_address', null);
        }
    },
    billing_contact: function(frm) {
        if (frm.doc.billing_contact) {
            frappe.call({
                method: 'frappe.contacts.doctype.contact.contact.get_contact_details',
                args: {
                    contact: frm.doc.billing_contact
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('billing_contact_display', r.message.contact_display);
                    }
                }
            });
        } else {
            frm.set_value('billing_contact_display', null);
        }
    },
    project_clone: function(frm) {
        set_project_manager(frm.doc.project_clone);
        //Check if Project is a Service Project
        check_service_project(frm);
        
        //Filter Tasks for Service Projects
        cur_frm.fields_dict.items.grid.get_field('task').get_query = function(doc) {                                                                      
                return {
                    filters: {'project': frm.doc.project}
                }
        }
    },
    is_service_project: function(frm) {
        //Mark Sales Order Items
        set_service_project(frm);
    }
});

frappe.ui.form.on('Sales Order Item', {
    with_bom(frm, cdt, cdn) {
        set_row_options(frm);
    },
    item_code(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            check_charging_points_item(row.item_code);
            check_for_family(row.item_code, row.qty);
            fetch_stock_items(row.item_code, cdt, cdn);
            check_deactivation(row.item_code);
            frappe.db.get_value("Item", row.item_code, "part_list_item").then( (value) => {
               if (value.message.part_list_item == 1) {
                    frappe.model.set_value(cdt, cdn, 'with_bom', 1);
                } else {
                    frappe.model.set_value(cdt, cdn, 'with_bom', 0);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'with_bom', 0);
        }
    },
    before_items_remove(frm, cdt, cdn) {
        var row = locals[cdt][cdn]
        locals.deleted_row = row.idx
        for (var i = frm.doc.part_list_items.length - 1; i >= 0; i--) {
            if (frm.doc.part_list_items[i].belongs_to == locals.deleted_row) {
                var bom_row = frm.doc.part_list_items[i];
                frm.doc.part_list_items.splice(i, 1);
            }
        }
    },
    delivered_by_supplier(frm, cdt, cdn) {
        var row = frappe.get_doc(cdt, cdn);
        if (row.delivered_by_supplier == 0) {
            frappe.model.set_value(cdt, cdn, "delivered_qty", 0);
        }
    },
    items_remove(frm, cdt, cdn) {
        if (frm.doc.part_list_items) {
            set_row_options(frm);
            set_new_rows(frm);
        }
    },
    close_position(frm, cdt, cdn) {
        close_so_position(frm, cdt, cdn);
    },
    overbill_item(frm, cdt, cdn) {
        create_overbilling_invoice(frm, cdt, cdn);
    },
    deliver_position(frm, cdt, cdn) {
        deliver_so_position(frm, cdt, cdn);
    },
    items_add(frm, cdt, cdn) {
        if (frm.doc.is_service_project) {
            frappe.model.set_value(cdt, cdn, "is_service_project_item", 1);
        }
    }
});

frappe.ui.form.on('Sales Order Part List Item', {
    item_code(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            check_deactivation(row.item_code);
        }
    },
    qty(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        } else {
            frappe.model.set_value(cdt, cdn, "amount", 0);
        }
    },
    rate(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        } else {
            frappe.model.set_value(cdt, cdn, "amount", 0);
        }
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
            if (field == "contact_display_two") {
                cur_frm.set_value("contact_salutation", res[0].salutation);
                cur_frm.set_value("contact_last_name", res[0].first_name);
                cur_frm.set_value("contact_email_two", res[0].email_id);
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

frappe.ui.form.on("Sales Order Item", "with_bom", function(frm, cdt, cdn) {
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
                frappe.msgprint( __("Kunde ist gesperrt!<br><br>Lobas-Anfragen von Hymes-Sperrkunden weiterleiten an info@hymes.de. Nicht Lobas-bezogene Anfragen/Aufträge (z.B. EZA-Regler) können angenommen und verarbeitet werden."), __("Sperrkunde") );
                if (event == "customer") {
                    cur_frm.set_value("customer", "");
                } else {
                    frappe.validated=false;
                }
            }
        }
    });
}

function check_for_part_list_items(frm) {
    if (frm.doc.items[0].prevdoc_docname && frm.doc.part_list_items.length < 1) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Quotation",
                'name': frm.doc.items[0].prevdoc_docname
            },
            'callback': function(response) {
                var items = response.message.part_list_items;
                if (items) {
                    for (let i = 0; i < items.length; i++) {
                        var child = cur_frm.add_child('part_list_items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', items[i].item_code);
                        frappe.model.set_value(child.doctype, child.name, 'qty', items[i].qty);
                        frappe.model.set_value(child.doctype, child.name, 'belongs_to', items[i].belongs_to);
                        frappe.model.set_value(child.doctype, child.name, 'description', items[i].description);
                        setTimeout(function(child, rate) {
                            frappe.model.set_value(child.doctype, child.name, 'item_name', items[i].item_name);
                            frappe.model.set_value(child.doctype, child.name, 'rate', rate);
                            frappe.model.set_value(child.doctype, child.name, 'description', items[i].description);
                            frm.refresh_field('part_list_items');
                        }, 5000, child, items[i].rate);
                    }
                }
            }
        });
    }
}

function set_row_options(frm) {
    if (frm.doc.part_list_items) {
        var options = [];
        for (i=0; i < frm.doc.items.length; i++) {
            if (frm.doc.items[i].with_bom) {
                options.push(frm.doc.items[i].idx);
            }
        }
        var options_string = options.join("\n");
        cur_frm.get_field("part_list_items").grid.docfields[4].options = options_string;
        cur_frm.refresh_field("part_list_items");
    }
}

function calculate_part_list_prices(frm) {
    for (i=0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].with_bom && !frm.doc.items[i].alternative_position) {
            var amount = 0
            for (j=0; j < frm.doc.part_list_items.length; j++) {
                if (frm.doc.part_list_items[j].belongs_to == i + 1) {
                    amount += frm.doc.part_list_items[j].amount
                }
            }
            frappe.model.set_value(frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "rate", amount);
        }
    }
}

function check_for_family(item_code, quantity) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Item",
            'name': item_code
        },
        'callback': function(response) {
            if (response.message.item_family == 1 && !locals.item_family) {
                locals.item_family=true;
                frappe.confirm('Dieser Artikel gehört zu einer Artikelfamilie, möchten Sie die Geschwister ebenfalls einfügen?', function() {
                    if (!quantity) {
                        quantity = 1
                    }
                    for (var i=0; i < response.message.family_items.length; i++) {
                        var child = cur_frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', response.message.family_items[i].item_code);
                        frappe.model.set_value(child.doctype, child.name, 'qty', response.message.family_items[i].qty * quantity);
                        cur_frm.refresh_field("items");
                    }
                });
            }
        }
    });
    setTimeout(function(){
        locals.item_family=false;
    }, 3000);
}

function get_customer_sales_order_note(frm) {
    frappe.call({
        'method': "frappe.client.get_list",
        'args':{
     	    'doctype': "Customer",
         	'filters': [
         	    ["name","IN", [cur_frm.doc.customer]]
         	],
            'fields': ["leave_sales_order_note", "sales_order_note_box"]
        },
        'callback': function (r) {
            var customer = r.message[0];
            
            if (customer.leave_sales_order_note === 1) {
                frappe.msgprint({
                    title: __('Dieser Kunde hat einen Auftragsvermerk hinterlassen:'),
                    indicator: 'red',
                    message: __(` &nbsp;  &nbsp; ${ customer.sales_order_note_box }`)
                });
            }
        }
    });
}

function deliver_int_positions(frm) {
    for (i=0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].interne_position == 1) {
            frappe.model.set_value(cur_frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "delivered_qty", cur_frm.doc.items[i].qty);
        }
    }
}

function part_list_items_check(frm) {
    for (i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].with_bom && !frm.doc.part_list_items) {
            frappe.msgprint("Dokument enthält keine Stücklistenartikel, obwohl mind. 1 Artikel eine Stückliste benötigt.", "Fehlende Stücklistenartikel");
        }
    }
}

function check_for_charged_at_cost(frm) {
    let charged_at_cost = false
    for (let i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].artikel_nach_aufwand) {
            charged_at_cost = true
            break;
        }
    }
    if (charged_at_cost) {
        for (let i = 0; i < frm.doc.items.length; i++) {
            frappe.model.set_value(cur_frm.doc.items[i].doctype, cur_frm.doc.items[i].name, "enthaelt_artikel_nach_aufwand", 1);
        }
    }
}

function set_lead_source(customer) {
    if (customer) {
        frappe.call({
            'method': 'energielenker.energielenker.sales_order.sales_order.get_lead_source',
            'args': {
                'customer': customer
            },
            'callback': function(response) {
                if (response.message) {
                    cur_frm.set_value('source', response.message);
                } else {
                    cur_frm.set_value('source', null);
                }
            }
        });
    } else {
        cur_frm.set_value('source', null);
    }
}

function set_new_rows(frm) {
    for (var i = 0; i < frm.doc.part_list_items.length; i++) {
        if (frm.doc.part_list_items[i].belongs_to >= locals.deleted_row) {
            frm.doc.part_list_items[i].belongs_to = frm.doc.part_list_items[i].belongs_to -1
        }
    }
    cur_frm.refresh_field('part_list_item');
}

function close_so_position(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let trans_item = [{'docname': cdn, 'item_code': row.item_code, 'qty': row.delivered_qty, 'rate': row.rate, 'idx': row.idx}];
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.close_so_position',
        'args': {
            'parent_doctype': "Sales Order",
            'trans_items': trans_item,
            'parent_doctype_name': frm.doc.name
        },
        'callback': function(response) {
            frappe.show_alert('Artikel wurde aktualisiert', 5);
            cur_frm.reload_doc();
        }
    });
}

function display_closed_positions(frm) {
    let display = false
    let delivered_display = false
    let closed_items = ""
    let delivered_items = ""
    for (let i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].closed_position) {
            closed_items += "Artikel " + frm.doc.items[i].item_code + " (Zeile " + frm.doc.items[i].idx + ")<br>"
            display = true
        }
        if (frm.doc.items[i].delivered_position) {
            delivered_items += "Artikel " + frm.doc.items[i].item_code + " (Zeile " + frm.doc.items[i].idx + ")<br>"
            delivered_display = true
        }
    }
    if (display) {
        cur_frm.dashboard.add_comment( "Folgende Positionen wurden manuell geschlossen: <br>" + closed_items, 'red', true);
    }
    
    if (delivered_display) {
        let line_break = ""
        if (display) {
            line_break = "<br>"
        }
        cur_frm.dashboard.add_comment(line_break + "Folgende Positionen wurden durch Steckengeschäft mitgeliefert: <br>" + delivered_items, 'red', true);
    }
}

function remove_billing_address(frm) {
    cur_frm.set_value("billing_address_name", null);
    cur_frm.set_value("billing_address", null);
    cur_frm.set_value("billing_contact", null);
    cur_frm.set_value("billing_contact_display", null);
}

function check_default_warehouses(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.check_default_warehouses',
        'args': {
            'doc': frm.doc
        },
        'callback': function(response) {
            if (response.message) {
				frappe.msgprint({
					message: response.message,
					indicator: 'orange',
					title: __('Default Warehouse')
				});
            }
        }
    });
}

function create_overbilling_invoice(frm, cdt, cdn) {
    frappe.call({
        'method': 'energielenker.energielenker.sales_order.sales_order.create_overbilling_invoice',
        'args': {
            'doc': frm.doc,
            'cdt': cdt,
            'cdn': cdn
        },
        'callback': function(response) {
            if (response.message) {
                window.open(response.message, '_blank');
            }
        }
    });
}

function deliver_so_position(frm, cdt, cdn) {
    frappe.confirm(
        'Die offene Liefermenge wird als "geliefert durch Streckengeschäft" markiert. Sind Sie sicher?',
        function(){
            let row = frappe.get_doc(cdt, cdn);
            frappe.model.set_value(cdt, cdn, "delivered_by_drop_ship", row.qty - row.delivered_qty);
            frappe.model.set_value(cdt, cdn, "total_delivered_qty", row.qty);
            frappe.model.set_value(cdt, cdn, "delivered_position", 1);
            window.close();
            frm.save("Update");
            frappe.show_alert('Artikel wurde aktualisiert', 5);
        },
        function(){
            // on no, do nothing
        }
    )
}

function remove_delivered_and_closed(frm) {
    let remove_comment = false
    //Remove Checks
    if (frm.doc.items && frm.doc.items.length > 0) {
        for (let i = 0; i < frm.doc.items.length; i++) {
            if (frm.doc.items[i].closed_position || frm.doc.items[i].delivered_position) {
                frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "closed_position", 0);
                frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "delivered_position", 0);
                frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "delivered_by_drop_ship", 0);
                frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "total_delivered_qty", 0);
                remove_comment = true
            }
        }
    }
    //Remove Comment
    if (remove_comment) {
        cur_frm.dashboard.clear_comment();
    }
}

function set_service_project(frm) {
    for (let i = 0; i < frm.doc.items.length; i++) {
        frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "is_service_project_item", frm.doc.is_service_project);
    }
}

function check_service_project(frm) {
    if (frm.doc.project_clone) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Project",
                'name': frm.doc.project_clone
            },
            'callback': function(response) {
                cur_frm.set_value("is_service_project", response.message.is_service_project);
            }
        });
    } else {
        cur_frm.set_value("is_service_project", 0);
    }
}

function check_service_project_tasks(frm) {
    if (frm.doc.is_service_project) {
        frappe.call({
            'method': 'energielenker.energielenker.sales_order.sales_order.check_service_project_tasks',
            'args': {
                'doc': frm.doc
            },
            'callback': function(response) {
                if (response.message) {
                    frappe.msgprint(response.message, "Aufgabe falsch!")
                    frappe.validated=false;
                }
            }
        });
    }
}
