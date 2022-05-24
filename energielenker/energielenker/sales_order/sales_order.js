// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
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
        if (cur_frm.doc.customer) {
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
        shipping_address_query(frm);
    },
    validate: function(frm) {
        check_navision(frm);
        if (cur_frm.doc.project_clone) {
            cur_frm.set_value('project', cur_frm.doc.project_clone);
        } else {
            cur_frm.set_value('project_clone', cur_frm.doc.project);
        }
        check_vielfaches(frm);
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
                    if (betrag >= 99.99999) {
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
    }
});

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
